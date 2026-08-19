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

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
    """Configura la página de Streamlit."""
    st.set_page_config(
        page_title="Financial Regulatory Copilot Chile",
        page_icon="🇨🇱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizado
    st.markdown("""
    <style>
    /* Estilos globales */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Estilos del sidebar */
    .css-1d391kg {
        background-color: #2c3e50;
    }
    
    /* Estilos de los botones */
    .stButton>button {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 0.25rem;
        padding: 0.5rem 1rem;
    }
    
    .stButton>button:hover {
        background-color: #2980b9;
    }
    
    /* Estilos de las tarjetas */
    .stExpander {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    /* Estilos del header */
    .header-container {
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Estilos del footer */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #666;
        font-size: 0.8rem;
        margin-top: 2rem;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Estilo para las secciones */
    .section {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
    """Renderiza la barra lateral con opciones de la aplicación."""
    with st.sidebar:
        # Logo y título
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h1 style="color: white; margin: 0;">🇨🇱</h1>
            <h2 style="color: white; margin: 0.5rem 0;">Financial Copilot</h2>
            <p style="color: #ccc; margin: 0; font-size: 0.8rem;">Asesoría Regulatoria Inteligente</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Opciones de configuración
        st.header("⚙️ Configuración")
        
        # Selección del modelo LLM
        llm_provider = st.selectbox(
            "Proveedor LLM",
            ["Ollama (Local)", "OpenAI"],
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
        else:
            model = st.selectbox(
                "Modelo",
                ["gpt-4", "gpt-3.5-turbo"],
                index=1,
                key="openai_model"
            )
        
            # Campo para API key de OpenAI
            if llm_provider == "OpenAI":
                api_key = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    key="openai_api_key"
                )
                if api_key:
                    os.environ["OPENAI_API_KEY"] = api_key
        
        st.markdown("---")
        
        # Estadísticas de la sesión
        st.header("📊 Estadísticas")
        
        session_manager = get_session_manager()
        session_info = session_manager.get_session_info()
        
        st.metric("Mensajes", session_info.get("chat_history_count", 0))
        st.metric("Documentos", session_info.get("uploaded_files_count", 0))
        st.metric("Recomendaciones", session_info.get("recommendations_count", 0))
        
        st.markdown("---")
        
        # Botones de acción
        st.header("🔄 Acciones")
        
        if st.button("🗑️ Limpiar Chat", use_container_width=True):
            session_manager.clear_chat_history()
            st.rerun()
        
        if st.button("🗑️ Limpiar Documentos", use_container_width=True):
            session_manager.clear_uploaded_files()
            st.rerun()
        
        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            session_manager.clear_all()
            st.rerun()
        
        st.markdown("---")
        
        # Información
        st.markdown("""
        <div style="padding: 1rem; background-color: #2c3e50; color: white; border-radius: 0.5rem;">
            <h4 style="color: white; margin-top: 0;">ℹ️ Sobre esta aplicación</h4>
            <p style="margin: 0; font-size: 0.8rem;">
                Asistente de regulación financiera chilena basado en IA.
                Desarrollado con LlamaIndex + RAG + Streamlit.
            </p>
        </div>
        """, unsafe_allow_html=True)


# Renderizado del área principal
def render_main_area() -> None:
    """Renderiza el área principal de la aplicación."""
    # Inicializar componentes
    file_uploader = create_file_uploader(
        label="📁 Cargar Documentos",
        accept_multiple_files=True,
        help_text="Soporta PDF, Word, Excel, TXT, CSV. Max 100MB por archivo."
    )
    
    chat_interface = create_chat_interface(
        title="Asistente de Regulación Financiera Chile",
        placeholder="Escribe tu consulta sobre normativa chilena, NIIF/IFRS, o carga documentos para analizar...",
        height=500
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
    if agent and kb and recommender:
        chat_interface.set_on_submit_callback(
            lambda msg: handle_chat_message(msg, agent, kb, recommender)
        )
    else:
        chat_interface.set_on_submit_callback(
            lambda msg: {
                "content": "Lo siento, el núcleo de la aplicación no está disponible. "
                           "Por favor, verifica que todos los módulos estén instalados correctamente.",
                "citations": []
            }
        )
    
    # Layout principal
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        # Área de carga de documentos
        st.subheader("📁 Gestión de Documentos")
        
        # Mostrar file uploader
        uploader_result = file_uploader.render_with_preview()
        
        if uploader_result.get("files"):
            # Agregar archivos al session_state
            for file_info in uploader_result["files"]:
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
            st.success(f"✅ {len(uploaded_files)} documento(s) cargado(s)")
        
        # Mostrar recomendaciones
        st.markdown("---")
        recommendation_engine.render()
    
    with col2:
        # Área de chat
        st.subheader("💬 Chat")
        chat_interface.render()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Financial Regulatory Copilot Chile v0.1.0 | Desarrollado con ❤️ usando Streamlit + LlamaIndex + IA</p>
    </div>
    """, unsafe_allow_html=True)


# Función principal
def main() -> None:
    """Función principal de la aplicación Streamlit."""
    configure_page()
    initialize_state()
    
    # Encabezado principal
    st.markdown("""
    <div class="header-container">
        <h1>🇨🇱 Financial Regulatory Copilot Chile</h1>
        <p style="font-size: 1.1rem; margin: 0.5rem 0;">
            Asistente de IA para normativa financiera chilena (BCCh, CMF, SII, NIIF/IFRS)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar advertencia si el núcleo no está disponible
    if not CORE_AVAILABLE:
        st.warning("⚠️ Advertencia: El núcleo de la aplicación no está disponible. "
                   "Algunas funcionalidades pueden no trabajar correctamente.")
    
    # Renderizar interfaz
    render_sidebar()
    render_main_area()


# Ejecutar la aplicación
if __name__ == "__main__":
    main()
