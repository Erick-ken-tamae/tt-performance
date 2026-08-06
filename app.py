import os
from functools import wraps
from flask import Flask, render_template, request, redirect, jsonify, flash, session, url_for
from models.partida import cadastrar_partida, listar_partida, buscar_partida, finalizar_partida, excluir_partida, salvar_jogada, estatistica_partida, listar_sets, salvar_set
from models.jogada import listar_jogadas
from models.usuario import criar_usuario, validar_login, email_existe, listar_usuarios, contar_usuarios, excluir_usuario, buscar_usuario_por_id

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


def admin_required(f):
    """Decorator para proteger rotas que exigem administrador."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        if session.get("usuario_tipo") != "Administrador":
            flash("Acesso restrito a administradores.", "error")
            return redirect(url_for("inicio"))
        return f(*args, **kwargs)
    return decorated_function


def eh_dono_da_partida(partida):
    """Verifica se a partida pertence ao usuário logado (admins têm acesso a tudo)."""
    if partida is None:
        return False
    if session.get("usuario_tipo") == "Administrador":
        return True
    return partida.get("usuario_id") == session.get("usuario_id")


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
            session["usuario_tipo"] = usuario["tipo"]
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("inicio"))
        else:
            flash("Email ou senha incorretos.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar_senha = request.form.get("confirmar_senha")
        tipo = request.form.get("tipo", "Jogador")

        if senha != confirmar_senha:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for("cadastro"))

        if email_existe(email):
            flash("Este email já está cadastrado.", "error")
            return redirect(url_for("cadastro"))

        criar_usuario(nome, email, senha, tipo)
        flash("Conta criada com sucesso! Faça login.", "success")
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

    partidas = listar_partida(session["usuario_id"])

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
        session["usuario_id"],
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

    if not eh_dono_da_partida(partida):
        flash("Você não tem acesso a essa partida.", "error")
        return redirect("/")

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

    partida = buscar_partida(dados["partida_id"])
    if not eh_dono_da_partida(partida):
        return jsonify({"erro": "Acesso negado"}), 403

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

    partida = buscar_partida(id)

    if not eh_dono_da_partida(partida):
        flash("Você não tem acesso a essa partida.", "error")
        return redirect("/")

    excluir_partida(id)

    flash("Partida excluída com sucesso!", "success")

    return redirect("/")


# Histórico de partida
@app.route("/historico/<int:id>")
@login_required
def historico(id):

    partida = buscar_partida(id)

    if not eh_dono_da_partida(partida):
        flash("Você não tem acesso a essa partida.", "error")
        return redirect("/")

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

    partida = buscar_partida(dados["partida_id"])
    if not eh_dono_da_partida(partida):
        return jsonify({"erro": "Acesso negado"}), 403

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

    partida = buscar_partida(dados["partida_id"])
    if not eh_dono_da_partida(partida):
        return jsonify({"erro": "Acesso negado"}), 403

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

    if not eh_dono_da_partida(partida):
        flash("Você não tem acesso a essa partida.", "error")
        return redirect("/")

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


# ---------------- ADMINISTRAÇÃO ----------------

@app.route("/admin")
@admin_required
def admin():
    usuarios = listar_usuarios()
    total_usuarios = contar_usuarios()

    return render_template(
        "admin.html",
        usuarios=usuarios,
        total_usuarios=total_usuarios
    )


@app.route("/admin/excluir_usuario/<int:id>")
@admin_required
def admin_excluir_usuario(id):

    if id == session.get("usuario_id"):
        flash("Você não pode excluir sua própria conta.", "error")
        return redirect(url_for("admin"))

    usuario = buscar_usuario_por_id(id)
    if not usuario:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("admin"))

    excluir_usuario(id)
    flash("Usuário excluído com sucesso!", "success")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )