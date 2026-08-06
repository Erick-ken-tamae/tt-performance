import os
from functools import wraps
from flask import Flask, render_template, request, redirect, jsonify, flash, session, url_for
from models.partida import cadastrar_partida, listar_partida, buscar_partida, finalizar_partida, excluir_partida, salvar_jogada, estatistica_partida, listar_sets, salvar_set
from models.jogada import listar_jogadas
from models.usuario import criar_usuario, validar_login, email_existe

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tt_performance_secret_key")


def login_required(f):
    """Decorator para proteger rotas que exigem login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------- LOGIN / CADASTRO / LOGOUT ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = validar_login(email, senha)

        if usuario:
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            return redirect(url_for("inicio"))
        else:
            flash("Email ou senha incorretos.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar_senha = request.form.get("confirmar_senha")

        if senha != confirmar_senha:
            flash("As senhas não coincidem.")
            return redirect(url_for("cadastro"))

        if email_existe(email):
            flash("Este email já está cadastrado.")
            return redirect(url_for("cadastro"))

        criar_usuario(nome, email, senha)
        flash("Conta criada com sucesso! Faça login.")
        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- ROTAS DO SISTEMA (protegidas) ----------------

# Página inicial
@app.route("/")
@login_required
def inicio():

    partidas = listar_partida()

    return render_template(
        "partida.html",
        partidas=partidas
    )


# Salvar partida
@app.route("/salvar_partida", methods=["POST"])
@login_required
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
@login_required
def iniciar_partida(id):

    partida = buscar_partida(id)

    if partida["status"] == "FINALIZADA":
        return redirect(f"/historico/{id}")

    return render_template(
        "iniciar_partida.html",
        partida=partida
    )


@app.route("/finalizar_partida", methods=["POST"])
@login_required
def finalizar():

    dados = request.get_json()

    finalizar_partida(
        dados["partida_id"],
        dados["vencedor"],
        dados["sets_jogador"],
        dados["sets_adversario"]
    )

    return jsonify({"mensagem": "Partida finalizada"})


# excluir partida
@app.route("/excluir_partida/<int:id>")
@login_required
def excluir(id):

    excluir_partida(id)

    flash("Partida excluída com sucesso!")

    return redirect("/")


# Histórico de partida
@app.route("/historico/<int:id>")
@login_required
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
@login_required
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

    return jsonify({"status": "ok"})


@app.route("/salvar_set", methods=["POST"])
@login_required
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
        "status": "ok"
    })


@app.route("/analise/<int:id>")
@login_required
def analise(id):
    partida = buscar_partida(id)
    estatistica = estatistica_partida(id)
    sets = listar_sets(id)
    jogadas = listar_jogadas(id)

    estatistica_jogador = [
        item for item in estatistica if item["jogador"] == partida["nome_jogador"]
    ]
    estatistica_adversario = [
        item for item in estatistica if item["jogador"] == partida["nome_adversario"]
    ]

    def calcular_resumo(lista):
        total_acertos = sum(item["acertos"] for item in lista)
        total_erros = sum(item["erros"] for item in lista)
        total_jogadas = total_acertos + total_erros

        if total_jogadas > 0:
            aproveitamento = round((total_acertos / total_jogadas) * 100, 2)
        else:
            aproveitamento = 0

        if lista:
            melhor = max(lista, key=lambda item: item["aproveitamento"])["tecnica"]
            pior = min(lista, key=lambda item: item["aproveitamento"])["tecnica"]
            mais_utilizada = max(
                lista, key=lambda item: item["acertos"] + item["erros"]
            )["tecnica"]
        else:
            melhor = "-"
            pior = "-"
            mais_utilizada = "-"

        return {
            "total_acertos": total_acertos,
            "total_erros": total_erros,
            "aproveitamento": aproveitamento,
            "melhor_tecnica": melhor,
            "pior_tecnica": pior,
            "tecnica_mais_utilizada": mais_utilizada
        }

    resumo_jogador = calcular_resumo(estatistica_jogador)
    resumo_adversario = calcular_resumo(estatistica_adversario)

    return render_template(
        'analise.html',
        partida=partida,
        sets=sets,
        jogadas=jogadas,
        estatistica_jogador=estatistica_jogador,
        estatistica_adversario=estatistica_adversario,
        resumo_jogador=resumo_jogador,
        resumo_adversario=resumo_adversario
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )