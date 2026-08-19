#!/usr/bin/env python3
"""
Financial Regulatory Copilot Chile - File Uploader Component

Componente de Streamlit para carga de archivos (drag & drop).
Soporta múltiples formatos: PDF, Word, Excel, TXT, CSV.
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple, Any
import tempfile
import os
import uuid
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Formatos de archivo soportados
SUPPORTED_FORMATS = {
    ".pdf": "PDF",
    ".docx": "Word",
    ".doc": "Word",
    ".xlsx": "Excel",
    ".xls": "Excel",
    ".txt": "Texto",
    ".csv": "CSV"
}

# Tamaño máximo de archivo (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


class FileUploader:
    """Componente para carga de archivos con soporte de drag & drop.
    
    Atributos:
        upload_area: Área de subida de Streamlit.
        uploaded_files: Lista de archivos subidos en la sesión actual.
    """
    
    def __init__(self, label: str = "Cargar Documentos", 
                 accept_multiple_files: bool = True,
                 help_text: Optional[str] = None) -> None:
        """Inicializa el componente FileUploader.
        
        Args:
            label: Texto del label del componente.
            accept_multiple_files: Si permite múltiples archivos.
            help_text: Texto de ayuda (opcional).
        """
        self.label = label
        self.accept_multiple_files = accept_multiple_files
        self.help_text = help_text or self._get_default_help_text()
        self._temp_dir: Optional[tempfile.TemporaryDirectory] = None
    
    def _get_default_help_text(self) -> str:
        """Obtiene el texto de ayuda por defecto.
        
        Returns:
            Texto de ayuda formateado.
        """
        formats = ", ".join(SUPPORTED_FORMATS.values())
        return f"Soporta: {formats}. Tamaño máximo: 100MB por archivo."
    
    def render(self) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Renderiza el componente de carga de archivos.
        
        Returns:
            Tupla con (lista de archivos subidos, mensaje de error si hay).
        """
        # Crear el uploader de Streamlit
        uploaded_files = st.file_uploader(
            self.label,
            type=list(SUPPORTED_FORMATS.keys()),
            accept_multiple_files=self.accept_multiple_files,
            help=self.help_text,
            key="file_uploader_component"
        )
        
        # Procesar archivos subidos
        if uploaded_files:
            processed_files = []
            error_message = None
            
            # Validar tamaño de archivos
            for file in uploaded_files:
                if file.size > MAX_FILE_SIZE:
                    error_message = f"Archivo {file.name} excede el tamaño máximo de 100MB"
                    logger.warning(f"Archivo demasiado grande: {file.name} ({file.size} bytes)")
                    continue
                
                # Procesar archivo
                file_info = self._process_uploaded_file(file)
                if file_info:
                    processed_files.append(file_info)
                else:
                    error_message = f"No se pudo procesar el archivo: {file.name}"
                    logger.error(f"Error procesando archivo: {file.name}")
            
            return processed_files, error_message
        
        return [], None
    
    def _process_uploaded_file(self, uploaded_file) -> Optional[Dict[str, Any]]:
        """Procesa un archivo subido y lo guarda temporalmente.
        
        Args:
            uploaded_file: Archivo subido de Streamlit.
            
        Returns:
            Diccionario con información del archivo o None si hay error.
        """
        try:
            # Crear directorio temporal si no existe
            if self._temp_dir is None or not os.path.exists(self._temp_dir.name):
                self._temp_dir = tempfile.TemporaryDirectory(prefix="financial_copilot_")
            
            # Generar ID único para el archivo
            file_id = str(uuid.uuid4())
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            file_name = uploaded_file.name
            
            # Validar extensión
            if file_ext not in SUPPORTED_FORMATS:
                logger.warning(f"Formato no soportado: {file_ext}")
                return None
            
            # Guardar archivo temporalmente
            temp_path = os.path.join(self._temp_dir.name, f"{file_id}{file_ext}")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Crear información del archivo
            file_info = {
                "id": file_id,
                "name": file_name,
                "path": temp_path,
                "type": SUPPORTED_FORMATS[file_ext],
                "size": uploaded_file.size,
                "extension": file_ext,
                "user_uploaded": True,
                "session_id": st.session_state.get("financial_copilot_session_id", ""),
                "uploaded_at": self._get_current_timestamp()
            }
            
            logger.info(f"Archivo procesado: {file_name} ({file_id})")
            return file_info
            
        except Exception as e:
            logger.error(f"Error procesando archivo {uploaded_file.name}: {str(e)}")
            return None
    
    def render_with_preview(self) -> Dict[str, Any]:
        """Renderiza el uploader con vista previa de archivos.
        
        Returns:
            Diccionario con información de los archivos procesados.
        """
        result = {
            "files": [],
            "error": None,
            "status": "idle"
        }
        
        # Área de subida
        uploaded_files, error = self.render()
        
        if error:
            result["error"] = error
            result["status"] = "error"
            st.error(error)
        
        if uploaded_files:
            result["files"] = uploaded_files
            result["status"] = "success"
            result["count"] = len(uploaded_files)
            
            # Mostrar vista previa
            self._render_file_preview(uploaded_files)
        
        # Mostrar archivos anteriormente subidos (de session_state)
        self._render_existing_files()
        
        return result
    
    def _render_file_preview(self, files: List[Dict[str, Any]]) -> None:
        """Muestra vista previa de los archivos recién subidos con estilo premium.
        
        Args:
            files: Lista de archivos a mostrar.
        """
        icon_map = {
            ".pdf": "📄",
            ".docx": "📝",
            ".doc": "📝",
            ".xlsx": "📊",
            ".xls": "📊",
            ".txt": "📃",
            ".csv": "📋"
        }
        
        with st.expander(f"📁 {len(files)} archivo(s) cargado(s)", expanded=True):
            for file_info in files:
                ext = file_info.get('extension', '').lower()
                icon = icon_map.get(ext, "📎")
                
                cols = st.columns([1, 3, 1, 1])
                
                with cols[0]:
                    st.markdown(f"<div style='font-size: 2rem;'>{icon}</div>", unsafe_allow_html=True)
                
                with cols[1]:
                    name = file_info['name']
                    if len(name) > 25:
                        name = name[:22] + "..."
                    st.markdown(f"**{name}**")
                    st.caption(f"{file_info['type']} | {self._format_file_size(file_info['size'])}")
                
                with cols[2]:
                    if st.button("Ver", key=f"view_{file_info['id']}"):
                        self._show_file_content(file_info)
                
                with cols[3]:
                    if st.button("❌", key=f"remove_{file_info['id']}"):
                        self._remove_file(file_info['id'])
                        st.rerun()
    
    def _render_existing_files(self) -> None:
        """Muestra los archivos subidos anteriormente en la sesión."""
        session_files = st.session_state.get("financial_copilot_uploaded_files", [])
        
        if session_files:
            with st.expander(f"📂 Archivos en sesión ({len(session_files)})", expanded=False):
                for file_info in session_files:
                    cols = st.columns([3, 1, 1])
                    
                    with cols[0]:
                        st.write(f"**{file_info['name']}**")
                        st.caption(f"Tipo: {file_info['type']} | {file_info['uploaded_at']}")
                    
                    with cols[1]:
                        if st.button("Ver", key=f"view_existing_{file_info['id']}"):
                            self._show_file_content(file_info)
                    
                    with cols[2]:
                        if st.button("❌", key=f"remove_existing_{file_info['id']}"):
                            self._remove_file(file_info['id'])
                            st.rerun()
    
    def _show_file_content(self, file_info: Dict[str, Any]) -> None:
        """Muestra el contenido de un archivo.
        
        Args:
            file_info: Información del archivo a mostrar.
        """
        try:
            if not os.path.exists(file_info['path']):
                st.warning("El archivo ya no está disponible.")
                return
            
            ext = file_info['extension'].lower()
            
            if ext == ".pdf":
                self._show_pdf(file_info['path'])
            elif ext in [".txt", ".csv"]:
                self._show_text(file_info['path'])
            elif ext in [".docx", ".doc"]:
                self._show_docx(file_info['path'])
            elif ext in [".xlsx", ".xls"]:
                self._show_excel(file_info['path'])
            else:
                st.warning("Formato no compatible para vista previa.")
                
        except Exception as e:
            st.error(f"Error mostrando archivo: {str(e)}")
            logger.error(f"Error mostrando archivo {file_info['name']}: {str(e)}")
    
    def _show_pdf(self, path: str) -> None:
        """Muestra un PDF.
        
        Args:
            path: Ruta al archivo PDF.
        """
        try:
            import PyPDF2
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)
                
                st.subheader("Contenido del PDF")
                st.write(f"Número de páginas: {num_pages}")
                
                # Mostrar primeras páginas
                pages_to_show = min(num_pages, 5)
                for i in range(pages_to_show):
                    with st.expander(f"Página {i + 1}"):
                        page = reader.pages[i]
                        st.text(page.extract_text()[:2000])  # Limitar a 2000 caracteres
                        
                if num_pages > 5:
                    st.info(f"Se muestran las primeras 5 páginas de {num_pages}.")
                    
        except ImportError:
            st.warning("PyPDF2 no está instalado. Instálalo para ver PDFs.")
        except Exception as e:
            st.error(f"Error leyendo PDF: {str(e)}")
    
    def _show_text(self, path: str) -> None:
        """Muestra un archivo de texto.
        
        Args:
            path: Ruta al archivo de texto.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            st.subheader("Contenido del archivo")
            st.text_area("Texto", content, height=400)
            
        except Exception as e:
            st.error(f"Error leyendo archivo: {str(e)}")
    
    def _show_docx(self, path: str) -> None:
        """Muestra un documento Word.
        
        Args:
            path: Ruta al archivo Word.
        """
        try:
            import python_docx
            doc = python_docx.Document(path)
            
            st.subheader("Contenido del documento Word")
            
            for i, para in enumerate(doc.paragraphs):
                if para.text.strip():
                    st.write(para.text)
                    
        except ImportError:
            st.warning("python-docx no está instalado. Instálalo para ver documentos Word.")
        except Exception as e:
            st.error(f"Error leyendo Word: {str(e)}")
    
    def _show_excel(self, path: str) -> None:
        """Muestra un archivo Excel.
        
        Args:
            path: Ruta al archivo Excel.
        """
        try:
            import pandas as pd
            
            st.subheader("Contenido del archivo Excel")
            
            # Leer todas las hojas
            xls = pd.ExcelFile(path)
            sheet_names = xls.sheet_names
            
            if len(sheet_names) == 1:
                df = pd.read_excel(path, sheet_name=sheet_names[0])
                st.dataframe(df)
            else:
                sheet = st.selectbox("Seleccionar hoja", sheet_names)
                df = pd.read_excel(path, sheet_name=sheet)
                st.dataframe(df)
                
        except ImportError:
            st.warning("pandas no está instalado. Instálalo para ver archivos Excel.")
        except Exception as e:
            st.error(f"Error leyendo Excel: {str(e)}")
    
    def _remove_file(self, file_id: str) -> bool:
        """Elimina un archivo de la sesión.
        
        Args:
            file_id: ID del archivo a eliminar.
            
        Returns:
            True si se eliminó correctamente.
        """
        try:
            # Eliminar del session_state
            uploaded_files = st.session_state.get("financial_copilot_uploaded_files", [])
            updated_files = [f for f in uploaded_files if f['id'] != file_id]
            st.session_state["financial_copilot_uploaded_files"] = updated_files
            
            # Eliminar archivo físico si existe
            for file_info in uploaded_files:
                if file_info['id'] == file_id and os.path.exists(file_info['path']):
                    os.remove(file_info['path'])
                    logger.info(f"Archivo físico eliminado: {file_info['path']}")
                    break
            
            logger.info(f"Archivo eliminado de sesión: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando archivo {file_id}: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """Limpia todos los archivos temporales."""
        if self._temp_dir:
            try:
                self._temp_dir.cleanup()
                logger.info("Directorio temporal limpiado")
            except Exception as e:
                logger.error(f"Error limpiando directorio temporal: {str(e)}")
            finally:
                self._temp_dir = None
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Formatea el tamaño del archivo en formato legible.
        
        Args:
            size_bytes: Tamaño en bytes.
            
        Returns:
            Tamaño formateado.
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def _get_current_timestamp(self) -> str:
        """Obtiene el timestamp actual.
        
        Returns:
            Timestamp en formato ISO.
        """
        from datetime import datetime
        return datetime.now().isoformat()


# Función conveniencia para uso directo
def create_file_uploader(label: str = "Cargar Documentos", 
                        accept_multiple_files: bool = True,
                        help_text: Optional[str] = None) -> FileUploader:
    """Crea una instancia del FileUploader.
    
    Args:
        label: Texto del label.
        accept_multiple_files: Si permite múltiples archivos.
        help_text: Texto de ayuda.
        
    Returns:
        Instancia de FileUploader.
    """
    return FileUploader(label, accept_multiple_files, help_text)
