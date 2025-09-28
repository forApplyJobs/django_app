import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Django modelini burada import et
        from .models import Frame
        from django.contrib.auth.models import AnonymousUser

        self.frame_id = self.scope['url_route']['kwargs']['frame_id']
        self.group_name = f'progress_{self.frame_id}'

        # Kullanıcı doğrulama
        if isinstance(self.scope.get("user"), AnonymousUser):
            await self.close()
            return

        # Frame sahibi mi kontrol et
        frame_exists = await self.check_frame_ownership()
        if not frame_exists:
            await self.close()
            return

        # Gruba katıl
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_progress(self, event):
        await self.send(text_data=event['data'])

    @database_sync_to_async
    def check_frame_ownership(self):
        from .models import Frame
        try:
            Frame.objects.get(id=self.frame_id, owner=self.scope["user"])
            return True
        except Frame.DoesNotExist:
            return False
    async def progress_update(self, event):
        """
        Bu method 'type':'progress_update' olan mesajları alır
        """
        await self.send(text_data=json.dumps(event['data']))