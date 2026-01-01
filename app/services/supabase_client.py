"""Supabase client configuration and initialization."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client singleton
_supabase_client = None
_supabase_available = False


def is_supabase_configured() -> bool:
    """Check if Supabase is properly configured."""
    return bool(SUPABASE_URL and SUPABASE_KEY)


def get_supabase_client():
    """Get the Supabase client instance (singleton pattern).
    
    Returns None if Supabase is not configured.
    """
    global _supabase_client, _supabase_available
    
    if not is_supabase_configured():
        return None
    
    if _supabase_client is None:
        try:
            from supabase import create_client
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            _supabase_available = True
        except Exception as e:
            print(f"Failed to create Supabase client: {e}")
            _supabase_available = False
            return None
    
    return _supabase_client

