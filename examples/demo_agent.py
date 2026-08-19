#!/usr/bin/env python3
"""
Financial Regulatory Copilot Chile - Demo del Agente Financiero

Script de demostración del uso directo del agente financiero sin Streamlit.
Muestra cómo cargar documentos, hacer consultas y obtener recomendaciones.
"""

import os
import sys

# Anadir el directorio raiz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent.financial_agent import FinancialAgent
from core.agent.knowledge_base import KnowledgeBase
from core.agent.data_recommender import DataRecommender


def demo_basica():
    """Demostracion basica del agente financiero."""
    print("=" * 60)
    print("DEMO: Financial Regulatory Copilot Chile")
    print("=" * 60)
    
    # Inicializar componentes
    print("\n1. Inicializando componentes...")
    kb = KnowledgeBase()
    recommender = DataRecommender()
    agent = FinancialAgent()
    
    # Configurar el agente
    agent.set_knowledge_base(kb)
    agent.set_recommender(recommender)
    
    print("   OK - KnowledgeBase creado")
    print("   OK - DataRecommender creado")
    print("   OK - FinancialAgent creado")
    
    # Cargar documentos base
    print("\n2. Cargando documentos base de conocimiento...")
    base_path = os.path.join("app", "data", "base")
    if os.path.exists(base_path):
        for filename in os.listdir(base_path):
            filepath = os.path.join(base_path, filename)
            if os.path.isfile(filepath):
                kb.add_document(filepath, user_uploaded=False)
                print(f"   OK - Cargado: {filename}")
    else:
        print("   ADVERTENCIA: Directorio app/data/base no encontrado")
    
    print(f"\n   Total documentos base: {len(kb.documents)}")
    
    # Mostrar estadisticas
    stats = agent.get_statistics()
    print("\n3. Estadisticas del agente:")
    print(f"   - Documentos cargados: {stats['knowledge_base']['total_documents']}")
    print(f"   - Patrones de recomendacion: {stats['recommender_patterns']}")
    
    # Hacer consultas de ejemplo
    print("\n4. Realizando consultas de ejemplo...")
    
    preguntas_ejemplo = [
        "Que dice la Ley General de Bancos sobre el capital minimo?",
        "Explica la NIIF 9",
        "Que es la CMF y que entidades fiscaliza?",
        "Cual es el encaje legal que deben mantener los bancos?"
    ]
    
    for i, pregunta in enumerate(preguntas_ejemplo, 1):
        print(f"\n   Pregunta {i}: {pregunta[:60]}...")
        respuesta = agent.respond(pregunta)
        
        # Mostrar respuesta resumida
        if isinstance(respuesta, dict):
            content = respuesta.get("content", "")
            citations = respuesta.get("citations", [])
            recommendations = respuesta.get("recommendations", [])
            
            # Mostrar primeros 200 caracteres de la respuesta
            print(f"   Respuesta: {content[:200]}...")
            
            # Mostrar recomendaciones
            if recommendations:
                print(f"   Recomendaciones ({len(recommendations)}):")
                for rec in recommendations[:3]:
                    required = " [REQUERIDO]" if rec.get("required", False) else ""
                    print(f"      - {rec.get('name', 'Documento')}{required}")
            
            # Mostrar citas
            if citations:
                print(f"   Fuentes: {', '.join(citations[:2])}")
        else:
            print(f"   Respuesta: {str(respuesta)[:200]}...")
    
    # Mostrar recomendaciones para una consulta
    print("\n5. Probando motor de recomendaciones...")
    consulta = "NIIF 9 instrumentos financieros"
    recomendaciones = recommender.recommend(consulta)
    print(f"   Consulta: {consulta}")
    print(f"   Documentos recomendados ({len(recomendaciones)}):")
    for i, rec in enumerate(recomendaciones[:5], 1):
        required = " [REQUERIDO]" if rec.get("required", False) else ""
        print(f"      {i}. {rec.get('name', 'Documento')}{required}")
        print(f"         Categoria: {rec.get('category', 'N/A')}")
        print(f"         Institucion: {rec.get('institution', 'N/A')}")
    
    # Mostrar categorias disponibles
    print("\n6. Categorias de recomendaciones disponibles:")
    categorias = recommender.get_categories()
    for i, cat in enumerate(categorias, 1):
        print(f"   {i}. {cat}")
    
    # Mostrar instituciones cubiertas
    print("\n7. Instituciones cubiertas:")
    instituciones = recommender.get_institutions()
    for i, inst in enumerate(instituciones, 1):
        print(f"   {i}. {inst}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETADA")
    print("=" * 60)


