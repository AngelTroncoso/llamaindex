#!/usr/bin/env python3
"""
Financial Regulatory Copilot Chile - Chat Interface Component

Componente de interfaz de chat para Streamlit.
Maneja el historial de conversaciones, entrada de usuario y visualización de respuestas.
"""

import streamlit as st
from typing import Dict, List, Optional, Callable, Any
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class ChatInterface:
    """Componente de interfaz de chat para la aplicación.
    
    Atributos:
        chat_container: Contenedor donde se muestra el chat.
        input_container: Contenedor para la entrada de usuario.
        message_history: Historial de mensajes.
    """
    
    def __init__(self, 
                 title: str = "Asistente de Regulación Financiera Chile",
                 placeholder: str = "Escribe tu consulta sobre normativa chilena, NIIF/IFRS, o carga documentos para analizar...",
                 height: int = 400) -> None:
        """Inicializa el ChatInterface.
        
        Args:
            title: Título del chat.
            placeholder: Texto de placeholder para el input.
            height: Altura del área de chat en píxeles.
        """
        self.title = title
        self.placeholder = placeholder
        self.height = height
        self._on_submit_callback: Optional[Callable] = None
        self._thinking_indicator: Optional[st.delta_generator.DeltaGenerator] = None
    
    def set_on_submit_callback(self, callback: Callable[[str], Any]) -> None:
        """Establece el callback para cuando se envía un mensaje.
        
        Args:
            callback: Función que recibe el mensaje del usuario y devuelve la respuesta.
        """
        self._on_submit_callback = callback
    
    def render(self) -> Optional[str]:
        """Renderiza la interfaz de chat completa.
        
        Returns:
            El mensaje del usuario si se envió uno, None en caso contrario.
        """
        # Contenedor principal
        chat_container = st.container(height=self.height, border=True)
        
        with chat_container:
            self._render_chat_header()
            self._render_messages()
        
        # Área de entrada
        user_message = self._render_input_area()
        
        return user_message
    
    def _render_chat_header(self) -> None:
        """Renderiza el encabezado del chat."""
        st.markdown(f"""
        <style>
        .chat-header {{
            background: linear-gradient(90deg, #1f77b4, #2ca02c);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem 0.5rem 0 0;
            margin: -1rem -1rem 1rem -1rem;
        }}
        .chat-header h1 {{
            margin: 0;
            font-size: 1.5rem;
        }}
        </style>
        <div class="chat-header">
            <h1>💬 {self.title}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_messages(self) -> None:
        """Renderiza los mensajes del historial de chat."""
        messages = st.session_state.get("financial_copilot_chat_history", [])
        
        if not messages:
            self._render_welcome_message()
            return
        
        # Scroll automático al final
        st.markdown("""
        <style>
        .message-container {
            margin: 0.5rem 0;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            max-width: 80%;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: auto;
            border-bottom-right-radius: 0;
        }
        .assistant-message {
            background-color: #f5f5f5;
            margin-right: auto;
            border-bottom-left-radius: 0;
        }
        .system-message {
            background-color: #fff3e0;
            margin: 0 auto;
            text-align: center;
            font-size: 0.8rem;
            color: #666;
        }
        .citations {
            font-size: 0.75rem;
            color: #666;
            margin-top: 0.5rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Mostrar mensajes
        for i, message in enumerate(messages):
            self._render_message(message, i)
    
    def _render_message(self, message: Dict[str, Any], index: int) -> None:
        """Renderiza un mensaje individual.
        
        Args:
            message: Diccionario con información del mensaje.
            index: Índice del mensaje.
        """
        role = message.get("role", "user")
        content = message.get("content", "")
        citations = message.get("citations", [])
        timestamp = message.get("timestamp", "")
        
        # Determinar clase CSS
        if role == "user":
            css_class = "user-message"
            icon = "👤"
        elif role == "assistant":
            css_class = "assistant-message"
            icon = "🤖"
        else:
            css_class = "system-message"
            icon = "ℹ️"
        
        # Contenedor del mensaje
        st.markdown(f"""
        <div class="message-container {css_class}">
            <span style="font-size: 0.9rem;">{icon} <strong>{role.upper()}</strong></span>
            <div style="margin-top: 0.25rem;">{content}</div>
        """, unsafe_allow_html=True)
        
        # Mostrar citas si existen
        if citations and role == "assistant":
            citations_html = " | ".join([f"<a href='{c}' target='_blank'>{c}</a>" for c in citations])
            st.markdown(f"""
            <div class="citations">
                📚 Fuentes: {citations_html}
            </div>
            """, unsafe_allow_html=True)
        
        # Mostrar timestamp
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime("%H:%M:%S")
                st.caption(f"{formatted_time}")
            except:
                pass
    
    def _render_welcome_message(self) -> None:
        """Renderiza el mensaje de bienvenida."""
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <h2>👋 ¡Bienvenido al Asistente de Regulación Financiera Chile!</h2>
            <p>Puedo ayudarte con:</p>
            <ul style="text-align: left; display: inline-block;">
                <li>Consultas sobre normativa BCCh, CMF, SII</li>
                <li>Análisis de estándares NIIF/IFRS</li>
                <li>Revisión de contratos y estados financieros</li>
                <li>Comparación entre normativas</li>
                <li>Recomendaciones de documentos a cargar</li>
            </ul>
            <p><em>Carga documentos en el panel izquierdo y hazme tu consulta.</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_input_area(self) -> Optional[str]:
        """Renderiza el área de entrada de usuario.
        
        Returns:
            Mensaje del usuario si se envió, None en caso contrario.
        """
        st.markdown("---")
        
        # Contenedor de entrada
        input_container = st.container()
        
        with input_container:
            # Mostrar indicador de "pensando" si está activo
            if st.session_state.get("financial_copilot_thinking", False):
                self._show_thinking_indicator()
            
            # Área de texto
            user_message = st.chat_input(
                self.placeholder,
                key="user_input",
                disabled=st.session_state.get("financial_copilot_thinking", False)
            )
            
            # Procesar mensaje si se envió
            if user_message:
                self._handle_user_message(user_message)
                return user_message
        
        return None
    
    def _handle_user_message(self, message: str) -> None:
        """Maneja el mensaje del usuario.
        
        Args:
            message: Mensaje del usuario.
        """
        logger.info(f"Mensaje del usuario: {message[:100]}...")
        
        # Agregar mensaje del usuario al historial
        self._add_message("user", message)
        
        # Mostrar indicador de pensar
        st.session_state["financial_copilot_thinking"] = True
        
        # Procesar con callback si existe
        if self._on_submit_callback:
            try:
                # Llamar al callback
                response = self._on_submit_callback(message)
                
                # Agregar respuesta al historial
                if isinstance(response, dict):
                    self._add_message("assistant", response.get("content", ""), 
                                     response.get("citations", []))
                else:
                    self._add_message("assistant", str(response))
                    
            except Exception as e:
                logger.error(f"Error en callback: {str(e)}")
                self._add_message("assistant", f"Lo siento, ocurrió un error: {str(e)}")
            finally:
                st.session_state["financial_copilot_thinking"] = False
                st.rerun()
    
    def _add_message(self, role: str, content: str, citations: Optional[List[str]] = None) -> None:
        """Agrega un mensaje al historial de chat.
        
        Args:
            role: Rol del mensaje (user, assistant, system).
            content: Contenido del mensaje.
            citations: Lista de citas (opcional).
        """
        message = {
            "role": role,
            "content": content,
            "citations": citations or [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Obtener o crear historial
        if "financial_copilot_chat_history" not in st.session_state:
            st.session_state["financial_copilot_chat_history"] = []
        
        st.session_state["financial_copilot_chat_history"].append(message)
        logger.debug(f"Mensaje agregado: {role} - {content[:50]}...")
    
    def _show_thinking_indicator(self) -> None:
        """Muestra el indicador de "pensando"."""
        import time
        
        # Usar st.progress o un spinner
        if self._thinking_indicator is None:
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("""
            <div style="text-align: center; padding: 0.5rem;">
                <div class="stSpinner" style="display: inline-block;"></div>
                <span style="margin-left: 0.5rem;">Procesando tu consulta...</span>
            </div>
            """, unsafe_allow_html=True)
            self._thinking_indicator = thinking_placeholder
    
    def clear_chat(self) -> None:
        """Limpia el historial de chat."""
        st.session_state["financial_copilot_chat_history"] = []
        logger.info("Historial de chat limpiado")
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de chat.
        
        Returns:
            Lista de mensajes del historial.
        """
        return st.session_state.get("financial_copilot_chat_history", [])
    
    def set_chat_history(self, history: List[Dict[str, Any]]) -> None:
        """Establece el historial de chat.
        
        Args:
            history: Lista de mensajes para establecer.
        """
        st.session_state["financial_copilot_chat_history"] = history


# Función conveniencia para uso directo
def create_chat_interface(title: str = "Asistente de Regulación Financiera Chile",
                         placeholder: str = "Escribe tu consulta...",
                         height: int = 400) -> ChatInterface:
    """Crea una instancia del ChatInterface.
    
    Args:
        title: Título del chat.
        placeholder: Texto de placeholder.
        height: Altura del área de chat.
        
    Returns:
        Instancia de ChatInterface.
    """
    return ChatInterface(title, placeholder, height)
