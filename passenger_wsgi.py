import os
import sys

# Define path to the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Set the Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hics.settings.production')

# Import the Django WSGI application
from hics.wsgi import application
