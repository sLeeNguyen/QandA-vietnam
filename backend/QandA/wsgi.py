"""
WSGI config for QandA project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from elasticsearch_client import elasticsearch

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QandA.settings')

# Run elasticsearch index settings
elasticsearch.init()

application = get_wsgi_application()
