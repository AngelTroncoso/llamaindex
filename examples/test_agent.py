#!/usr/bin/env python3
"""
Financial Regulatory Copilot Chile - Test del Agente Financiero

Script de prueba simplificado sin caracteres Unicode.
"""

import os
import sys

# Anadir el directorio raiz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent.financial_agent import FinancialAgent
from core.agent.knowledge_base import KnowledgeBase
from core.agent.data_recommender import DataRecommender


def main():
    """Test basico del agente financiero."""
    print("=" * 60)
    print("TEST: Financial Regulatory Copilot Chile")
    print("=" * 60)
    
    # Inicializar componentes
    print("\n1. Inicializando componentes...")
    kb = KnowledgeBase()
    recommender = DataRecommender()
    agent = FinancialAgent()
    
    # Configurar el agente
    agent.set_knowledge_base(kb)
    agent.set_recommender(recommender)
    
    print("   [OK] KnowledgeBase creado")
    print("   [OK] DataRecommender creado")
    print("   [OK] FinancialAgent creado")
    
    # Cargar documentos base
    print("\n2. Cargando documentos base de conocimiento...")
    base_path = os.path.join("app", "data", "base")
    if os.path.exists(base_path):
        for filename in os.listdir(base_path):
            filepath = os.path.join(base_path, filename)
            if os.path.isfile(filepath):
                kb.add_document(filepath, user_uploaded=False)
                print(f"   [OK] Cargado: {filename}")
    else:
        print("   [ADVERTENCIA] Directorio app/data/base no encontrado")
    
    print(f"\n   Total documentos base: {len(kb.documents)}")
    
    # Mostrar estadisticas
    stats = agent.get_statistics()
    print("\n3. Estadisticas del agente:")
    print(f"   - Documentos cargados: {stats['knowledge_base']['total_documents']}")
    print(f"   - Patrones de recomendacion: {stats['recommender_patterns']}")
    
    # Hacer consultas de ejemplo
    print("\n4. Realizando consultas de ejemplo...")
    
    preguntas_ejemplo = [
        "Que dice la Ley General de Bancos sobre el capital minimo",
        "Explica la NIIF 9",
        "Que es la CMF",
    ]
    
    for i, pregunta in enumerate(preguntas_ejemplo, 1):
        print(f"\n   Pregunta {i}: {pregunta[:50]}...")
        respuesta = agent.respond(pregunta)
        
        # Mostrar respuesta resumida
        if isinstance(respuesta, dict):
            content = respuesta.get("content", "")
            recommendations = respuesta.get("recommendations", [])
            
            # Mostrar primeros 150 caracteres de la respuesta
            print(f"   Respuesta: {content[:150].encode('ascii', 'ignore').decode('ascii')}...")
            
            # Mostrar recomendaciones
            if recommendations:
                print(f"   Recomendaciones ({len(recommendations)}):")
                for rec in recommendations[:3]:
                    required = " [REQUERIDO]" if rec.get("required", False) else ""
                    name = rec.get('name', 'Documento')
                    print(f"      - {name.encode('ascii', 'ignore').decode('ascii')}{required}")
    
    # Mostrar categorias disponibles
    print("\n5. Categorias de recomendaciones disponibles:")
    categorias = recommender.get_categories()
    for i, cat in enumerate(categorias, 1):
        print(f"   {i}. {cat.encode('ascii', 'ignore').decode('ascii')}")
    
    # Mostrar instituciones cubiertas
    print("\n6. Instituciones cubiertas:")
    instituciones = recommender.get_institutions()
    for i, inst in enumerate(instituciones, 1):
        print(f"   {i}. {inst.encode('ascii', 'ignore').decode('ascii')}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
    print("\nPara ejecutar la aplicacion Streamlit:")
    print("  python -m streamlit run app/main.py")


if __name__ == "__main__":
    main()
