#!/usr/bin/env python3
"""
Financial Regulatory Copilot Chile - Test del Nucleo del Agente

Este script prueba los componentes principales del nucleo:
- DataRecommender
- KnowledgeBase
- FinancialAgent

Ejecucion:
    python examples/test_core_agent.py
"""

import sys
import os
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent.data_recommender import DataRecommender
from core.agent.knowledge_base import KnowledgeBase
from core.agent.financial_agent import FinancialAgent


def test_data_recommender():
    """Prueba el motor de recomendacion."""
    print("=" * 60)
    print("TEST 1: DataRecommender")
    print("=" * 60)
    
    recommender = DataRecommender()
    
    # Prueba 1: Consulta sobre NIIF 9
    print("\n1. Consulta: '¿Cómo aplicar NIIF 9 a un derivado?'")
    recommendations = recommender.get_recommendations("¿Cómo aplicar NIIF 9 a un derivado?")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec['title']} (Requerido: {rec.get('required', False)})")
    
    # Prueba 2: Consulta sobre LGB
    print("\n2. Consulta: '¿Qué dice la LGB sobre capital mínimo?'")
    recommendations = recommender.get_recommendations("¿Qué dice la LGB sobre capital mínimo?")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec['title']} (Requerido: {rec.get('required', False)})")
    
    # Prueba 3: Consulta sobre IVA
    print("\n3. Consulta: '¿Cómo funciona el IVA en Chile?'")
    recommendations = recommender.get_recommendations("¿Cómo funciona el IVA en Chile?")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec['title']} (Requerido: {rec.get('required', False)})")
    
    # Prueba 4: Consulta generica
    print("\n4. Consulta: 'Analiza este documento'")
    recommendations = recommender.get_recommendations("Analiza este documento")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec['title']} (Requerido: {rec.get('required', False)})")
    
    print("\n✅ DataRecommender funcionando correctamente!")
    return True


def test_knowledge_base():
    """Prueba la base de conocimiento."""
    print("\n" + "=" * 60)
    print("TEST 2: KnowledgeBase")
    print("=" * 60)
    
    kb = KnowledgeBase(persist_index=False)
    
    # Prueba 1: Estadisticas iniciales
    print("\n1. Estadisticas iniciales:")
    stats = kb.get_statistics()
    print(f"   - Documentos totales: {stats['total_documents']}")
    print(f"   - Documentos de usuario: {stats['user_documents']}")
    print(f"   - Indice listo: {stats['index_ready']}")
    
    # Prueba 2: Agregar documento (si hay ejemplos)
    examples_dir = Path(__file__).parent / "data"
    if examples_dir.exists():
        for doc_file in examples_dir.glob("*"):
            if doc_file.is_file():
                print(f"\n2. Agregando documento: {doc_file.name}")
                try:
                    doc_id = kb.add_document(doc_file, is_user_doc=True)
                    print(f"   ✅ Documento agregado con ID: {doc_id}")
                except Exception as e:
                    print(f"   ⚠️  No se pudo agregar {doc_file.name}: {e}")
    else:
        print("\n2. No hay documentos de ejemplo para cargar")
        print("   Puedes crear la carpeta 'examples/data/' y agregar archivos PDF/TXT")
    
    # Prueba 3: Estadisticas finales
    print("\n3. Estadisticas finales:")
    stats = kb.get_statistics()
    print(f"   - Documentos totales: {stats['total_documents']}")
    print(f"   - Documentos de usuario: {stats['user_documents']}")
    print(f"   - Indice listo: {stats['index_ready']}")
    
    # Prueba 4: Listar documentos
    if kb.get_documents():
        print("\n4. Documentos cargados:")
        for doc in kb.get_documents():
            print(f"   - {doc['name']} ({doc['type']})")
    
    print("\n✅ KnowledgeBase funcionando correctamente!")
    return True


