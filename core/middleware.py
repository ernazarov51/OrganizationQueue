from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from core.models import User
from datetime import timedelta
from django.utils.timezone import now
from django.http import JsonResponse


@database_sync_to_async
def get_user(token):
    try:
        access_token = AccessToken(token)
        return User.objects.get(id=access_token["user_id"])
    except Exception:
        return AnonymousUser()


class TokenAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]
        scope["user"] = await get_user(token) if token else AnonymousUser()
        return await self.inner(scope, receive, send)




