"""
Vercel Serverless entry point for FastAPI.
Exposes the FastAPI app instance for Vercel Python Serverless / Services runtime.
"""

import os
import sys

_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_current_dir)
_parent_dir = os.path.dirname(_backend_dir)

for path in [_current_dir, _backend_dir, _parent_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from backend.main import app
except ImportError:
    from main import app
