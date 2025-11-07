from cassandra.cluster import Cluster

def conectar_cassandra():
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect()
    print("✅ Conectado ao Cassandra com sucesso!")
    print("📦 Keyspaces disponíveis:")
    rows = session.execute("SELECT keyspace_name FROM system_schema.keyspaces;")
    for row in rows:
        print("-", row.keyspace_name)
    return session
