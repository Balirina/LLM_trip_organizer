import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from groq import Groq
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from urllib.parse import urlparse
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("GROQ_MODEL")


# Configuración de base de datos postgres
DATABASE_URL = os.getenv('DATABASE_URL')

'''DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", 5432)
}'''

# Inicializar cliente Groq
try:
    if GROQ_API_KEY and GROQ_API_KEY.startswith('gsk_'):
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info(f"✅ Cliente Groq inicializado con modelo: {MODEL_NAME}")
    else:
        groq_client = None
        logger.warning("❌ GROQ_API_KEY no configurada o inválida")
except Exception as e:
    logger.error(f"❌ Error inicializando Groq: {e}")
    groq_client = None

# Prompt Template simple (sin LangChain)
class SimplePromptTemplate:
    def __init__(self, template):
        self.template = template
    
    def format(self, **kwargs):
        return self.template.format(**kwargs)
    
# Funcion para convertir DATABASE_URL en config para psycopg2
def get_db_config():
    if DATABASE_URL:
        # Render usa postgres:// pero psycopg2 necesita postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        result = urlparse(DATABASE_URL)
        return {
            'host': result.hostname,
            'database': result.path[1:],  # Quita el '/' inicial
            'user': result.username,
            'password': result.password,
            'port': result.port or 5432
        }
    
    # Fallback para desarrollo local (opcional)
    return {
        'host': os.getenv("DB_HOST", "localhost"),
        'database': os.getenv("DB_NAME", "llm_chat"),
        'user': os.getenv("DB_USER", "postgres"),
        'password': os.getenv("DB_PASSWORD", ""),
        'port': os.getenv("DB_PORT", "5432")
    }
DB_CONFIG = get_db_config()


# Función para conectar a la base de datos
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"❌ Error conectando a DB: {e}")
        return None

# Crear tabla si no existe
def init_db():
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    session_id VARCHAR(100),
                    user_query TEXT NOT NULL,
                    llm_response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
            logger.info("✅ Base de datos inicializada")
        else:
            logger.warning("⚠️ No se pudo inicializar DB")
    except Exception as e:
        logger.error(f"⚠️ Error inicializando DB: {e}")
        

def get_system_prompt():
    return """"Eres un experto en viajes especializado en organizar y planear viajes. 
                    Conoces información sobre transporte, gastronomía, cultura, alojamiento y actividades turísticas de diferentes países.
                    No respondas a otras pregunstas que no sean relacionadas con los viajes y siempre intenta volver a este tema.
                    
                    INSTRUCCIONES DE FORMATO:
                    1. NUNCA uses tablas con líneas verticales (|)
                    2. Usa párrafos cortos y concisos
                    3. Usa negritas para títulos o términos importantes
                    4. Usa viñetas • para listas
                    5. Separa ideas con saltos de línea
                    6. Sé claro y directo, evita formatos complejos
                    7. Usa tamaño de letra mas grandes para titulos
                    
                    Ejemplo de cómo NO responder:
                    | Plato | Descripción |
                    |-------|-------------|
                    | Quiche | Tarta salada... |
                    
                    Ejemplo de cómo SÍ responder:
                    Quiche Lorraine
                    Tarta salada de masa quebrada rellena de crema, huevo, queso y jamón.
                    
                    Coq au vin
                    Pollo cocido lentamente en vino tiro con champiñones y tocino.
                    
                    Responde siempre en español y con este formato."""


# Endpoint principal - Página web
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint para chat
@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not groq_client:
            return jsonify({
                "error": "Servicio de IA no disponible",
                "details": "API key de Groq no configurada"
            }), 503
            
        data = request.json
        query = data.get('query', '').strip()
        session_id = data.get('session_id', 'default_session')
        
        if not query:
            return jsonify({"error": "Query vacía"}), 400
        
        # Enviar consulta a Groq
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": query}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        llm_response = response.choices[0].message.content
        current_time = datetime.utcnow()
        
        # Guardar en base de datos
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO interactions 
                (session_id, user_query, llm_response, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING created_at
            """, (session_id, query, llm_response, current_time))
            
            result = cur.fetchone()
            saved_time = result
            conn.commit()
            cur.close()
            conn.close()
        except Exception as db_error:
            logger.error(f"⚠️ Error guardando en DB: {db_error}")
            interaction_id = 0
            saved_time = datetime.utcnow()
            
        # Respuesta
        return jsonify({
            "response": llm_response,
            "session_id": session_id,
            "model_used": MODEL_NAME,
            "created_at": saved_time.isoformat() if hasattr(saved_time, 'isoformat') else str(saved_time),
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para obtener historial
@app.route('/history', methods=['GET'])
def get_history():
    try:
        session_id = request.args.get('session_id', 'default_session')
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT session_id, user_query, llm_response, created_at
            FROM interactions 
            WHERE session_id = %s 
        """, (session_id))
        
        history = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({"history": history})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Inicializar base de datos al iniciar
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Iniciando aplicación en puerto {port}")
    logger.info(f"📊 Modelo: {MODEL_NAME}")
    logger.info(f"🔗 DB Host: {DB_CONFIG.get('host', 'N/A')}")
    init_db()
    # Verificar conexiones
    if groq_client:
        logger.info("✅ Groq: Conectado")
    else:
        logger.warning("❌ Groq: No conectado - Verifica GROQ_API_KEY")
    
    if get_db_connection():
        logger.info("✅ Database: Conectada")
    else:
        logger.warning("❌ Database: No conectada")
    app.run(host='0.0.0.0', port=5000, debug=True)