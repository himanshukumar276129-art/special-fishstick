import sys
import os

# Add parent directory to sys.path to allow importing app.py and local siblings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
