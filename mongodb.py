# mongodb.py
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

MONGO_URI = "mongodb://localhost:27017"
MONGO_DB  = "Informações"  # ← exatamente como está no Compass

def conectar_mongo():
    """
    Retorna o objeto Database. Lança exceção se não conectar.
    """
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    # força um ping rápido; se não responder em 3s, cai fora
    client.admin.command("ping")
    return client[MONGO_DB]
