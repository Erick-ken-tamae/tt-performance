from flask import Flask, render_template, request, redirect
from models.partida import cadastrar_partida, listar_partida, buscar_partida, listar_historico

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
    data_partida = request.form["data_partida"]
    quantidade_sets = request.form["melhor_de"]

    cadastrar_partida(
        nome,
        clube,
        adversario,
        data_partida,
         quantidade_sets
    )

    return redirect("/")
# Iniciar partida
@app.route("/iniciar_partida/<int:id>")
def iniciar_partida(id):

    partida = buscar_partida(id)

    return render_template(
        "iniciar_partida.html",
        partida=partida
    )

#Histórico de partida
@app.route("/historico")
def historico():
    partidas = listar_historico()

    return render_template(
        "historico.html",
        partidas=partidas
    )

if __name__ == "__main__":
    app.run(debug=True)