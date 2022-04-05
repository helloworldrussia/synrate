import os
import threading
from django.core.wsgi import get_wsgi_application

from custom_timer import timer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'synrate.settings')

application = get_wsgi_application()
t1 = threading.Thread(target=timer)
t1.start()