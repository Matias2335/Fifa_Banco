# db/postgres.py
import psycopg2
import psycopg2.extras

def conectar_postgres():
    """
    Abre conexão no banco Fifa_Ultimate e define o search_path=fut.
    Retorna a conexão aberta (caller fecha depois).
    """
    conn = psycopg2.connect(
        host="localhost",
        port=5432,                 # int é ok, string também
        dbname="Fifa_Ultimate",    # nome do banco (como aparece no pgAdmin)
        user="postgres",
        password="Gui@2535"
    )
    # define o schema padrão para não precisar prefixar fut.
    with conn.cursor() as cur:
        cur.execute("SET search_path TO fut;")
    return conn


def teste_conexao():
    try:
        conn = conectar_postgres()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            print("✅ Conectado! SELECT 1 ->", cur.fetchone()[0])
        conn.close()
    except psycopg2.Error as e:
        print("❌ Erro psycopg2:", e.pgerror or str(e))
    except Exception as e:
        print("❌ Erro geral:", str(e))


if __name__ == "__main__":
    teste_conexao()
