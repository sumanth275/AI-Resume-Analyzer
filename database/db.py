"""Backward-compatible re-export of root db module."""

from db import get_db, close_db, init_db, seed_default_jobs_if_needed

__all__ = ['get_db', 'close_db', 'init_db', 'seed_default_jobs_if_needed']
