#!/usr/bin/env python3
"""
Financial Regulatory Copilot Chile - Main Streamlit Application

Aplicación principal de Streamlit para el Asistente de Regulación Financiera Chile.
Integra todos los componentes y proporciona la interfaz de usuario completa.
"""

import streamlit as st
from typing import Dict, List, Any, Optional
import logging
import sys
import os

# Importar cliente de Gemini (opcional, solo si está instalado)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar componentes
from app.components.file_uploader import FileUploader, create_file_uploader
from app.components.chat_interface import ChatInterface, create_chat_interface
from app.components.recommendation_engine import RecommendationEngine, create_recommendation_engine
from app.utils.session_manager import SessionManager, get_session_manager

# Importar núcleo
try:
    from core.agent.financial_agent import FinancialAgent
    from core.agent.knowledge_base import KnowledgeBase
    from core.agent.data_recommender import DataRecommender
    CORE_AVAILABLE = True
except ImportError as e:
    CORE_AVAILABLE = False
    logging.warning(f"Core no disponible: {str(e)}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Configuración de la página
def configure_page() -> None:
    """Configura la página de Streamlit con estilo premium."""
    st.set_page_config(
        page_title="Financial Regulatory Copilot Chile",
        page_icon="🇨🇱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS Premium Completo
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #0F3D54;
        --secondary: #2E86AB;
        --accent: #F26522;
        --success: #28A745;
        --warning: #FFC107;
        --danger: #DC3545;
        --background: #F8F9FA;
        --card-bg: #FFFFFF;
        --text: #1E293B;
        --text-light: #64748B;
        --border-radius: 12px;
        --transition: all 0.3s ease;
    }
    
    * { font-family: 'Inter', sans-serif !important; }
    
    /* ===== ESTILOS GLOBALES ===== */
    .main { background: linear-gradient(to bottom, #F8F9FA 0%, #E9ECEF 100%) !important; }
    
    /* ===== SIDEBAR PREMIUM ===== */
    .css-1d391kg {
        background: linear-gradient(180deg, #0F3D54 0%, #1A4D6A 100%) !important;
        box-shadow: 2px 0 10px rgba(15, 61, 84, 0.3) !important;
    }
    
    /* Logo con efecto 3D */
    .sidebar-logo {
        background: linear-gradient(135deg, #FFFFFF 0%, #E0E0E0 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* ===== HEADER ESPECTACULAR ===== */
    .header-container {
        background: linear-gradient(135deg, #0F3D54 0%, #2E86AB 50%, #F26522 100%);
        color: white;
        padding: 2rem 1.5rem;
        border-radius: var(--border-radius);
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(15, 61, 84, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    /* ===== BOTONES PREMIUM ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: var(--transition) !important;
        box-shadow: 0 4px 10px rgba(15, 61, 84, 0.2) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        height: auto !important;
        min-height: auto !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(15, 61, 84, 0.3) !important;
        background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Botones de Limpiar (Danger) */
    .stButton > button:has-text("Limpiar") {
        background: linear-gradient(135deg, var(--danger) 0%, #C82333 100%) !important;
    }
    
    .stButton > button:has-text("Limpiar"):hover {
        background: linear-gradient(135deg, #C82333 0%, var(--danger) 100%) !important;
    }
    
    /* ===== CARDS PREMIUM ===== */
    .stExpander {
        background: white !important;
        border-radius: var(--border-radius) !important;
        border: 1px solid #E9ECEF !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        transition: var(--transition) !important;
        margin: 0.75rem 0 !important;
    }
    
    .stExpander:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.12) !important;
        transform: translateY(-2px) !important;
    }
    
    /* ===== FILE UPLOADER ENHANCED ===== */
    .stFileUploader {
        border: 2px dashed var(--secondary) !important;
        border-radius: var(--border-radius) !important;
        padding: 2rem !important;
        background: white !important;
        transition: var(--transition) !important;
        text-align: center !important;
    }
    
    .stFileUploader:hover {
        border-color: var(--primary) !important;
        box-shadow: 0 4px 15px rgba(46, 134, 171, 0.2) !important;
    }
    
    .stFileUploader > div {
        color: var(--text) !important;
    }
    
    /* ===== FORM INPUTS ===== */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 8px !important;
        border: 1px solid #E9ECEF !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--secondary) !important;
        box-shadow: 0 0 0 3px rgba(46, 134, 171, 0.1) !important;
    }
    
    /* ===== CHAT MESSAGES ===== */
    .chat-message {
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 0.5rem 0;
        max-width: 85%;
        position: relative;
        animation: fadeIn 0.3s ease;
        line-height: 1.5;
    }
    
    .user-message {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        margin-left: auto;
        border-bottom-right-radius: 0;
        color: var(--text);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #F5F5F5 0%, #E0E0E0 100%);
        margin-right: auto;
        border-bottom-left-radius: 0;
        color: var(--text);
    }
    
    .system-message {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        margin: 0 auto;
        text-align: center;
        font-size: 0.85rem;
        color: var(--text-light);
    }
    
    .message-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
    }
    
    .user-avatar {
        right: -45px;
        background: var(--primary);
        color: white;
    }
    
    .assistant-avatar {
        left: -45px;
        background: var(--secondary);
        color: white;
    }
    
    .message-content {
        padding: 0.5rem 1rem;
    }
    
    .message-role {
        font-size: 0.8rem;
        color: var(--text-light);
        margin-bottom: 0.25rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* ===== SCROLLBAR CUSTOM ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F1F1F1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary) 0%, var(--secondary) 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent);
    }
    
    /* ===== ANIMACIONES ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes loadingBar {
        0% { margin-left: -100%; }
        100% { margin-left: 100%; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* ===== LOADING SPINNER ===== */
    .stSpinner > div {
        border-top-color: var(--accent) !important;
        border-width: 3px !important;
    }
    
    /* ===== METRICS EN SIDEBAR ===== */
    .stMetric {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        margin: 0.5rem 0 !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    
    .stMetric label {
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
    
    .stMetric div {
        color: white !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    
    /* ===== FOOTER ELEGANTE ===== */
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: var(--text-light);
        font-size: 0.85rem;
        margin-top: 2rem;
        border-top: 1px solid #E9ECEF;
        background: white;
        border-radius: var(--border-radius) var(--border-radius) 0 0;
    }
    
    .footer p {
        margin: 0;
    }
    
    /* ===== TOOLTIPS ===== */
    [data-tooltip] {
        position: relative;
    }
    
    [data-tooltip]::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: var(--primary);
        color: white;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.8rem;
        white-space: nowrap;
        margin-bottom: 0.5rem;
        opacity: 0;
        transition: opacity 0.3s;
        z-index: 1000;
        pointer-events: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    [data-tooltip]:hover::after {
        opacity: 1;
    }
    
    /* ===== SECCIONES ===== */
    .section-title {
        color: var(--primary);
        font-size: 1.25rem;
        font-weight: 700;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid var(--secondary);
        display: inline-block;
    }
    
    .section-subtitle {
        color: var(--text-light);
        font-size: 0.95rem;
        font-style: italic;
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* ===== INFO MESSAGES ===== */
    .stAlert {
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }
    
    /* ===== THINKING INDICATOR ===== */
    .thinking-container {
        text-align: center;
        padding: 1rem;
    }
    
    .thinking-bar {
        width: 100%;
        height: 4px;
        background: #E9ECEF;
        border-radius: 2px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .thinking-bar-inner {
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
        animation: loadingBar 2s infinite;
        border-radius: 2px;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .header-container {
            padding: 1.5rem 1rem !important;
        }
        .chat-message {
            max-width: 90% !important;
        }
        .user-avatar {
            right: -40px !important;
        }
        .assistant-avatar {
            left: -40px !important;
        }
    }
    
    /* ===== WELCOME MESSAGE ===== */
    .welcome-container {
        background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
        border-radius: var(--border-radius);
        margin: 1rem 0;
        padding: 2rem;
        text-align: center;
    }
    
    .welcome-icon {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        box-shadow: 0 4px 15px rgba(15, 61, 84, 0.3);
    }
    
    .welcome-icon span {
        font-size: 2.5rem;
    }
    
    .welcome-title {
        color: var(--primary);
        margin: 0.5rem 0;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .welcome-subtitle {
        color: var(--text-light);
        margin: 1rem 0;
        font-size: 1.05rem;
    }
    
    .welcome-features {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: left;
    }
    
    .welcome-features p {
        margin: 0 0 0.5rem 0;
        color: var(--text);
        font-weight: 600;
    }
    
    .welcome-features ul {
        padding-left: 1.5rem;
        color: var(--text-light);
    }
    
    .welcome-features li {
        margin: 0.5rem 0;
    }
    
    .welcome-features li::before {
        content: "✅ ";
        color: var(--success);
        font-weight: bold;
    }
    
    .welcome-tip {
        color: var(--text-light);
        font-style: italic;
        margin: 1rem 0 0 0;
    }
    </style>
    """, unsafe_allow_html=True)


# Inicialización del estado
def initialize_state() -> Dict[str, Any]:
    """Inicializa el estado de la aplicación.
    
    Returns:
        Diccionario con el estado inicial.
    """
    state = {
        "initialized": True,
        "agent": None,
        "knowledge_base": None,
        "recommender": None,
        "session_manager": None
    }
    
    # Inicializar session_state si no existe
    if "financial_copilot_initialized" not in st.session_state:
        st.session_state["financial_copilot_initialized"] = True
        st.session_state["financial_copilot_chat_history"] = []
        st.session_state["financial_copilot_uploaded_files"] = []
        st.session_state["financial_copilot_recommendations"] = []
        st.session_state["financial_copilot_thinking"] = False
    
    return state


# Carga de documentos base
def load_base_knowledge() -> Optional[KnowledgeBase]:
    """Carga los documentos base de conocimiento.
    
    Returns:
        Instancia de KnowledgeBase con documentos base cargados.
    """
    if not CORE_AVAILABLE:
        return None
    
    try:
        kb = KnowledgeBase()
        
        # Ruta a los documentos base
        base_data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "app", "data", "base"
        )
        
        # Cargar documentos si el directorio existe
        if os.path.exists(base_data_path):
            for filename in os.listdir(base_data_path):
                filepath = os.path.join(base_data_path, filename)
                if os.path.isfile(filepath):
                    try:
                        kb.add_document(filepath, user_uploaded=False)
                        logger.info(f"Documento base cargado: {filename}")
                    except Exception as e:
                        logger.warning(f"Error cargando documento base {filename}: {str(e)}")
        else:
            logger.warning(f"Directorio de documentos base no encontrado: {base_data_path}")
        
        return kb
        
    except Exception as e:
        logger.error(f"Error cargando conocimiento base: {str(e)}")
        return None


# Creación del agente financiero
def create_financial_agent() -> Optional[FinancialAgent]:
    """Crea una instancia del agente financiero.
    
    Returns:
        Instancia de FinancialAgent.
    """
    if not CORE_AVAILABLE:
        return None
    
    try:
        agent = FinancialAgent()
        logger.info("Agente financiero creado")
        return agent
    except Exception as e:
        logger.error(f"Error creando agente financiero: {str(e)}")
        return None


def create_data_recommender() -> Optional[DataRecommender]:
    """Crea una instancia del DataRecommender.
    
    Returns:
        Instancia de DataRecommender.
    """
    if not CORE_AVAILABLE:
        return None
    
    try:
        recommender = DataRecommender()
        logger.info("DataRecommender creado")
        return recommender
    except Exception as e:
        logger.error(f"Error creando DataRecommender: {str(e)}")
        return None


# Callback para procesar mensajes del chat con LLM directo
def handle_chat_message_with_gemini(message: str) -> Dict[str, Any]:
    """Procesa mensaje usando Google Gemini directamente.
    
    Args:
        message: Mensaje del usuario.
        
    Returns:
        Diccionario con la respuesta.
    """
    try:
        if not GEMINI_AVAILABLE or "GOOGLE_API_KEY" not in os.environ:
            return {
                "content": "Por favor, configura tu API Key de Google Gemini en la barra lateral.",
                "citations": []
            }
        
        # Obtener modelo seleccionado
        model_name = st.session_state.get("gemini_model", "gemini-1.5-flash")
        
        # Crear cliente y modelo
        client = genai.Client()
        model = client.models.get(model_name)
        
        # Generar respuesta
        response = model.generate_content(message)
        
        # Devolver respuesta
        return {
            "content": response.text,
            "citations": []
        }
        
    except Exception as e:
        logger.error(f"Error con Gemini: {str(e)}")
        return {
            "content": f"Error al usar Gemini: {str(e)}",
            "citations": []
        }


# Callback para procesar mensajes del chat
def handle_chat_message(message: str, agent: FinancialAgent, 
                        kb: KnowledgeBase, recommender: DataRecommender) -> Dict[str, Any]:
    """Procesa un mensaje del usuario y genera una respuesta.
    
    Args:
        message: Mensaje del usuario.
        agent: Instancia del agente financiero.
        kb: Instancia de la base de conocimiento.
        recommender: Instancia del DataRecommender.
        
    Returns:
        Diccionario con la respuesta y citas.
    """
    try:
        # Actualizar última consulta en session_state
        st.session_state["financial_copilot_last_query"] = message
        
        # Obtener recomendaciones
        recommendations = recommender.recommend(message)
        st.session_state["financial_copilot_recommendations"] = recommendations
        
        # Procesar con el agente
        response = agent.respond(message)
        
        # Devolver respuesta con citas
        return {
            "content": response,
            "citations": response.get("citations", []) if isinstance(response, dict) else []
        }
        
    except Exception as e:
        logger.error(f"Error procesando mensaje: {str(e)}")
        return {
            "content": f"Lo siento, ocurrió un error al procesar tu consulta: {str(e)}",
            "citations": []
        }


# Callback para selección de documentos recomendados
def handle_document_select(recommendation: Dict[str, Any]) -> None:
    """Maneja la selección de un documento recomendado.
    
    Args:
        recommendation: Diccionario con información del documento recomendado.
    """
    st.info(f"Documento recomendado seleccionado: {recommendation.get('name')}")
    
    # Aquí se podría implementar la descarga automática o mostrar más información
    if recommendation.get("url"):
        st.markdown(f"[Descargar documento]({recommendation.get('url')})")


# Renderizado de la barra lateral
def render_sidebar() -> None:
    """Renderiza la barra lateral con estilo premium."""
    with st.sidebar:
        # Logo premium
        st.markdown("""
        <div class="sidebar-logo" style="text-align: center;">
            <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #FFFFFF 0%, #E0E0E0 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <span style="font-size: 2rem;">🤖</span>
            </div>
            <h2 style="color: white; margin: 0.5rem 0; font-size: 1.25rem; font-weight: 700;">Financial Copilot</h2>
            <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 0.8rem; font-weight: 500;">Asesoría Regulatoria Inteligente</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sección de configuración
        st.markdown("<div style='color: rgba(255,255,255,0.8); font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem;'>⚙️ CONFIGURACIÓN</div>", unsafe_allow_html=True)
        
        # Selección del modelo LLM
        llm_provider = st.selectbox(
            "Proveedor LLM",
            ["Google Gemini", "Ollama (Local)", "OpenAI"],
            index=0,
            key="llm_provider"
        )
        
        if llm_provider == "Ollama (Local)":
            model = st.selectbox(
                "Modelo",
                ["llama3.2:70b", "mistral:latest", "llama3.2:3b"],
                index=1,
                key="ollama_model"
            )
        elif llm_provider == "OpenAI":
            model = st.selectbox(
                "Modelo",
                ["gpt-4", "gpt-3.5-turbo"],
                index=1,
                key="openai_model"
            )
            # Campo para API key de OpenAI
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                key="openai_api_key"
            )
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
        elif llm_provider == "Google Gemini" and GEMINI_AVAILABLE:
            model = st.selectbox(
                "Modelo",
                ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
                index=0,
                key="gemini_model"
            )
            # Campo para API key de Google
            gemini_api_key = st.text_input(
                "Google API Key (Gemini)",
                type="password",
                key="gemini_api_key"
            )
            if gemini_api_key:
                os.environ["GOOGLE_API_KEY"] = gemini_api_key
                # Inicializar cliente de Gemini
                genai.configure(api_key=gemini_api_key)
                st.session_state["gemini_client_configured"] = True
        
        st.markdown("---")
        
        # Estadísticas de la sesión
        st.markdown("<div style='color: rgba(255,255,255,0.8); font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem;'>📊 ESTADÍSTICAS DE SESIÓN</div>", unsafe_allow_html=True)
        
        session_manager = get_session_manager()
        session_info = session_manager.get_session_info()
        
        # Métricas con estilo premium
        st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin: 0.5rem 0;">
        """, unsafe_allow_html=True)
        
        st.metric("💬 Mensajes", session_info.get("chat_history_count", 0))
        st.metric("📁 Documentos", session_info.get("uploaded_files_count", 0))
        st.metric("📚 Recomendaciones", session_info.get("recommendations_count", 0))
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Botones de acción
        st.markdown("<div style='color: rgba(255,255,255,0.8); font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem;'>🔄 ACCIONES</div>", unsafe_allow_html=True)
        
        # Botones con tooltips
        cols = st.columns(1)
        with cols[0]:
            if st.button("🗑️ Limpiar Chat", use_container_width=True, key="clear_chat"):
                session_manager.clear_chat_history()
                st.rerun()
            
            if st.button("🗑️ Limpiar Documentos", use_container_width=True, key="clear_docs"):
                session_manager.clear_uploaded_files()
                st.rerun()
            
            if st.button("🗑️ Limpiar Todo", use_container_width=True, key="clear_all"):
                session_manager.clear_all()
                st.rerun()
        
        st.markdown("---")
        
        # Información
        st.markdown("""
        <div style="padding: 1rem; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2);">
            <p style="margin: 0; font-size: 0.85rem; line-height: 1.5;">
                <strong>ℹ️ Sobre esta aplicación</strong><br>
                <br>
                Asistente de IA especializado en normativa financiera chilena.<br>
                <br>
                <small>Desarrollado con ❤️ usando Streamlit + LlamaIndex + IA</small>
            </p>
        </div>
        """, unsafe_allow_html=True)


# Renderizado del área principal
def render_main_area() -> None:
    """Renderiza el área principal con diseño premium."""
    # Detección de móvil (simplificada)
    if 'mobile' not in st.session_state:
        st.session_state.mobile = False  # Streamlit no tiene screen_width en todos los entornos
    
    # Configurar layout según dispositivo
    if st.session_state.mobile:
        col1, col2 = st.columns([1, 1], gap="medium")
        chat_height = 350
    else:
        col1, col2 = st.columns([1, 2], gap="large")
        chat_height = 500
    
    # Inicializar componentes
    file_uploader = create_file_uploader(
        label="📁 Cargar Documentos",
        accept_multiple_files=True,
        help_text="Arrastra múltiples archivos aquí. Soporta PDF, Word, Excel, TXT, CSV. Max 100MB."
    )
    
    chat_interface = create_chat_interface(
        title="Financial Regulatory Copilot",
        placeholder="Escribe tu consulta sobre normativa chilena...",
        height=chat_height
    )
    
    recommendation_engine = create_recommendation_engine(
        title="📚 Documentos Recomendados",
        max_recommendations=10
    )
    
    # Inicializar el núcleo si está disponible
    agent = None
    kb = None
    recommender = None
    
    if CORE_AVAILABLE:
        kb = load_base_knowledge()
        agent = create_financial_agent()
        recommender = create_data_recommender()
        
        if agent and kb:
            agent.set_knowledge_base(kb)
        
        if recommendation_engine and recommender:
            recommendation_engine.set_recommender(recommender)
            recommendation_engine.set_on_document_select_callback(handle_document_select)
    
    # Configurar callback del chat
    llm_provider = st.session_state.get("llm_provider", "Google Gemini")
    
    if llm_provider == "Google Gemini" and GEMINI_AVAILABLE:
        chat_interface.set_on_submit_callback(handle_chat_message_with_gemini)
    elif agent and kb and recommender:
        chat_interface.set_on_submit_callback(
            lambda msg: handle_chat_message(msg, agent, kb, recommender)
        )
    else:
        chat_interface.set_on_submit_callback(
            lambda msg: {
                "content": "Lo siento, el núcleo de la aplicación no está disponible. Configura tu API Key.",
                "citations": []
            }
        )
    
    # Layout principal
    with col1:
        # Área de carga de documentos
        st.markdown('<p class="section-title">📁 Gestión de Documentos</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Carga múltiples archivos para analizar con el asistente</p>', unsafe_allow_html=True)
        
        # Mostrar file uploader
        uploader_result = file_uploader.render_with_preview()
        
        if uploader_result.get("files"):
            # Agregar archivos al session_state
            for file_info in uploader_result["files"]:
                if file_info not in st.session_state["financial_copilot_uploaded_files"]:
                    st.session_state["financial_copilot_uploaded_files"].append(file_info)
                
                # Intentar agregar al knowledge base si está disponible
                if kb and agent:
                    try:
                        kb.add_document_from_bytes(
                            file_info["path"],
                            file_info["name"],
                            user_uploaded=True
                        )
                        agent.add_user_document_from_bytes(
                            file_info["path"],
                            file_info["name"]
                        )
                        logger.info(f"Documento agregado a KB: {file_info['name']}")
                    except Exception as e:
                        logger.error(f"Error agregando documento a KB: {str(e)}")
        
        # Mostrar estadísticas de documentos
        uploaded_files = st.session_state.get("financial_copilot_uploaded_files", [])
        if uploaded_files:
            st.success(f"✅ **{len(uploaded_files)} documento(s) cargado(s)**")
        else:
            st.info("👆 Carga documentos para que el asistente pueda analizar su contenido")
        
        # Mostrar recomendaciones
        st.markdown("---")
        st.markdown('<p class="section-title">📚 Análisis</p>', unsafe_allow_html=True)
        recommendation_engine.render()
    
    with col2:
        # Área de chat
        st.markdown('<p class="section-title">💬 Asistente de IA</p>', unsafe_allow_html=True)
        chat_interface.render()
    
    # Footer premium
    st.markdown("""
    <div class="footer">
        <p><strong>Financial Regulatory Copilot Chile v1.0</strong> | Desarrollado con ❤️ usando Streamlit + LlamaIndex + IA</p>
    </div>
    """, unsafe_allow_html=True)


# Función principal
def main() -> None:
    """Función principal de la aplicación Streamlit."""
    configure_page()
    initialize_state()
    
    # Encabezado principal premium
    st.markdown("""
    <div class="header-container">
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="background: white; padding: 1rem; border-radius: 50%; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                <span style="font-size: 2.5rem;">🇨🇱</span>
            </div>
        </div>
        <h1 style="font-size: 2rem; margin: 0.5rem 0; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            Financial Regulatory Copilot
        </h1>
        <p style="font-size: 1.1rem; margin: 0.5rem 0; opacity: 0.95; color: white;">
            Asistente de IA para normativa financiera chilena
        </p>
        <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                BCCh
            </span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                CMF
            </span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                SII
            </span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                NIIF/IFRS
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar advertencia si el núcleo no está disponible
    if not CORE_AVAILABLE:
        st.warning("⚠️ El núcleo avanzado no está disponible. La app funciona con Gemini directamente. Para más funcionalidades, instala los módulos core.")
    
    # Renderizar interfaz
    render_sidebar()
    render_main_area()


# Ejecutar la aplicación
if __name__ == "__main__":
    main()
