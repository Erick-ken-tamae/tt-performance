from bson.objectid import ObjectId

from database import conectar


def listar_jogadas(id):
    partida = conectar()["partidas"].find_one({"_id": ObjectId(id)}, {"jogadas": 1})
    jogadas = partida.get("jogadas", []) if partida else []

    return sorted(
        jogadas,
        key=lambda j: (j["numero_set"], j.get("data_registro"))
    )