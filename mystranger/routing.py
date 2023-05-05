from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path
from mystranger.asgi import get_asgi_application
django_asgi_app = get_asgi_application()
from mystranger_app.consumers import ChatConsumer

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
	'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter([
				
				path('chat/', ChatConsumer.as_asgi()),
				
				]
				
			)
		)
	),
})