#!/usr/bin/env python3
"""
Financial Regulatory Copilot Chile - Session Manager

Gestor de estado de sesión para Streamlit.
Maneja el estado persistente entre reruns de la aplicación.
"""

from typing import Any, Dict, List, Optional
import streamlit as st
import uuid
import logging

# Configure logging
logger = logging.getLogger(__name__)


class SessionManager:
    """Gestor de estado de sesión para la aplicación Streamlit.
    
    Atributos:
        session_id: ID único de la sesión actual.
        user_id: ID único del usuario (generado o proporcionado).
    """
    
    # Claves de estado de Streamlit
    SESSION_ID_KEY = "financial_copilot_session_id"
    USER_ID_KEY = "financial_copilot_user_id"
    CHAT_HISTORY_KEY = "financial_copilot_chat_history"
    UPLOADED_FILES_KEY = "financial_copilot_uploaded_files"
    AGENT_STATE_KEY = "financial_copilot_agent_state"
    RECOMMENDATIONS_KEY = "financial_copilot_recommendations"
    LAST_QUERY_KEY = "financial_copilot_last_query"
    
    def __init__(self) -> None:
        """Inicializa el SessionManager."""
        self._initialize_session()
    
    def _initialize_session(self) -> None:
        """Inicializa las claves de sesión si no existen."""
        if self.SESSION_ID_KEY not in st.session_state:
            st.session_state[self.SESSION_ID_KEY] = str(uuid.uuid4())
            logger.info(f"Nueva sesión iniciada: {st.session_state[self.SESSION_ID_KEY]}")
        
        if self.USER_ID_KEY not in st.session_state:
            st.session_state[self.USER_ID_KEY] = str(uuid.uuid4())
            logger.info(f"Nuevo usuario: {st.session_state[self.USER_ID_KEY]}")
        
        if self.CHAT_HISTORY_KEY not in st.session_state:
            st.session_state[self.CHAT_HISTORY_KEY] = []
        
        if self.UPLOADED_FILES_KEY not in st.session_state:
            st.session_state[self.UPLOADED_FILES_KEY] = []
        
        if self.AGENT_STATE_KEY not in st.session_state:
            st.session_state[self.AGENT_STATE_KEY] = {}
        
        if self.RECOMMENDATIONS_KEY not in st.session_state:
            st.session_state[self.RECOMMENDATIONS_KEY] = []
        
        if self.LAST_QUERY_KEY not in st.session_state:
            st.session_state[self.LAST_QUERY_KEY] = ""
    
    @property
    def session_id(self) -> str:
        """Obtiene el ID de la sesión actual."""
        return st.session_state.get(self.SESSION_ID_KEY, "")
    
    @property
    def user_id(self) -> str:
        """Obtiene el ID del usuario actual."""
        return st.session_state.get(self.USER_ID_KEY, "")
    
    @property
    def chat_history(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de chat de la sesión actual."""
        return st.session_state.get(self.CHAT_HISTORY_KEY, [])
    
    @chat_history.setter
    def chat_history(self, value: List[Dict[str, Any]]) -> None:
        """Establece el historial de chat."""
        st.session_state[self.CHAT_HISTORY_KEY] = value
    
    @property
    def uploaded_files(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de archivos subidos por el usuario."""
        return st.session_state.get(self.UPLOADED_FILES_KEY, [])
    
    @uploaded_files.setter
    def uploaded_files(self, value: List[Dict[str, Any]]) -> None:
        """Establece la lista de archivos subidos."""
        st.session_state[self.UPLOADED_FILES_KEY] = value
    
    @property
    def agent_state(self) -> Dict[str, Any]:
        """Obtiene el estado del agente."""
        return st.session_state.get(self.AGENT_STATE_KEY, {})
    
    @agent_state.setter
    def agent_state(self, value: Dict[str, Any]) -> None:
        """Establece el estado del agente."""
        st.session_state[self.AGENT_STATE_KEY] = value
    
    @property
    def recommendations(self) -> List[Dict[str, Any]]:
        """Obtiene las recomendaciones actuales."""
        return st.session_state.get(self.RECOMMENDATIONS_KEY, [])
    
    @recommendations.setter
    def recommendations(self, value: List[Dict[str, Any]]) -> None:
        """Establece las recomendaciones actuales."""
        st.session_state[self.RECOMMENDATIONS_KEY] = value
    
    @property
    def last_query(self) -> str:
        """Obtiene la última consulta realizada."""
        return st.session_state.get(self.LAST_QUERY_KEY, "")
    
    @last_query.setter
    def last_query(self, value: str) -> None:
        """Establece la última consulta realizada."""
        st.session_state[self.LAST_QUERY_KEY] = value
    
    def add_chat_message(self, role: str, content: str, citations: Optional[List[str]] = None) -> None:
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
            "timestamp": self._get_current_timestamp()
        }
        st.session_state[self.CHAT_HISTORY_KEY].append(message)
        logger.debug(f"Mensaje agregado al chat: {role} - {content[:50]}...")
    
    def add_uploaded_file(self, file_info: Dict[str, Any]) -> None:
        """Agrega información de un archivo subido.
        
        Args:
            file_info: Diccionario con información del archivo.
        """
        st.session_state[self.UPLOADED_FILES_KEY].append(file_info)
        logger.info(f"Archivo subido: {file_info.get('name', 'desconocido')}")
    
    def remove_uploaded_file(self, file_id: str) -> bool:
        """Elimina un archivo subido por su ID.
        
        Args:
            file_id: ID del archivo a eliminar.
            
        Returns:
            True si se eliminó, False si no se encontró.
        """
        files = st.session_state.get(self.UPLOADED_FILES_KEY, [])
        for i, file_info in enumerate(files):
            if file_info.get("id") == file_id:
                del st.session_state[self.UPLOADED_FILES_KEY][i]
                logger.info(f"Archivo eliminado: {file_id}")
                return True
        return False
    
    def clear_uploaded_files(self) -> None:
        """Elimina todos los archivos subidos."""
        st.session_state[self.UPLOADED_FILES_KEY] = []
        logger.info("Todos los archivos subidos han sido eliminados")
    
    def clear_chat_history(self) -> None:
        """Elimina el historial de chat."""
        st.session_state[self.CHAT_HISTORY_KEY] = []
        logger.info("Historial de chat eliminado")
    
    def clear_all(self) -> None:
        """Elimina todo el estado de la sesión."""
        st.session_state[self.CHAT_HISTORY_KEY] = []
        st.session_state[self.UPLOADED_FILES_KEY] = []
        st.session_state[self.AGENT_STATE_KEY] = {}
        st.session_state[self.RECOMMENDATIONS_KEY] = []
        st.session_state[self.LAST_QUERY_KEY] = ""
        logger.info("Todo el estado de la sesión ha sido eliminado")
    
    def update_agent_state(self, key: str, value: Any) -> None:
        """Actualiza el estado del agente.
        
        Args:
            key: Clave del estado.
            value: Valor a establecer.
        """
        st.session_state[self.AGENT_STATE_KEY][key] = value
        logger.debug(f"Estado del agente actualizado: {key}")
    
    def get_agent_state(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor del estado del agente.
        
        Args:
            key: Clave del estado.
            default: Valor por defecto si no existe.
            
        Returns:
            El valor del estado o el valor por defecto.
        """
        return st.session_state.get(self.AGENT_STATE_KEY, {}).get(key, default)
    
    def _get_current_timestamp(self) -> str:
        """Obtiene el timestamp actual en formato legible.
        
        Returns:
            Timestamp en formato ISO.
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_session_info(self) -> Dict[str, Any]:
        """Obtiene toda la información de la sesión.
        
        Returns:
            Diccionario con toda la información de la sesión.
        """
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "chat_history_count": len(self.chat_history),
            "uploaded_files_count": len(self.uploaded_files),
            "agent_state": self.agent_state,
            "recommendations_count": len(self.recommendations),
            "last_query": self.last_query
        }


# Instancia global para fácil acceso
def get_session_manager() -> SessionManager:
    """Obtiene o crea una instancia del SessionManager.
    
    Returns:
        Instancia de SessionManager.
    """
    if "_session_manager" not in st.session_state:
        st.session_state["_session_manager"] = SessionManager()
    return st.session_state["_session_manager"]
