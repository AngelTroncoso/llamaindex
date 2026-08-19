#!/usr/bin/env python3
"""
Financial Regulatory Copilot Chile - Financial Agent

Agente principal que orquesta la lógica de negocio.
Integra la base de conocimiento, el motor de recomendaciones y el LLM.
"""

from typing import Dict, List, Optional, Any
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)


class FinancialAgent:
    """Agente financiero principal de la aplicación.
    
    Atributos:
        knowledge_base: Base de conocimiento asociada.
        recommender: Motor de recomendaciones.
        llm_config: Configuración del modelo de lenguaje.
    """
    
    # Prompts del sistema
    SYSTEM_PROMPTS = {
        "default": """
        Eres un asistente de IA especializado en normativa financiera chilena. 
        Tu conocimiento abarca:
        - Normativa del Banco Central de Chile (BCCh): CNF, CNMF, política monetaria
        - Normativa de la Comisión para el Mercado Financiero (CMF): NCG, circulares, bancos, valores, seguros
        - Normativa del Servicio de Impuestos Internos (SII): IVA, renta, declaraciones
        - Estándares contables: NIIF/IFRS (9, 7, 13, 15, 16), NIC (1, 7, 21)
        - Ley General de Bancos (DFL N°3)
        - Ley de Mercado de Valores (Ley N° 18.045)
        - Ley de Sociedades Anónimas (Ley N° 18.046)
        
        Responde en español de Chile, con precisión técnica y siempre cita las fuentes.
        Si no conoces la respuesta, di que no la sabes en lugar de inventar información.
        """,
        
        "legal": """
        Eres un experto en normativa legal financiera chilena. 
        Tu conocimiento está enfocado en:
        - Leyes y decretos con fuerza de ley
        - Reglamentos y normas de carácter general
        - Circulares y oficios normativos
        - Jurisprudencia relevante
        
        Responde con precisión jurídica, citando siempre el número de la norma y el articulo específico.
        Si hay ambigüedad, indica las posibles interpretaciones.
        """,
        
        "niif": """
        Eres un experto en estándares contables internacionales (NIIF/IFRS) aplicables en Chile.
        Tu conocimiento abarca:
        - NIIF 9: Instrumentos Financieros
        - NIIF 7: Información a Revelar
        - NIIF 13: Valor Razonable
        - NIIF 15: Ingresos
        - NIIF 16: Arrendamientos
        - NIC 1: Presentación de Estados Financieros
        - NIC 7: Estado de Flujos de Efectivo
        - NIC 21: Variaciones en Tasas de Cambio
        
        Explica la aplicación en el contexto chileno, considerando las adaptaciones y guías de la CMF.
        """,
        
        "analysis": """
        Eres un analista financiero especializado en normativa chilena.
        Tu tarea es:
        - Analizar documentos financieros
        - Identificar cumplimiento normativo
        - Señalar posibles incumplimientos
        - Sugerir mejoras
        
        Proporciona análisis detallados con referencias a las normas aplicables.
        """
    }
    
    def __init__(self) -> None:
        """Inicializa el FinancialAgent."""
        self.knowledge_base = None
        self.recommender = None
        self.llm_config = {
            "provider": "ollama",
            "model": "llama3.2:70b"
        }
        self.chat_history: List[Dict[str, Any]] = []
        logger.info("FinancialAgent inicializado")
    
    def set_knowledge_base(self, kb) -> None:
        """Establece la base de conocimiento.
        
        Args:
            kb: Instancia de KnowledgeBase.
        """
        self.knowledge_base = kb
        logger.info("KnowledgeBase asociada al agente")
    
    def set_recommender(self, recommender) -> None:
        """Establece el motor de recomendaciones.
        
        Args:
            recommender: Instancia de DataRecommender.
        """
        self.recommender = recommender
        logger.info("DataRecommender asociado al agente")
    
    def set_llm_config(self, provider: str, model: str) -> None:
        """Configura el modelo de lenguaje.
        
        Args:
            provider: Proveedor (ollama, openai).
            model: Nombre del modelo.
        """
        self.llm_config = {
            "provider": provider,
            "model": model
        }
        logger.info(f"LLM configurado: {provider} - {model}")
    
    def respond(self, query: str) -> Dict[str, Any]:
        """Genera una respuesta a una consulta.
        
        Args:
            query: Consulta del usuario.
            
        Returns:
            Diccionario con la respuesta y metadatos.
        """
        try:
            logger.info(f"Procesando consulta: {query[:50]}...")
            
            # Determinar el tipo de consulta para seleccionar el prompt
            prompt_type = self._determine_prompt_type(query)
            system_prompt = self.SYSTEM_PROMPTS.get(prompt_type, self.SYSTEM_PROMPTS["default"])
            
            # Obtener recomendaciones
            recommendations = []
            if self.recommender:
                recommendations = self.recommender.recommend(query)
            
            # Buscar en la base de conocimiento
            search_results = []
            if self.knowledge_base:
                search_results = self.knowledge_base.query_index(query)
            
            # Generar respuesta (simulación mínima sin LLM real)
            response = self._generate_response(query, recommendations, search_results, system_prompt)
            
            # Agregar a historial
            self.chat_history.append({
                "query": query,
                "response": response,
                "timestamp": self._get_current_timestamp()
            })
            
            return {
                "content": response,
                "citations": self._extract_citations(recommendations, search_results),
                "recommendations": recommendations,
                "sources": search_results
            }
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return {
                "content": f"Lo siento, ocurrió un error al procesar tu consulta: {str(e)}",
                "citations": [],
                "recommendations": [],
                "sources": []
            }
    
    def chat(self, message: str) -> Dict[str, Any]:
        """Maneja una conversación (con historial).
        
        Args:
            message: Mensaje del usuario.
            
        Returns:
            Diccionario con la respuesta y metadatos.
        """
        # Por ahora, respond es suficiente
        return self.respond(message)
    
    def add_user_document(self, file_path: str) -> Optional[str]:
        """Agrega un documento del usuario.
        
        Args:
            file_path: Ruta al archivo.
            
        Returns:
            ID del documento o None si hay error.
        """
        if self.knowledge_base:
            return self.knowledge_base.add_document(file_path, user_uploaded=True)
        return None
    
    def add_user_document_from_bytes(self, file_path: str, file_name: str) -> Optional[str]:
        """Agrega un documento del usuario desde bytes.
        
        Args:
            file_path: Ruta temporal del archivo.
            file_name: Nombre original del archivo.
            
        Returns:
            ID del documento o None si hay error.
        """
        if self.knowledge_base:
            return self.knowledge_base.add_document_from_bytes(file_path, file_name, user_uploaded=True)
        return None
    
    def clear_user_documents(self) -> None:
        """Elimina todos los documentos del usuario."""
        if self.knowledge_base:
            self.knowledge_base.clear_user_documents()
    
    def clear_all(self) -> None:
        """Elimina todo el estado del agente."""
        self.chat_history = []
        if self.knowledge_base:
            self.knowledge_base.clear_all()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del agente.
        
        Returns:
            Diccionario con estadísticas.
        """
        kb_stats = {}
        if self.knowledge_base:
            kb_stats = self.knowledge_base.get_statistics()
        
        return {
            "chat_history_count": len(self.chat_history),
            "knowledge_base": kb_stats,
            "recommender_patterns": self.recommender.get_pattern_count() if self.recommender else 0
        }
    
    def _determine_prompt_type(self, query: str) -> str:
        """Determina el tipo de prompt según la consulta.
        
        Args:
            query: Consulta del usuario.
            
        Returns:
            Tipo de prompt (default, legal, niif, analysis).
        """
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["niif", "ifrs", "nic", "ias", "contable", "contabilidad"]):
            return "niif"
        elif any(word in query_lower for word in ["ley", "artículo", "decreto", "reglamento", "jurídico", "legal"]):
            return "legal"
        elif any(word in query_lower for word in ["analizar", "revisar", "contrato", "estados financieros", "informe"]):
            return "analysis"
        else:
            return "default"
    
    def _generate_response(self, query: str, recommendations: List[Dict[str, Any]], 
                          search_results: List[Dict[str, Any]], 
                          system_prompt: str) -> str:
        """Genera una respuesta basada en la consulta y los resultados.
        
        Args:
            query: Consulta del usuario.
            recommendations: Lista de recomendaciones.
            search_results: Resultados de búsqueda.
            system_prompt: Prompt del sistema.
            
        Returns:
            Respuesta generada.
        """
        # Esta es una implementación mínima sin LLM real
        # En producción, aquí se integraría con LlamaIndex o el proveedor de LLM
        
        response_parts = []
        
        # Agregar contexto del prompt
        response_parts.append("Según mi conocimiento sobre normativa financiera chilena:")
        
        # Agregar información de los resultados de búsqueda
        if search_results:
            response_parts.append("\n\nEncontré información relevante en los siguientes documentos:")
            for i, result in enumerate(search_results[:3], 1):
                response_parts.append(f"\n{i}. {result.get('name', 'Documento')}: {result.get('content', '')[:200]}...")
        
        # Agregar recomendaciones
        if recommendations:
            required_docs = [r for r in recommendations if r.get("required", False)]
            if required_docs:
                response_parts.append("\n\n📚 **Documentos requeridos para responder adecuadamente:**")
                for doc in required_docs:
                    response_parts.append(f"\n- {doc.get('name', 'Documento')} ({doc.get('reference', '')})")
            
            suggested_docs = [r for r in recommendations if not r.get("required", False)]
            if suggested_docs:
                response_parts.append("\n\n💡 **Documentos sugeridos:**")
                for doc in suggested_docs[:3]:
                    response_parts.append(f"\n- {doc.get('name', 'Documento')}")
        
        # Respuesta específica según la consulta
        response_parts.append(self._generate_specific_response(query))
        
        return "".join(response_parts)
    
    def _generate_specific_response(self, query: str) -> str:
        """Genera una respuesta específica basada en palabras clave.
        
        Args:
            query: Consulta del usuario.
            
        Returns:
            Respuesta específica.
        """
        query_lower = query.lower()
        
        # Respuestas basadas en palabras clave
        if any(word in query_lower for word in ["niif 9", "instrumentos financieros"]):
            return """

