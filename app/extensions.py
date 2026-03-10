"""Supabase client and other extensions."""
import logging
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)


def get_supabase_client():
    """Get Supabase client instance. Returns None if not configured."""
    try:
        from supabase import create_client, Client
        from app.config import get_settings
        settings = get_settings()
        client: Client = create_client(settings.supabase_url, settings.supabase_key)
        return client
    except Exception as exc:
        logger.warning("Supabase client could not be initialized: %s", exc)
        return None


def get_supabase_admin_client():
    """Get Supabase admin client with service role key."""
    try:
        from supabase import create_client, Client
        from app.config import get_settings
        settings = get_settings()
        client: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        return client
    except Exception as exc:
        logger.warning("Supabase admin client could not be initialized: %s", exc)
        return None
