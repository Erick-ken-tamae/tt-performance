from datetime import datetime

from bson.objectid import ObjectId

from database import conectar


def _partidas():
    return conectar()["partidas"]


def _formatar(partida):
    """Adiciona um campo 'id' em texto (string) equivalente ao _id do Mongo."""
    if partida:
        partida["id"] = str(partida["_id"])
    return partida


def cadastrar_partida(usuario_id,
                       nome_jogador,
                       clube_jogador,
                       nome_adversario,
                       clube_adversario,
                       data_partida,
                       quantidade_sets):

    # O formulário HTML manda a data como texto (ex: "2026-09-05").
    # O MySQL convertia isso pra data automaticamente; no Mongo precisamos
    # converter na mão pra manter partida.data_partida.strftime(...) funcionando
    # nos templates (historico.html, analise.html).
    data_partida_convertida = datetime.strptime(data_partida, "%Y-%m-%d")

    _partidas().insert_one({
        "usuario_id": usuario_id,
        "nome_jogador": nome_jogador,
        "clube_jogador": clube_jogador,
        "nome_adversario": nome_adversario,
        "clube_adversario": clube_adversario,
        "quantidade_sets": quantidade_sets,
        "sets_jogador": 0,
        "sets_adversario": 0,
        "vencedor": None,
        "status": "EM_ANDAMENTO",
        "data_partida": data_partida_convertida,
        "sets": [],
        "jogadas": []
    })


def listar_partida(usuario_id):
    """Lista só as partidas EM ANDAMENTO do usuário (pra tela principal)."""
    partidas = list(_partidas().find({
        "usuario_id": usuario_id,
        "status": {"$ne": "FINALIZADA"}
    }).sort("_id", 1))
    return [_formatar(p) for p in partidas]


def buscar_partida(id):
    partida = _partidas().find_one({"_id": ObjectId(id)})
    return _formatar(partida)


def listar_historico_usuario(usuario_id):
    """Lista as partidas FINALIZADAS do usuário, mais recentes primeiro (pra tela de histórico)."""
    partidas = list(_partidas().find({
        "usuario_id": usuario_id,
        "status": "FINALIZADA"
    }).sort("data_partida", -1))
    return [_formatar(p) for p in partidas]


def finalizar_partida(id, vencedor, sets_jogador, sets_adversario):
    _partidas().update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "vencedor": vencedor,
            "sets_jogador": sets_jogador,
            "sets_adversario": sets_adversario,
            "status": "FINALIZADA"
        }}
    )


def excluir_partida(id):
    # Antes eram 2 DELETEs (jogada + partida); agora as jogadas já estão
    # dentro do próprio documento da partida, então um só remove tudo.
    _partidas().delete_one({"_id": ObjectId(id)})


def salvar_jogada(partida_id, set_numero, jogador, vencedor_ponto, tecnica, resultado):
    _partidas().update_one(
        {"_id": ObjectId(partida_id)},
        {"$push": {
            "jogadas": {
                "numero_set": set_numero,
                "jogador": jogador,
                "vencedor_ponto": vencedor_ponto,
                "tecnica": tecnica,
                "resultado": resultado,
                "data_registro": datetime.utcnow()
            }
        }}
    )


def listar_sets(partida_id):
    partida = _partidas().find_one({"_id": ObjectId(partida_id)}, {"sets": 1})
    sets = partida.get("sets", []) if partida else []
    return sorted(sets, key=lambda s: s["numero_set"])


def salvar_set(partida_id, numero_set, pontos_jogador, pontos_adversario, vencedor):
    _partidas().update_one(
        {"_id": ObjectId(partida_id)},
        {"$push": {
            "sets": {
                "numero_set": numero_set,
                "pontos_jogador": pontos_jogador,
                "pontos_adversario": pontos_adversario,
                "vencedor": vencedor
            }
        }}
    )


def estatistica_partida(id):
    partida = _partidas().find_one({"_id": ObjectId(id)}, {"jogadas": 1})
    jogadas = partida.get("jogadas", []) if partida else []

    # Agrupa por (jogador, tecnica), reproduzindo o GROUP BY do SQL original.
    resumo = {}
    for jogada in jogadas:
        chave = (jogada["jogador"], jogada["tecnica"])
        grupo = resumo.setdefault(chave, {"acertos": 0, "erros": 0})

        if jogada["resultado"] == "Acerto":
            grupo["acertos"] += 1
        elif jogada["resultado"] == "Erro":
            grupo["erros"] += 1

    estatisticas = []
    for (jogador, tecnica), valores in resumo.items():
        total = valores["acertos"] + valores["erros"]
        aproveitamento = round((valores["acertos"] / total) * 100, 2) if total else 0

        estatisticas.append({
            "jogador": jogador,
            "tecnica": tecnica,
            "acertos": valores["acertos"],
            "erros": valores["erros"],
            "aproveitamento": aproveitamento
        })

    return estatisticas