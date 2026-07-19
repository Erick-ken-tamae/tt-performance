from flask import Flask, render_template, request, redirect
from models.jogador import cadastrar_jogador, listar_jogador


app = Flask(__name__)

@app.route("/")
def inicio():

    jogadores = listar_jogador()

    return render_template(
        "cadastro_jogador.html",
        jogadores=jogadores
    )


@app.route("/cadastrar", methods=["POST"])
def cadastrar():

    print(request.form)

    nome = request.form["nome"]
    idade = request.form["idade"]
    categoria = request.form["categoria"]
    clube = request.form["clube"]

    cadastrar_jogador(nome, idade, categoria, clube)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
