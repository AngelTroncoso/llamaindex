#!/usr/bin/env python3
"""
Financial Regulatory Copilot Chile - Connectors Package

Paquete que contiene los conectores a APIs externas.
"""

# Importar conectores (si existen)
try:
    from .cmf_connector import CMFConnector
    from .bch_connector import BCChConnector
    from .sii_connector import SIIConnector
    
    __all__ = ["CMFConnector", "BCChConnector", "SIIConnector"]
except ImportError:
    __all__ = []
