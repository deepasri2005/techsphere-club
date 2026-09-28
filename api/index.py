import os
import sys

# Append project root directory to Python module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Export WSGI application for Vercel
app = app
