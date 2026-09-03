#!/usr/bin/env python3
"""Expose le serveur MCP Google Scholar de JackKuo666 en HTTP pour l'ajouter comme connecteur personnalisé claude.ai.

1. git clone https://github.com/JackKuo666/Google-Scholar-MCP-Server  &&  cd Google-Scholar-MCP-Server
2. pip install -r requirements.txt   (mcp, scholarly, requests, bs4)
3. python3 /chemin/vers/stratification_qc/Scripts/serveur_scholar_http.py     -> http://127.0.0.1:8000/mcp
4. Exposer le port (ex. : ngrok http 8000 ou cloudflared tunnel --url http://localhost:8000), puis dans claude.ai :
   Paramètres > Connecteurs > Ajouter un connecteur personnalisé > URL https://<tunnel>/mcp ; activer le
   connecteur dans la conversation. Les requêtes vers Google Scholar partent alors de votre poste.
Le serveur d'origine tourne en stdio (Claude Desktop) ; ce lanceur ne fait que changer le transport.
"""
import os, sys
sys.path.insert(0, os.getcwd())
from google_scholar_server import mcp  # objet FastMCP défini par le dépôt cloné

if __name__ == "__main__":
    mcp.settings.host = "127.0.0.1"
    mcp.settings.port = int(os.environ.get("PORT", "8000"))
    try:
        mcp.run(transport="streamable-http")   # mcp >= 1.8
    except (ValueError, TypeError):
        mcp.run(transport="sse")               # anciennes versions : URL .../sse
