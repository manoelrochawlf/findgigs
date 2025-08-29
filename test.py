from database import get_mariadb_connection, get_redis_connection

# Teste MySQL
try:
    conn = get_mariadb_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    print("✅ MySQL conectado! Tabelas:", cursor.fetchall())
    cursor.close()
    conn.close()
except Exception as e:
    print("❌ Erro MySQL:", e)

# Teste Redis
try:
    client = get_redis_connection()
    client.set("teste", "ok")
    print("✅ Redis conectado! Valor teste:", client.get("teste"))
except Exception as e:
    print("❌ Erro Redis:", e)
