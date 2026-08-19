#!/usr/bin/env python3
"""
Financial Regulatory Copilot Chile - Knowledge Base

Base de conocimiento para el agente financiero.
Gestiona la indexación y búsqueda de documentos usando LlamaIndex.
"""

from typing import Dict, List, Optional, Any
import logging
import os
import uuid
import tempfile

# Configure logging
logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Base de conocimiento para el agente financiero.
    
    Atributos:
        documents: Lista de documentos cargados.
        index: Índice de LlamaIndex.
    """
    
    def __init__(self) -> None:
        """Inicializa la KnowledgeBase."""
        self.documents: List[Dict[str, Any]] = []
        self._index = None
        self._temp_dir = tempfile.mkdtemp(prefix="kb_")
        logger.info("KnowledgeBase inicializada")
    
    def add_document(self, file_path: str, user_uploaded: bool = False) -> Optional[str]:
        """Agrega un documento desde una ruta de archivo.
        
        Args:
            file_path: Ruta al archivo.
            user_uploaded: Si el documento fue subido por el usuario.
            
        Returns:
            ID del documento agregado o None si hay error.
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Archivo no encontrado: {file_path}")
                return None
            
            doc_id = str(uuid.uuid4())
            filename = os.path.basename(file_path)
            
            # Obtener metadatos
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(filename)[1].lower()
            
            doc_info = {
                "id": doc_id,
                "name": filename,
                "path": file_path,
                "type": self._get_document_type(file_ext),
                "size": file_size,
                "user_uploaded": user_uploaded,
                "timestamp": self._get_current_timestamp()
            }
            
            self.documents.append(doc_info)
            logger.info(f"Documento agregado: {filename}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error agregando documento {file_path}: {str(e)}")
            return None
    
    def add_document_from_bytes(self, file_path: str, file_name: str, 
                                user_uploaded: bool = False) -> Optional[str]:
        """Agrega un documento desde bytes (para archivos subidos).
        
        Args:
            file_path: Ruta temporal del archivo.
            file_name: Nombre original del archivo.
            user_uploaded: Si el documento fue subido por el usuario.
            
        Returns:
            ID del documento agregado o None si hay error.
        """
        return self.add_document(file_path, user_uploaded)
    
    def remove_document(self, doc_id: str) -> bool:
        """Elimina un documento por su ID.
        
        Args:
            doc_id: ID del documento a eliminar.
            
        Returns:
            True si se eliminó correctamente.
        """
        try:
            self.documents = [doc for doc in self.documents if doc["id"] != doc_id]
            logger.info(f"Documento eliminado: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando documento {doc_id}: {str(e)}")
            return False
    
    def clear_user_documents(self) -> None:
        """Elimina todos los documentos subidos por el usuario."""
        self.documents = [doc for doc in self.documents if not doc.get("user_uploaded", False)]
        logger.info("Documentos de usuario eliminados")
    
    def clear_all(self) -> None:
        """Elimina todos los documentos."""
        self.documents = []
        logger.info("Todos los documentos eliminados")
    
    def get_index(self):
        """Obtiene el índice de LlamaIndex.
        
        Returns:
            Índice de LlamaIndex o None.
        """
        return self._index
    
    def query_index(self, query: str) -> List[Dict[str, Any]]:
        """Realiza una búsqueda semántica en el índice.
        
        Args:
            query: Consulta de búsqueda.
            
        Returns:
            Lista de resultados.
        """
        logger.info(f"Búsqueda en KB: {query[:50]}...")
        # Implementación mínima - buscar en documentos por nombre
        results = []
        for doc in self.documents:
            if query.lower() in doc.get("name", "").lower():
                results.append({
                    "id": doc["id"],
                    "name": doc["name"],
                    "score": 0.9,
                    "content": f"Documento: {doc['name']}"
                })
        return results[:5]  # Devolver solo los mejores 5
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la base de conocimiento.
        
        Returns:
            Diccionario con estadísticas.
        """
        user_docs = [doc for doc in self.documents if doc.get("user_uploaded", False)]
        base_docs = [doc for doc in self.documents if not doc.get("user_uploaded", False)]
        
        return {
            "total_documents": len(self.documents),
            "user_documents": len(user_docs),
            "base_documents": len(base_docs),
            "total_size": sum(doc.get("size", 0) for doc in self.documents),
            "index_available": self._index is not None
        }
    
    def _get_document_type(self, extension: str) -> str:
        """Obtiene el tipo de documento basado en la extensión.
        
        Args:
            extension: Extensión del archivo.
            
        Returns:
            Tipo de documento.
        """
        types = {
            ".pdf": "PDF",
            ".docx": "Word",
            ".doc": "Word",
            ".xlsx": "Excel",
            ".xls": "Excel",
            ".txt": "Text",
            ".csv": "CSV"
        }
        return types.get(extension, "Unknown")
    
    def _get_current_timestamp(self) -> str:
        """Obtiene el timestamp actual.
        
        Returns:
            Timestamp en formato ISO.
        """
        from datetime import datetime
        return datetime.now().isoformat()
