from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser, User
from channels.middleware import BaseMiddleware
from jwt import decode as jwt_decode
from django.conf import settings
from channels.auth import AuthMiddlewareStack

@database_sync_to_async
def get_user(validated_token):
    try:
        user = User.objects.get(id=validated_token["user_id"])
        # return get_user_model().objects.get(id=toke_id)
        return user
       
    except User.DoesNotExist:
        return AnonymousUser()
    
class JwtAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)
        
    
    async def __call__(self, scope, receive, send):
        try:
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
            decoded_data = jwt_decode(token_key, settings.SECRET_KEY, algorithms=["HS256"])
            scope["user"] =  await get_user(validated_token=decoded_data)
        except:
            scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)

def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(AuthMiddlewareStack(inner))