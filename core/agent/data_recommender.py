#!/usr/bin/env python3
"""
Financial Regulatory Copilot Chile - Data Recommender

Motor de recomendación de documentos basado en patrones de consulta.
Sugiere documentos relevantes según la consulta del usuario.
"""

from typing import Dict, List, Optional, Any
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)


class DataRecommender:
    """Motor de recomendación de documentos.
    
    Atributos:
        patterns: Lista de patrones de recomendación.
    """
    
    def __init__(self) -> None:
        """Inicializa el DataRecommender."""
        self.patterns = self._load_recommendation_patterns()
        logger.info(f"DataRecommender inicializado con {len(self.patterns)} patrones")
    
    def recommend(self, query: str, max_recommendations: int = 10) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en una consulta.
        
        Args:
            query: Consulta del usuario.
            max_recommendations: Número máximo de recomendaciones a devolver.
            
        Returns:
            Lista de recomendaciones ordenadas por relevancia.
        """
        try:
            query_lower = query.lower()
            recommendations = []
            
            # Buscar patrones coincidentes
            for pattern in self.patterns:
                if re.search(pattern.get("regex", ""), query_lower):
                    # Crear recomendaciones para este patrón
                    for suggestion in pattern.get("suggests", []):
                        # Determinar si es requerido
                        is_required = pattern.get("required", False)
                        
                        recommendation = {
                            "id": f"{pattern['id']}_{suggestion}",
                            "name": suggestion,
                            "category": pattern.get("category", "General"),
                            "institution": pattern.get("institution", ""),
                            "description": pattern.get("description", ""),
                            "reference": pattern.get("reference", ""),
                            "url": pattern.get("url", ""),
                            "required": is_required,
                            "priority": "high" if is_required else "medium",
                            "score": 1.0 if is_required else 0.8
                        }
                        recommendations.append(recommendation)
            
            # Deduplicar recomendaciones
            unique_recommendations = []
            seen_names = set()
            for rec in recommendations:
                if rec["name"] not in seen_names:
                    seen_names.add(rec["name"])
                    unique_recommendations.append(rec)
            
            # Ordenar: requeridos primero, luego por score
            unique_recommendations.sort(key=lambda x: (0 if x["required"] else 1, -x["score"]))
            
            # Limitar a max_recommendations
            return unique_recommendations[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {str(e)}")
            return []
    
    def _load_recommendation_patterns(self) -> List[Dict[str, Any]]:
        """Carga los patrones de recomendación.
        
        Returns:
            Lista de patrones.
        """
        # Patrones de recomendación para normativa chilena
        patterns = [
            # BCCh - Banco Central de Chile
            {
                "id": "bch_general",
                "regex": r"banco central|bch|política monetaria|encaje|liquidez|sistemas de pagos",
                "suggests": ["CNF (Compendio de Normas Financieras)", "CNMF (Compendio de Normas Monetarias)", "Informe de Política Monetaria"],
                "category": "Banco Central de Chile",
                "institution": "BCCh",
                "description": "Documentos normativos del Banco Central de Chile",
                "required": False
            },
            
            # CMF - Comisión para el Mercado Financiero
            {
                "id": "cmf_general",
                "regex": r"cmf|mercado financiero|superintendencia|normativa financiera|bancos|valores|seguros",
                "suggests": ["NCG (Normas de Carácter General)", "Circulares CMF", "Oficios CMF"],
                "category": "CMF",
                "institution": "CMF",
                "description": "Normativa de la Comisión para el Mercado Financiero",
                "required": False
            },
            
            # Ley General de Bancos
            {
                "id": "lgb",
                "regex": r"lgb|ley general de bancos|bancos|solvencia|capital|gestión de riesgos",
                "suggests": ["Ley General de Bancos (DFL N°3)"],
                "category": "Normas Fundamentales",
                "institution": "BCCh/CMF",
                "description": "Ley que regula el sistema bancario chileno",
                "reference": "DFL N°3",
                "required": True
            },
            
            # Ley de Mercado de Valores
            {
                "id": "ley_18045",
                "regex": r"ley 18.045|ley de mercado de valores|valores|emisión|oferta pública|intermediarios",
                "suggests": ["Ley de Mercado de Valores (Ley N° 18.045)"],
                "category": "Normas Fundamentales",
                "institution": "CMF",
                "description": "Normativa sobre emisión y oferta pública de valores",
                "reference": "Ley N° 18.045",
                "required": True
            },
            
            # Ley de Sociedades Anónimas
            {
                "id": "ley_18046",
                "regex": r"ley 18.046|ley de sociedades anónimas|sociedades|gobierno corporativo|estados financieros",
                "suggests": ["Ley de Sociedades Anónimas (Ley N° 18.046)"],
                "category": "Normas Fundamentales",
                "institution": "CMF",
                "description": "Normativa sobre sociedades anónimas y gobierno corporativo",
                "reference": "Ley N° 18.046",
                "required": True
            },
            
            # NIIF/IFRS
            {
                "id": "niif_9",
                "regex": r"niif 9|ifrs 9|instrumentos financieros|clasificación|medición|deterioro",
                "suggests": ["NIIF 9: Instrumentos Financieros"],
                "category": "Estándares Contables",
                "institution": "IFRS/CMF",
                "description": "Normativa sobre clasificación, medición y deterioro de instrumentos financieros",
                "reference": "NIIF 9",
                "required": True
            },
            
            {
                "id": "niif_16",
                "regex": r"niif 16|ifrs 16|arrendamientos|arrendador|arrendatario",
                "suggests": ["NIIF 16: Arrendamientos", "Guía de Arrendamientos CMF"],
                "category": "Estándares Contables",
                "institution": "IFRS/CMF",
                "description": "Normativa sobre contabilización de arrendamientos",
                "reference": "NIIF 16",
                "required": True
            },
            
            {
                "id": "niif_7",
                "regex": r"niif 7|ifrs 7|revelaciones|riesgos|exposición a mercado",
                "suggests": ["NIIF 7: Información a Revelar sobre Instrumentos Financieros"],
                "category": "Estándares Contables",
                "institution": "IFRS/CMF",
                "description": "Normativa sobre revelaciones de riesgos financieros",
                "reference": "NIIF 7",
                "required": False
            },
            
            {
                "id": "niif_13",
                "regex": r"niif 13|ifrs 13|valor razonable|valoración|técnicas de valoración",
                "suggests": ["NIIF 13: Medición del Valor Razonable"],
                "category": "Estándares Contables",
                "institution": "IFRS/CMF",
                "description": "Normativa sobre medición del valor razonable",
                "reference": "NIIF 13",
                "required": False
            },
            
            {
                "id": "niif_15",
                "regex": r"niif 15|ifrs 15|ingresos|reconocimiento|medición|presentación",
                "suggests": ["NIIF 15: Ingresos de Actividades Ordinarias"],
                "category": "Estándares Contables",
                "institution": "IFRS/CMF",
                "description": "Normativa sobre reconocimiento y medición de ingresos",
                "reference": "NIIF 15",
                "required": False
            },
            
            # NIC - Normas Internacionales de Contabilidad
            {
                "id": "nic_1",
                "regex": r"nic 1|ias 1|presentación de estados financieros|estructura|presentación",
                "suggests": ["NIC 1: Presentación de Estados Financieros"],
                "category": "Estándares Contables",
                "institution": "IASB/CMF",
                "description": "Normativa sobre presentación de estados financieros",
                "reference": "NIC 1",
                "required": False
            },
            
            {
                "id": "nic_7",
                "regex": r"nic 7|ias 7|estado de flujos de efectivo|clasificación de flujos",
                "suggests": ["NIC 7: Estado de Flujos de Efectivo"],
                "category": "Estándares Contables",
                "institution": "IASB/CMF",
                "description": "Normativa sobre preparación del estado de flujos de efectivo",
                "reference": "NIC 7",
                "required": False
            },
            
            {
                "id": "nic_21",
                "regex": r"nic 21|ias 21|efectos de variaciones|tasas de cambio|moneda extranjera",
                "suggests": ["NIC 21: Efectos de las Variaciones en las Tasas de Cambio"],
                "category": "Estándares Contables",
                "institution": "IASB/CMF",
                "description": "Normativa sobre conversión de moneda extranjera",
                "reference": "NIC 21",
                "required": False
            },
            
            # SII - Servicio de Impuestos Internos
            {
                "id": "sii_iva",
                "regex": r"sii|impuestos|iva|impuesto al valor agregado|declaración",
                "suggests": ["Ley sobre Impuesto a las Ventas y Servicios", "Circulares SII sobre IVA"],
                "category": "Tributación",
                "institution": "SII",
                "description": "Normativa tributaria sobre IVA",
                "required": False
            },
            
            {
                "id": "sii_renta",
                "regex": r"impuesto a la renta|ley de renta|renta|impuestos final",
                "suggests": ["Ley sobre Impuesto a la Renta", "Circulares SII sobre Renta"],
                "category": "Tributación",
                "institution": "SII",
                "description": "Normativa tributaria sobre impuesto a la renta",
                "required": False
            },
            
            # Análisis de documentos
            {
                "id": "document_analysis",
                "regex": r"analizar|revisar|contrato|estados financieros|informe|documento",
                "suggests": ["Documentos del usuario"],
                "category": "Documentos del Usuario",
                "institution": "Usuario",
                "description": "Analizar documentos cargados por el usuario",
                "required": True
            },
            
            # Comparaciones
            {
                "id": "comparison",
                "regex": r"comparar|diferencias|versiones|evolución|cambios",
                "suggests": ["Comparación de normativas", "Historial de versiones"],
                "category": "Comparaciones",
                "institution": "General",
                "description": "Comparación entre normativas o versiones de documentos",
                "required": False
            },
            
            # Categorías generales
            {
                "id": "general_regulation",
                "regex": r"normativa|regulación|ley|decreto|resolución",
                "suggests": ["Ley General de Bancos", "Ley de Mercado de Valores", "Ley de Sociedades Anónimas"],
                "category": "Normas Fundamentales",
                "institution": "General",
                "description": "Documentos normativos generales",
                "required": False
            },
            
            # Fallback para consultas generales
            {
                "id": "fallback",
                "regex": r".*",
                "suggests": ["CNF (BCCh)", "CNMF (BCCh)", "NCG (CMF)", "Ley General de Bancos"],
                "category": "General",
                "institution": "General",
                "description": "Documentos de referencia general",
                "required": False
            }
        ]
        
        return patterns
    
    def get_pattern_count(self) -> int:
        """Obtiene el número de patrones cargados.
        
        Returns:
            Número de patrones.
        """
        return len(self.patterns)
    
    def get_categories(self) -> List[str]:
        """Obtiene la lista de categorías disponibles.
        
        Returns:
            Lista de categorías.
        """
        categories = set()
        for pattern in self.patterns:
            categories.add(pattern.get("category", "General"))
        return sorted(list(categories))
    
    def get_institutions(self) -> List[str]:
        """Obtiene la lista de instituciones cubiertas.
        
        Returns:
            Lista de instituciones.
        """
        institutions = set()
        for pattern in self.patterns:
            if pattern.get("institution"):
                institutions.add(pattern["institution"])
        return sorted(list(institutions))
