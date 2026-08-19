#!/usr/bin/env python3
"""
Financial Regulatory Copilot Chile - Recommendation Engine Component

Componente de Streamlit para mostrar y gestionar recomendaciones de documentos.
Integra con el DataRecommender del núcleo para sugerir documentos relevantes.
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Callable
import logging

# Configure logging
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Componente para mostrar y gestionar recomendaciones de documentos.
    
    Atributos:
        recommendations: Lista de recomendaciones actuales.
        on_document_select_callback: Callback para cuando se selecciona un documento.
    """
    
    def __init__(self, 
                 title: str = "📚 Documentos Recomendados",
                 max_recommendations: int = 10) -> None:
        """Inicializa el RecommendationEngine.
        
        Args:
            title: Título del componente.
            max_recommendations: Número máximo de recomendaciones a mostrar.
        """
        self.title = title
        self.max_recommendations = max_recommendations
        self._on_document_select_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self._recommender: Optional[Any] = None  # Será el DataRecommender del core
    
    def set_recommender(self, recommender: Any) -> None:
        """Establece el DataRecommender del núcleo.
        
        Args:
            recommender: Instancia de DataRecommender.
        """
        self._recommender = recommender
    
    def set_on_document_select_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Establece el callback para cuando se selecciona un documento.
        
        Args:
            callback: Función que recibe el documento seleccionado.
        """
        self._on_document_select_callback = callback
    
    def render(self) -> None:
        """Renderiza el componente de recomendaciones."""
        recommendations = self._get_recommendations()
        
        if not recommendations:
            self._render_empty_state()
            return
        
        # Contenedor principal
        with st.expander(self.title, expanded=True):
            self._render_recommendations(recommendations)
    
    def _get_recommendations(self) -> List[Dict[str, Any]]:
        """Obtiene las recomendaciones actuales.
        
        Returns:
            Lista de recomendaciones.
        """
        # Intentar obtener de session_state primero
        session_recommendations = st.session_state.get("financial_copilot_recommendations", [])
        
        if session_recommendations:
            return session_recommendations[:self.max_recommendations]
        
        # Si no hay en session_state, generar nuevas
        if self._recommender:
            try:
                last_query = st.session_state.get("financial_copilot_last_query", "")
                if last_query:
                    recommendations = self._recommender.recommend(last_query)
                    st.session_state["financial_copilot_recommendations"] = recommendations
                    return recommendations[:self.max_recommendations]
            except Exception as e:
                logger.error(f"Error obteniendo recomendaciones: {str(e)}")
        
        return []
    
    def _render_empty_state(self) -> None:
        """Renderiza el estado vacío (sin recomendaciones)."""
        st.info("💡 **Sugerencia:** Escribe una consulta para obtener recomendaciones de documentos relevantes.")
    
    def _render_recommendations(self, recommendations: List[Dict[str, Any]]) -> None:
        """Renderiza la lista de recomendaciones.
        
        Args:
            recommendations: Lista de recomendaciones a mostrar.
        """
        # Agrupar por categoría
        categories = {}
        for rec in recommendations:
            category = rec.get("category", "General")
            if category not in categories:
                categories[category] = []
            categories[category].append(rec)
        
        # Mostrar por categoría
        for category, recs in categories.items():
            with st.expander(f"📌 {category} ({len(recs)})", expanded=category == "Requeridos"):
                for rec in recs:
                    self._render_recommendation_item(rec)
    
    def _render_recommendation_item(self, recommendation: Dict[str, Any]) -> None:
        """Renderiza un elemento de recomendación individual.
        
        Args:
            recommendation: Diccionario con información de la recomendación.
        """
        cols = st.columns([3, 1, 1])
        
        with cols[0]:
            # Icono basado en prioridad
            priority_icon = self._get_priority_icon(recommendation)
            required_marker = " ❗" if recommendation.get("required", False) else ""
            
            st.write(f"{priority_icon} **{recommendation.get('name', 'Documento')}**{required_marker}")
            
            # Descripción
            description = recommendation.get("description", "")
            if description:
                st.caption(description[:200] + "..." if len(description) > 200 else description)
        
        with cols[1]:
            # Botón para cargar el documento
            if st.button("📥 Cargar", key=f"load_{recommendation.get('id', 'unknown')}"):
                if self._on_document_select_callback:
                    self._on_document_select_callback(recommendation)
                else:
                    st.info(f"Documento seleccionado: {recommendation.get('name')}")
        
        with cols[2]:
            # Botón de información
            if st.button("ℹ️", key=f"info_{recommendation.get('id', 'unknown')}"):
                self._show_recommendation_details(recommendation)
    
    def _get_priority_icon(self, recommendation: Dict[str, Any]) -> str:
        """Obtiene el icono basado en la prioridad.
        
        Args:
            recommendation: Diccionario con información de la recomendación.
            
        Returns:
            Icono representando la prioridad.
        """
        if recommendation.get("required", False):
            return "🔴"
        elif recommendation.get("priority", "medium") == "high":
            return "🟡"
        else:
            return "🟢"
    
    def _show_recommendation_details(self, recommendation: Dict[str, Any]) -> None:
        """Muestra los detalles de una recomendación.
        
        Args:
            recommendation: Diccionario con información de la recomendación.
        """
        with st.expander(f"Detalles: {recommendation.get('name', 'Documento')}", expanded=True):
            st.markdown(f"**Nombre:** {recommendation.get('name', 'N/A')}")
            st.markdown(f"**Categoría:** {recommendation.get('category', 'N/A')}")
            st.markdown(f"**Institución:** {recommendation.get('institution', 'N/A')}")
            
            if recommendation.get("description"):
                st.markdown(f"**Descripción:** {recommendation.get('description')}")
            
            if recommendation.get("url"):
                st.markdown(f"**Enlace:** [{recommendation.get('url')}]({recommendation.get('url')})")
            
            if recommendation.get("reference"):
                st.markdown(f"**Referencia:** {recommendation.get('reference')}")
            
            if recommendation.get("required", False):
                st.warning("⚠️ Este documento es **requerido** para responder adecuadamente a tu consulta.")
    
    def update_recommendations(self, query: str) -> List[Dict[str, Any]]:
        """Actualiza las recomendaciones basado en una consulta.
        
        Args:
            query: Consulta del usuario.
            
        Returns:
            Lista de recomendaciones generadas.
        """
        if not self._recommender:
            logger.warning("No hay DataRecommender configurado")
            return []
        
        try:
            recommendations = self._recommender.recommend(query)
            st.session_state["financial_copilot_recommendations"] = recommendations
            st.session_state["financial_copilot_last_query"] = query
            logger.info(f"Recomendaciones actualizadas para consulta: {query[:50]}...")
            return recommendations
        except Exception as e:
            logger.error(f"Error actualizando recomendaciones: {str(e)}")
            return []
    
    def clear_recommendations(self) -> None:
        """Limpia las recomendaciones actuales."""
        st.session_state["financial_copilot_recommendations"] = []
        logger.info("Recomendaciones limpiadas")
    
    def render_with_query_input(self) -> Optional[str]:
        """Renderiza el componente con un campo de entrada para consultas rápidas.
        
        Returns:
            La consulta ingresada si se envió, None en caso contrario.
        """
        query = st.text_input(
            "🔍 ¿Sobre qué tema necesitas recomendaciones?",
            key="recommendation_query_input",
            placeholder="Ej: NIIF 9, regulación bancaria, IVA..."
        )
        
        if query:
            if st.button("🔄 Obtener Recomendaciones", key="get_recommendations_btn"):
                recommendations = self.update_recommendations(query)
                st.session_state["financial_copilot_last_query"] = query
                st.rerun()
        
        self.render()
        return query


# Función conveniencia para uso directo
def create_recommendation_engine(title: str = "📚 Documentos Recomendados",
                                  max_recommendations: int = 10) -> RecommendationEngine:
    """Crea una instancia del RecommendationEngine.
    
    Args:
        title: Título del componente.
        max_recommendations: Número máximo de recomendaciones.
        
    Returns:
        Instancia de RecommendationEngine.
    """
    return RecommendationEngine(title, max_recommendations)
