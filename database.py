import os
from pymongo import MongoClient

# Reaproveita a mesma conexão entre chamadas (recomendado pelo MongoDB
# para ambientes serverless como a Vercel, ao contrário do MySQL onde
# abríamos/fechávamos a conexão a cada função).
_client = None


def conectar():
    """Retorna o banco (database) do MongoDB configurado."""
    global _client

    if _client is None:
        mongo_uri = os.environ.get("MONGO_URI", "mongodb+srv://erick_ken:erickmongo123@cluster0.uzkctku.mongodb.net/?appName=Cluster0")
        _client = MongoClient(mongo_uri)

    db_name = os.environ.get("DB_NAME", "tt_performance")
    return _client[db_name]