from datetime import datetime

from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

from database import conectar


def _usuarios():
    return conectar()["usuarios"]


def criar_usuario(nome, email, senha, tipo="Jogador"):
    senha_hash = generate_password_hash(senha)

    _usuarios().insert_one({
        "nome": nome,
        "email": email,
        "senha": senha_hash,
        "tipo": tipo,
        "data_cadastro": datetime.utcnow()
    })


def buscar_usuario_por_email(email):
    usuario = _usuarios().find_one({"email": email})

    if usuario:
        usuario["id"] = str(usuario["_id"])

    return usuario


def validar_login(email, senha_digitada):
    usuario = buscar_usuario_por_email(email)

    if usuario and check_password_hash(usuario["senha"], senha_digitada):
        return usuario

    return None


def email_existe(email):
    return buscar_usuario_por_email(email) is not None


def listar_usuarios():
    usuarios = list(
        _usuarios()
        .find({}, {"nome": 1, "email": 1, "tipo": 1, "data_cadastro": 1})
        .sort("data_cadastro", -1)
    )

    for usuario in usuarios:
        usuario["id"] = str(usuario["_id"])

    return usuarios


def contar_usuarios():
    return _usuarios().count_documents({})


def buscar_usuario_por_id(usuario_id):
    usuario = _usuarios().find_one({"_id": ObjectId(usuario_id)})

    if usuario:
        usuario["id"] = str(usuario["_id"])

    return usuario


def excluir_usuario(usuario_id):
    _usuarios().delete_one({"_id": ObjectId(usuario_id)})


def alterar_tipo_usuario(usuario_id, novo_tipo):
    """
    Altera o tipo do usuário (Administrador ou Jogador).

    Retorna True se o usuário foi encontrado, False se não existe.
    """
    resultado = _usuarios().update_one(
        {"_id": ObjectId(usuario_id)},
        {"$set": {"tipo": novo_tipo}}
    )

    return resultado.matched_count > 0