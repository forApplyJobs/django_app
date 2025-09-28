from __future__ import absolute_import, unicode_literals

# Celery app'in Django ile birlikte yüklenmesini sağla
from .celery import app as celery_app

__all__ = ('celery_app',)