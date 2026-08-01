from flask import Flask, render_template, request, redirect, jsonify
from models.partida import cadastrar_partida, listar_partida, buscar_partida, finalizar_partida, excluir_partida, salvar_jogada, estatistica_partida, listar_sets, salvar_set
from models.jogada import listar_jogadas
app = Flask(__name__)

# Página inicial
@app.route("/")
def inicio():

    partidas = listar_partida()

    return render_template(
        "partida.html",
        partidas=partidas
    )


# Salvar partida
@app.route("/salvar_partida", methods=["POST"])
def salvar_partida():

    
    nome = request.form["nome"]
    clube = request.form["clube"]
    adversario = request.form["adversario"]
    clube_adversario = request.form["clube_adversario"]
    data_partida = request.form["data_partida"]
    quantidade_sets = request.form["melhor_de"]

    cadastrar_partida(
        nome,
        clube,
        adversario,
        clube_adversario,
        data_partida,
        quantidade_sets
    )

    return redirect("/")
# Iniciar partida
@app.route("/iniciar_partida/<int:id>")
def iniciar_partida(id):

    partida = buscar_partida(id)

    if partida["status"] == "FINALIZADA":
        return redirect(f"/historico/{id}")

    return render_template(
        "iniciar_partida.html",
        partida=partida
    )

@app.route("/finalizar_partida", methods=["POST"])
def finalizar():

    dados = request.get_json()

    finalizar_partida(
        dados["partida_id"],
        dados["vencedor"],
        dados["sets_jogador"],
        dados["sets_adversario"]
    )

    return jsonify({"mensagem":"Partida finalizada"})

#excluir partida
@app.route("/excluir_partida/<int:id>")
def excluir(id):

    excluir_partida(id)

    return redirect("/")


#Histórico de partida
@app.route("/historico/<int:id>")
def historico(id):

    partida = buscar_partida(id)

    sets = listar_sets(id)

    print("SETS:", sets)
    return render_template(
        "historico.html",
        partida=partida,
        sets=sets
    )

@app.route("/salvar_jogada", methods=["POST"])
def salvar_jogada_api():

    dados = request.get_json()

    salvar_jogada(
        dados["partida_id"],
        dados["set_numero"],
        dados["jogador"],
        dados["vencedor_ponto"],
        dados["tecnica"],
        dados["resultado"]
    )

    return jsonify({"status":"ok"})


@app.route("/salvar_set", methods=["POST"])
def salvar_set_api():

    dados = request.get_json()

    print("DADOS RECEBIDOS:", dados)

    salvar_set(
        dados["partida_id"],
        dados["numero_set"],
        dados["pontos_jogador"],
        dados["pontos_adversario"],
        dados["vencedor"]
    )


    return jsonify({
        "status":"ok"
    })

@app.route("/analise/<int:id>")
def analise(id):
    partida =buscar_partida(id)
    estatistica = estatistica_partida(id)
    sets=listar_sets(id)
    jogadas = listar_jogadas(id)
    
    return render_template(
        'analise.html',
        partida=partida,
        estatistica=estatistica,
        sets = sets,
        jogadas = jogadas
        )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )