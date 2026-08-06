from database import conectar
from werkzeug.security import generate_password_hash, check_password_hash


def criar_usuario(nome, email, senha, tipo="Treinador"):
    banco = conectar()
    cursor = banco.cursor()

    senha_hash = generate_password_hash(senha)

    cursor.execute(
        "INSERT INTO usuario (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)",
        (nome, email, senha_hash, tipo)
    )

    banco.commit()
    cursor.close()
    banco.close()


def buscar_usuario_por_email(email):
    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuario WHERE email = %s", (email,))
    usuario = cursor.fetchone()

    cursor.close()
    banco.close()
    return usuario


def validar_login(email, senha_digitada):
    usuario = buscar_usuario_por_email(email)

    if usuario and check_password_hash(usuario["senha"], senha_digitada):
        return usuario

    return None


def email_existe(email):
    return buscar_usuario_por_email(email) is not None