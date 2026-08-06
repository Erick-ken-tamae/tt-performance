from database import conectar
from werkzeug.security import generate_password_hash, check_password_hash


def criar_usuario(nome, email, senha, tipo="Jogador"):
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


def listar_usuarios():
    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, nome, email, tipo, data_cadastro FROM usuario ORDER BY data_cadastro DESC"
    )
    usuarios = cursor.fetchall()

    cursor.close()
    banco.close()
    return usuarios


def contar_usuarios():
    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("SELECT COUNT(*) FROM usuario")
    total = cursor.fetchone()[0]

    cursor.close()
    banco.close()
    return total


def buscar_usuario_por_id(usuario_id):
    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuario WHERE id = %s", (usuario_id,))
    usuario = cursor.fetchone()

    cursor.close()
    banco.close()
    return usuario


def excluir_usuario(usuario_id):
    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("DELETE FROM usuario WHERE id = %s", (usuario_id,))

    banco.commit()
    cursor.close()
    banco.close()