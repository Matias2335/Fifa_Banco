# s2.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from postgres import conectar_postgres
from mongodb import conectar_mongo
from cassandra_connect import conectar_cassandra
from cassandra.query import SimpleStatement
from pymongo.errors import ServerSelectionTimeoutError

app = Flask(__name__)
CORS(app)

def rows_to_dicts(cur):
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

@app.get("/health")
def health():
    return jsonify({"ok": True, "ts": datetime.utcnow().isoformat()})


# =============== POSTGRES: USUÁRIOS ===============
@app.post("/usuarios")
def inserir_usuario():
    data = request.json
    conn = conectar_postgres()
    if not conn:
        return jsonify({"erro": "Falha ao conectar ao PostgreSQL"}), 500
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO fut.usuarios
                (id_usuario, nickname, email, senha_hash, pais_origem, data_criacao)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (data["id_usuario"], data["nickname"], data["email"],
              data["senha_hash"], data["pais_origem"], data["data_criacao"]))
        conn.commit()
        return jsonify({"status": "Usuário inserido com sucesso!"})
    finally:
        cur.close(); conn.close()


@app.get("/usuarios")
def listar_usuarios():
    conn = conectar_postgres()
    if not conn:
        return jsonify({"erro": "Falha ao conectar ao PostgreSQL"}), 500
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO fut;")
        cur.execute("""
            SELECT
              id_usuario,
              nickname,
              email,
              senha_hash,
              pais_origem,
              to_char(data_criacao, 'YYYY-MM-DD HH24:MI:SS') AS data_criacao
            FROM usuarios
            ORDER BY id_usuario ASC;
        """)
        return jsonify(rows_to_dicts(cur))
    finally:
        cur.close(); conn.close()


# =============== POSTGRES: TRANSAÇÕES ===============
@app.post("/transacoes")
def inserir_transacao():
    data = request.json
    conn = conectar_postgres()
    if not conn:
        return jsonify({"erro": "Falha ao conectar ao PostgreSQL"}), 500
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO fut.transacoes
                (id_transacao, id_usuario, jogador_id, tipo, valor, data_transacao)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (data["id_transacao"], data["id_usuario"], data["jogador_id"],
              data["tipo"], data["valor"], data["data_transacao"]))
        conn.commit()
        return jsonify({"status": "Transação inserida com sucesso!"})
    finally:
        cur.close(); conn.close()


@app.get("/transacoes")
def listar_transacoes():
    conn = conectar_postgres()
    if not conn:
        return jsonify({"erro": "Falha ao conectar ao PostgreSQL"}), 500
    id_usuario = request.args.get("id_usuario", type=int)
    nickname   = request.args.get("nickname")
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO fut;")
        if nickname:
            cur.execute("""
              SELECT
                u.nickname,
                t.id_transacao,
                t.id_usuario,
                t.jogador_id,
                t.tipo,
                t.valor,
                to_char(t.data_transacao, 'YYYY-MM-DD') AS data_transacao
              FROM transacoes t
              JOIN usuarios u ON u.id_usuario = t.id_usuario
              WHERE u.nickname = %s
              ORDER BY t.id_transacao ASC;
            """, (nickname,))
        elif id_usuario:
            cur.execute("""
              SELECT
                id_transacao, id_usuario, jogador_id, tipo, valor,
                to_char(data_transacao, 'YYYY-MM-DD') AS data_transacao
              FROM transacoes
              WHERE id_usuario = %s
              ORDER BY id_transacao ASC;
            """, (id_usuario,))
        else:
            cur.execute("""
              SELECT
                id_transacao, id_usuario, jogador_id, tipo, valor,
                to_char(data_transacao, 'YYYY-MM-DD') AS data_transacao
              FROM transacoes
              ORDER BY id_transacao ASC;
            """)
        return jsonify(rows_to_dicts(cur))
    finally:
        cur.close(); conn.close()


# =============== MONGODB: ESTATÍSTICAS ===============
@app.post("/estatisticas")
def inserir_estatisticas():
    data = request.json
    try:
        db = conectar_mongo()
        col = db["Estatisticas_jogador"]
        col.insert_one(data)
        return jsonify({"status": "Estatística inserida no MongoDB!"})
    except ServerSelectionTimeoutError:
        return jsonify({"erro": "MongoDB indisponível"}), 503


@app.get("/estatisticas")
def listar_estatisticas():
    try:
        db = conectar_mongo()
        col = db["Estatisticas_jogador"]
        # ordena por id ascendente se existir campo id
        docs = list(col.find({}, {"_id": 0}).sort("id", 1).limit(500))
        return jsonify(docs)
    except ServerSelectionTimeoutError:
        return jsonify([])


# =============== CASSANDRA: JOGADORES ===============
@app.post("/jogadores")
def inserir_jogador():
    data = request.json
    session = conectar_cassandra()
    if not session:
        return jsonify({"erro": "Falha ao conectar ao Cassandra"}), 500
    session.set_keyspace("futdb")
    session.execute("""
        INSERT INTO jogadores (id, nome, overall, posicao, quantidade, raridade, valor)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (data["id"], data["nome"], data["overall"], data["posicao"],
          data["quantidade"], data["raridade"], data["valor"]))
    return jsonify({"status": "Jogador inserido no Cassandra!"})


@app.get("/jogadores")
def listar_jogadores():
    session = conectar_cassandra()
    if not session:
        return jsonify({"erro": "Falha ao conectar ao Cassandra"}), 500
    session.set_keyspace("futdb")
    # ordena por id ascendente
    rows = session.execute(SimpleStatement("""
        SELECT id, nome, overall, posicao, quantidade, raridade, valor
        FROM jogadores
    """))
    # Cassandra não suporta ORDER BY genérico, então ordenamos em memória:
    data = sorted([dict(r._asdict()) for r in rows], key=lambda x: x["id"])
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