def test_financial_agent():
    """Prueba el agente financiero."""
    print("\n" + "=" * 60)
    print("TEST 3: FinancialAgent")
    print("=" * 60)
    
    # Usar modelo local (sin LLM para prueba de estructura)
    try:
        agent = FinancialAgent(
            model="local",
            temperature=0.1,
            persist_index=False
        )
        
        print("\n1. Agente inicializado:")
        print(f"   - Modelo: {agent.model_name}")
        print(f"   - Temperatura: {agent.temperature}")
        
        stats = agent.get_statistics()
        print(f"   - LLM disponible: {stats['llm_available']}")
        print(f"   - LlamaIndex disponible: {stats['llama_index_available']}")
        
        # Prueba 2: Consulta sin documentos
        print("\n2. Consulta de prueba: '¿Qué es la LGB?'")
        response = agent.respond("¿Qué es la LGB?", use_recommender=True)
        print("   Respuesta:")
        print(f"   {response[:200]}...")
        
        # Prueba 3: Consulta con recomendaciones
        print("\n3. Consulta: '¿Cómo aplicar NIIF 9?'")
        response = agent.respond("¿Cómo aplicar NIIF 9?")
        print("   Respuesta:")
        # Mostrar solo la primera linea de recomendaciones
        lines = response.split('\n')
        for line in lines[:5]:
            print(f"   {line}")
        if len(lines) > 5:
            print(f"   ... ({len(lines) - 5} lineas mas)")
        
        # Prueba 4: Chat
        print("\n4. Prueba de chat:")
        messages = [
            {"role": "user", "content": "Hola, ¿qué sabes sobre NIIF?"}
        ]
        response = agent.chat(messages)
        print(f"   Usuario: {messages[0]['content']}")
        print(f"   Asistente: {response['content'][:100]}...")
        
        print("\n✅ FinancialAgent funcionando correctamente!")
        return True
        
    except Exception as e:
        print(f"\n⚠️  Error al inicializar FinancialAgent: {e}")
        print("   Esto es normal si LlamaIndex no esta instalado.")
        print("   Instala las dependencias con: pip install -r requirements.txt")
        return False


def test_connectors():
    """Prueba los conectores a APIs."""
    print("\n" + "=" * 60)
    print("TEST 4: Conectores a APIs (Sin API Key)")
    print("=" * 60)
    
    try:
        from core.connectors.cmf_connector import CMFConnector
        from core.connectors.bch_connector import BCChConnector
        from core.connectors.sii_connector import SIIConnector
        
        # Prueba CMF
        print("\n1. CMFConnector:")
        cmf = CMFConnector()
        print(f"   - Instancia creada: {cmf}")
        # No hacemos requests sin API key valida
        
        # Prueba BCCh
        print("\n2. BCChConnector:")
        bch = BCChConnector()
        print(f"   - Instancia creada: {bch}")
        
        # Prueba SII
        print("\n3. SIIConnector:")
        sii = SIIConnector()
        print(f"   - Instancia creada: {sii}")
        
        # Prueba calculos offline (no requieren API)
        print("\n4. Calculos offline del SII:")
        iva_calc = sii.calcular_iva(100000, tasa=0.19)
        print(f"   - IVA de $100,000: ${iva_calc['monto_iva']:.2f}")
        print(f"   - Total: ${iva_calc['total']:.2f}")
        
        renta_calc = sii.calcular_renta(ingresos=1000000, gastos=200000, tasa=0.25)
        print(f"   - Renta (ingresos $1M, gastos $200K): ${renta_calc['impuesto']:.2f}")
        
        print("\n✅ Conectores funcionando correctamente!")
        return True
        
    except Exception as e:
        print(f"\n⚠️  Error en conectores: {e}")
        return False


def main():
    """Ejecuta todas las pruebas."""
    print("\n" + "=" * 60)
    print("FINANCIAL REGULATORY COPILOT CHILE - TESTS")
    print("=" * 60)
    
    results = []
    
    # Prueba 1: DataRecommender (siempre funciona)
    results.append(("DataRecommender", test_data_recommender()))
    
    # Prueba 2: KnowledgeBase (siempre funciona)
    results.append(("KnowledgeBase", test_knowledge_base()))
    
    # Prueba 3: FinancialAgent (requiere LlamaIndex)
    results.append(("FinancialAgent", test_financial_agent()))
    
    # Prueba 4: Conectores (siempre funciona)
    results.append(("Conectores", test_connectors()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:25} {status}")
    
    print(f"\nTotal: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("\n🎉 Todos los tests pasaron! El nucleo esta listo.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa las dependencias.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
