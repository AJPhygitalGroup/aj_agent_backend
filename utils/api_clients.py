"""
Clientes de API centralizados para todos los agentes.
Cada agente importa el cliente que necesita de aquí.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(Path(__file__).parent.parent / ".env")


def get_anthropic_client():
    """Retorna cliente de Anthropic."""
    import anthropic
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def get_openai_client():
    """Retorna cliente de OpenAI."""
    import openai
    return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_perplexity_client():
    """Retorna cliente de Perplexity (usa SDK de OpenAI con base_url diferente)."""
    import openai
    return openai.OpenAI(
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        base_url="https://api.perplexity.ai",
    )


def get_google_sheets_client():
    """Retorna cliente de Google Sheets."""
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "config/google-service-account.json")
    credentials = Credentials.from_service_account_file(creds_file, scopes=scopes)
    return gspread.authorize(credentials)


def get_heygen_headers() -> dict:
    """Retorna headers para HeyGen API."""
    return {
        "X-Api-Key": os.getenv("HEYGEN_API_KEY", ""),
        "Content-Type": "application/json",
    }


def get_flux_headers() -> dict:
    """Retorna headers para Flux API."""
    return {
        "Authorization": f"Bearer {os.getenv('FLUX_API_KEY', '')}",
        "Content-Type": "application/json",
    }


def get_meta_access_token() -> str:
    """Retorna access token de Meta."""
    return os.getenv("META_ACCESS_TOKEN", "")


def get_youtube_credentials() -> dict:
    """Retorna credenciales de YouTube."""
    return {
        "api_key": os.getenv("YOUTUBE_API_KEY", ""),
        "client_id": os.getenv("YOUTUBE_CLIENT_ID", ""),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET", ""),
        "refresh_token": os.getenv("YOUTUBE_REFRESH_TOKEN", ""),
    }


def get_linkedin_credentials() -> dict:
    """Retorna credenciales de LinkedIn."""
    return {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID", ""),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET", ""),
        "access_token": os.getenv("LINKEDIN_ACCESS_TOKEN", ""),
        "organization_id": os.getenv("LINKEDIN_ORGANIZATION_ID", ""),
    }


def get_tiktok_credentials() -> dict:
    """Retorna credenciales de TikTok."""
    return {
        "client_key": os.getenv("TIKTOK_CLIENT_KEY", ""),
        "client_secret": os.getenv("TIKTOK_CLIENT_SECRET", ""),
        "access_token": os.getenv("TIKTOK_ACCESS_TOKEN", ""),
    }