La NIIF 9 establece los principios para la clasificación, medición, deterioro y revelación de instrumentos financieros. 
En Chile, su aplicación es obligatoria y está regulada por la CMF a través de sus Normas de Carácter General.

Principales aspectos:
- Clasificación en 3 categorías: a valor razonable con cambios en resultados, a valor razonable con cambios en otro resultado integral, y a costo amortizado
- Modelo de pérdida crediticia esperada para deterioro
- Revelaciones mejoradas"""
        
        elif any(word in query_lower for word in ["lgb", "ley general de bancos"]):
            return """

La Ley General de Bancos (DFL N°3) es la normativa principal que regula el sistema bancario en Chile. 
Establece requisitos de solvencia, capital mínimo, gestión de riesgos y supervisión.

El Banco Central de Chile y la CMF son las entidades encargadas de su aplicación y fiscalización."""
        
        elif any(word in query_lower for word in ["cmf", "comisión para el mercado financiero"]):
            return """

La Comisión para el Mercado Financiero (CMF) es el organismo regulador de los mercados financieros en Chile. 
Supervisa bancos, instituciones financieras, Mercado de Valores, seguros, y otras entidades fiscalizadas.

Sus principales funciones incluyen la regulación, supervisión y fiscalización del cumplimiento de las normas."""
        
        elif any(word in query_lower for word in ["bch", "banco central"]):
            return """

