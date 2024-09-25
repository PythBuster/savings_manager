"""Everything about the limiter is implemented here."""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter: Limiter = Limiter(key_func=get_remote_address)
"""The global limiter for all fastAPI endpoints."""