def demo_interactiva():
    """Demo interactiva donde el usuario puede hacer preguntas."""
    print("=" * 60)
    print("MODO INTERACTIVO: Financial Regulatory Copilot Chile")
    print("=" * 60)
    print("\nEscribe 'salir' para terminar")
    
    # Inicializar componentes
    kb = KnowledgeBase()
    recommender = DataRecommender()
    agent = FinancialAgent()
    
    agent.set_knowledge_base(kb)
    agent.set_recommender(recommender)
    
    # Cargar documentos base
    base_path = os.path.join("app", "data", "base")
    if os.path.exists(base_path):
        for filename in os.listdir(base_path):
            filepath = os.path.join(base_path, filename)
            if os.path.isfile(filepath):
                kb.add_document(filepath, user_uploaded=False)
    
    print(f"Documentos base cargados: {len(kb.documents)}")
    
    # Bucle de preguntas
    while True:
        try:
            pregunta = input("\nTu pregunta: ")
            
            if pregunta.lower() in ['salir', 'exit', 'quit']:
                print("\nHasta pronto!")
                break
            
            if not pregunta.strip():
                continue
            
            # Obtener respuesta
            respuesta = agent.respond(pregunta)
            
            if isinstance(respuesta, dict):
                content = respuesta.get("content", "")
                recommendations = respuesta.get("recommendations", [])
                citations = respuesta.get("citations", [])
                
                print("\nRespuesta:")
                print("-" * 60)
                print(content)
                print("-" * 60)
                
                if recommendations:
                    print("\nDocumentos Recomendados:")
                    for i, rec in enumerate(recommendations[:5], 1):
                        required = " [REQUERIDO]" if rec.get("required", False) else ""
                        print(f"   {i}. {rec.get('name', 'Documento')}{required}")
                        print(f"      Categoria: {rec.get('category', 'N/A')}")
                        print(f"      Institucion: {rec.get('institution', 'N/A')}")
                
                if citations:
                    print("\nFuentes:")
                    for i, cita in enumerate(citations[:5], 1):
                        print(f"   {i}. {cita}")
            else:
                print("\nRespuesta:", str(respuesta))
                
        except KeyboardInterrupt:
            print("\n\nHasta pronto!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Demo del Financial Regulatory Copilot Chile"
    )
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Modo interactivo para hacer preguntas"
    )
    parser.add_argument(
        "--query", 
        type=str,
        help="Consulta directa para probar"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        demo_interactiva()
    elif args.query:
        # Demo con consulta especifica
        kb = KnowledgeBase()
        recommender = DataRecommender()
        agent = FinancialAgent()
        agent.set_knowledge_base(kb)
        agent.set_recommender(recommender)
        
        # Cargar documentos base
        base_path = os.path.join("app", "data", "base")
        if os.path.exists(base_path):
            for filename in os.listdir(base_path):
                filepath = os.path.join(base_path, filename)
                if os.path.isfile(filepath):
                    kb.add_document(filepath, user_uploaded=False)
        
        respuesta = agent.respond(args.query)
        print(f"\nPregunta: {args.query}")
        print(f"Respuesta: {respuesta.get('content', respuesta)}")
        if isinstance(respuesta, dict) and respuesta.get("recommendations"):
            print(f"\nRecomendaciones: {[r['name'] for r in respuesta['recommendations'][:3]]}")
    else:
        demo_basica()
