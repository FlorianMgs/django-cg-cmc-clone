# Websockets Routing File

from django.urls import path
from .consumers import CoinsConsumer


ws_urlpatterns = [
    path('ws/coins/', CoinsConsumer.as_asgi())
]

# Consumers are similar as views in classical django wsgi apps
