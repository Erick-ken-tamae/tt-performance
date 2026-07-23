from flask import Flask, render_template, request, redirect
from models.jogador import cadastrar_jogador, listar_jogador, excluir_jogador
from models.partida import  cadastrar_partida, listar_partida

app = Flask(__name__)

#inicio
@app.route("/")
def inicio():

    jogadores = listar_jogador()

    return render_template(
        "cadastro_jogador.html",
        jogadores=jogadores
    )

#PÁGINA DE CADASTRAR jogador
@app.route("/cadastrar", methods=["POST"])
def cadastrar():

    print(request.form)

    nome = request.form["nome"]
    idade = request.form["idade"]
    categoria = request.form["categoria"]
    clube = request.form["clube"]

    cadastrar_jogador(nome, idade, categoria, clube)

    return redirect("/partida")

    
#PÁGINA DA PARTIDA
@app.route("/partida")
def partida():
    jogadores = listar_jogador()
    partidas = listar_partida()
    
    return render_template(
        "partida.html",
        jogadores=jogadores,
        partidas=partidas
    )
    
#salvar partida
@app.route("/salvar_partida", methods=["POST"])
def salvar_partida():

    jogador_id = request.form["jogador_id"]

    adversario = request.form["adversario"]

    data_partida = request.form["data_partida"]

    cadastrar_partida(
        jogador_id,
        adversario,
        data_partida
    )

    return redirect("/partida")
#Excluir partida
@app.route("/excluir_jogador/<int:id>")
def excluir(id):
    excluir_jogador(id)
    return redirect("/")

#iniciar partida
@app.route("/iniciar_partida")
def iniciar_partida():
    return render_template("iniciar_partida.html")


if __name__ == "__main__":
    app.run(debug=True)