from flask import Flask
from database import conectar


app = Flask(__name__)

@app.route("/")
def inicio():
    banco = conectar()
    
    return "Banco Conectado com sucesso!"

if __name__ == "__main__":
    app.run(debug=True)