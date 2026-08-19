# Financial Regulatory Copilot Chile

> **Sistema de Asesoramiento Financiero Chileno basado en IA**
> Asistente inteligente que combina LlamaIndex + RAG + Motor de Recomendacion para normativa BCCh, CMF, SII y NIIF/IFRS.

---

## Caracteristicas Principales

- **Carga dinamica de documentos**: Drag & drop de PDF, Word, Excel, TXT, CSV
- **Recomendacion inteligente**: Sugiere que documentos cargar segun la consulta
- **Asesoria polifuncional**: Normativa chilena y analisis de documentos
- **Citacion automatica**: Referencias a fuentes en todas las respuestas

## Estructura del Proyecto

```
financial-regulatory-copilot-chile/
├── app/                          # Aplicacion Streamlit
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada
│   ├── components/
│   │   ├── __init__.py
│   │   ├── file_uploader.py      # Carga de archivos
│   │   ├── chat_interface.py    # Interfaz de chat
│   │   └── recommendation_engine.py
│   └── utils/
│       ├── __init__.py
│       └── session_manager.py  # Gestor de sesion
├── core/                          # Nucleo compartido
│   ├── __init__.py
│   └── agent/
│       ├── __init__.py
│       ├── financial_agent.py  # Agente principal
│       ├── knowledge_base.py   # Base de conocimiento
│       └── data_recommender.py  # Motor de recomendaciones
├── backend/
│   ├── __init__.py
│   ├── api.py                  # API REST (opcional)
│   └── mcp_server.py          # Servidor MCP (opcional)
├── examples/
│   └── test_core_agent.py
├── skills/
│   └── financial-regulatory-copilot-chile/
│       └── SKILL.md            # Documentacion de la skill
├── tests/
├── requirements.txt
├── README.md
└── .gitignore
```

## Tecnologias Utilizadas

| Categoria | Tecnologia | Version | Proposito |
|------------|--------------|-----------|-------------|
| **Frontend** | Streamlit | >=1.28.0 | Interfaz web |
| **RAG** | LlamaIndex | >=0.10.0 | Indexacion y busqueda |
| **LLM** | Ollama/OpenAI | - | Modelos de lenguaje |
| **Documentos** | PyPDF2, python-docx, pandas | - | Procesamiento de archivos |

## Requisitos Previos

- Python 3.10+
- pip (gestor de paquetes de Python)
- Git

## Instalacion

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/financial-regulatory-copilot-chile.git
cd financial-regulatory-copilot-chile
```

### 2. Crear entorno virtual (opcional pero recomendado)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar dependencias adicionales (opcional)

```bash
# Para LLM local con Ollama
pip install ollama openai

# Para procesamiento de documentos
pip install pypdf python-docx pandas openpyxl beautifulsoup4
```

## Ejecutar la Aplicacion

```bash
streamlit run app/main.py
```

La aplicacion se abrira automaticamente en tu navegador en `http://localhost:8501`

## Configuracion

### Variables de Entorno

Crea un archivo `.env` en la raiz del proyecto:

```env
# OpenAI (opcional)
OPENAI_API_KEY=tu_api_key_aqui

# Ollama (opcional - default: http://localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434
```

### Configuracion de LLM

En la interfaz de Streamlit (barra lateral):
- Selecciona el proveedor: **Ollama (Local)** o **OpenAI**
- Si usas OpenAI, ingresa tu API Key
- Selecciona el modelo preferido

## Uso de la Aplicacion

### 1. Cargar Documentos
- Usa el componente de **Drag & Drop** en el panel izquierdo
- Soporta: PDF, Word, Excel, TXT, CSV
- Tamanio maximo: 100MB por archivo

### 2. Realizar Consultas
- Escribe tu pregunta en el chat
- Ejemplos:
  - "Que dice la Ley General de Bancos sobre solvencia?"
  - "Explica la NIIF 9"
  - "Analiza este contrato"

### 3. Recomendaciones Automaticas
- El sistema sugerira documentos relevantes
- Documentos **requeridos** vs sugeridos
- Puedes cargar los documentos recomendados con un clic

## Normativa Cubierta

### Instituciones
- **BCCh**: Banco Central de Chile
- **CMF**: Comision para el Mercado Financiero
- **SII**: Servicio de Impuestos Internos
- **Hacienda**: Ministerio de Hacienda

### Normas Fundamentales
- Ley General de Bancos (DFL No 3)
- Ley de Mercado de Valores (Ley No 18.045)
- Ley de Sociedades Anonimas (Ley No 18.046)
- CNF (Compendio de Normas Financieras)
- CNMF (Compendio de Normas Monetarias y Financieras)
- NCG (Normas de Caracter General)

### Estandares Contables (NIIF/IFRS)
- NIIF 9: Instrumentos Financieros
- NIIF 7: Informacion a Revelar sobre Instrumentos Financieros
- NIIF 13: Medicion del Valor Razonable
- NIIF 15: Ingresos de Actividades Ordinarias
- NIIF 16: Arrendamientos
- NIC 1: Presentacion de Estados Financieros
- NIC 7: Estado de Flujos de Efectivo
- NIC 21: Efectos de las Variaciones en las Tasas de Cambio

## Estructura de Archivos

```
app/
├── main.py                    # Aplicacion principal Streamlit
├── components/
│   ├── file_uploader.py      # Componente de carga de archivos
│   ├── chat_interface.py    # Componente de chat
│   └── recommendation_engine.py # Motor de recomendaciones UI
└── utils/
    └── session_manager.py  # Gestor de estado

core/
├── agent/
│   ├── financial_agent.py  # Agente principal
│   ├── knowledge_base.py   # Base de conocimiento (LlamaIndex)
│   └── data_recommender.py  # Motor de recomendaciones
└── connectors/
    # Conectores a APIs (BCCh, CMF, SII)
```

## API de los Componentes

### FinancialAgent

```python
from core.agent.financial_agent import FinancialAgent

agent = FinancialAgent()

# Configurar base de conocimiento
agent.set_knowledge_base(kb)

# Responder consulta
response = agent.respond("Que es la NIIF 9?")
# Devuelve: {"content": "...", "citations": [...], "recommendations": [...]}

# Anadir documento de usuario
agent.add_user_document("path/to/document.pdf")
```

### DataRecommender

```python
from core.agent.data_recommender import DataRecommender

recommender = DataRecommender()
recommendations = recommender.recommend("NIIF 9")
# Devuelve: Lista de documentos recomendados con categorias
```

### KnowledgeBase

```python
from core.agent.knowledge_base import KnowledgeBase

kb = KnowledgeBase()

# Anadir documento
kb.add_document("path/to/document.pdf")

# Buscar en indice
results = kb.query_index("bancos solvencia")
```

## Contribuir

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -m 'Anade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

MIT License - Libre para uso personal y comercial.

## Contacto

Para preguntas o soporte, contacta a los mantenedores del proyecto.

---

**Desarrollado con amor usando Streamlit + LlamaIndex + IA**

*Version: 0.1.0 | Estado: En Desarrollo | Phase 2: 100% Completado*
