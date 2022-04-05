import os
import threading
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'synrate.settings')

application = get_wsgi_application()

from . import custom_timer

t1 = threading.Thread(target=custom_timer.timer())
t1.start()