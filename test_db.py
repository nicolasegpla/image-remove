import psycopg2

try:
    conn = psycopg2.connect(
        dbname="image_processor",
        user="image_user",
        password="Viajerola1",
        host="host.docker.internal",  # Esto funciona dentro del contenedor
        port="5432"
    )
    print("✅ Conexión exitosa a PostgreSQL")
    conn.close()
except Exception as e:
    print("❌ Error de conexión:", e)
