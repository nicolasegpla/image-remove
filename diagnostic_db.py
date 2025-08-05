from app.database.sesssion import get_db
from app.models.user import User
import os
from dotenv import load_dotenv
load_dotenv()

def test_db():
    try:
        db = next(get_db())
        users = db.query(User).all()
        print(f"✅ Conexión exitosa. Usuarios encontrados: {len(users)}")
        for user in users:
            print(f"- {user.email} | Tokens: {user.tokens}")
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")

if __name__ == "__main__":
    test_db()
# diagnostic_db.py

DB_PASSWORD = os.getenv("DB_PASSWORD")
print("🔑 DB_PASSWORD desde entorno:", DB_PASSWORD)