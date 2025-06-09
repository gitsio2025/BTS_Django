"""
WSGI config for BTS_PY project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Définit la variable d’environnement 'DJANGO_SETTINGS_MODULE' si elle n’est pas déjà définie.
# Cela indique à Django où se trouve le fichier de configuration principal du projet (settings.py).
# Ici, 'BTS_PY.settings' signifie que Django utilisera BTS_PY/settings.py comme configuration.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BTS_PY.settings')

# Initialise l'application WSGI de Django.
# Cela permet à un serveur WSGI (comme Gunicorn, uWSGI ou mod_wsgi) de lancer ton projet Django.
# Cette variable 'application' sera utilisée comme point d’entrée pour servir les requêtes HTTP.
application = get_wsgi_application()
