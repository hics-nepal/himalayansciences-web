import os
import sys

# Load virtual environment packages
VENV_PACKAGES = '/home/elyakadv/virtualenv/himalayansciences-web/3.11/lib/python3.11/site-packages'
if VENV_PACKAGES not in sys.path:
    sys.path.insert(0, VENV_PACKAGES)

sys.path.insert(0, os.path.dirname(__file__))

import hics.wsgi
application = hics.wsgi.application