El Banco Central de Chile (BCCh) es una entidad autónoma con rango constitucional. 
Sus funciones principales incluyen:
- Mantener la estabilidad de la moneda
- Regular la cantidad de dinero y de crédito
- Dictar normas de carácter general para el sistema financiero
- Administrar las reservas internacionales"""
        
        elif any(word in query_lower for word in ["iva", "impuesto al valor agregado"]):
            return """

El Impuesto al Valor Agregado (IVA) en Chile está regulado por el DL 825 de 1974.
La tasa general es del 19%, con algunas excepciones y exenciones.

El Servicio de Impuestos Internos (SII) es la entidad encargada de su administración y fiscalización."""
        
        else:
            return f"\n\nHe entendido tu consulta sobre: {query}. Para darte una respuesta más precisa, te recomiendo revisar los documentos sugeridos."
    
    def _extract_citations(self, recommendations: List[Dict[str, Any]], 
                          search_results: List[Dict[str, Any]]) -> List[str]:
        """Extrae las citas de los resultados.
        
        Args:
            recommendations: Lista de recomendaciones.
            search_results: Resultados de búsqueda.
            
        Returns:
            Lista de citas formateadas.
        """
        citations = []
        
        # Agregar referencias de recomendaciones
        for rec in recommendations:
            if rec.get("reference"):
                citations.append(f"{rec.get('name', 'Documento')} ({rec.get('reference')})")
        
        # Agregar referencias de búsqueda
        for result in search_results:
            citations.append(f"Documento: {result.get('name', 'Desconocido')}")
        
        return citations[:10]  # Limitar a 10 citas
    
    def _get_current_timestamp(self) -> str:
        """Obtiene el timestamp actual.
        
        Returns:
            Timestamp en formato ISO.
        """
        from datetime import datetime
        return datetime.now().isoformat()
