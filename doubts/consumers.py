from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

class DoubtConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated :
          await  self.close(code = 4001)
          return

        self.group_names = await self.get_groups_for_user(user)
        if not self.group_names :
            await self.close(code = 4003)
            return

        for group_name in self.group_names :
            await self.channel_layer.group_add(group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        for group_name in getattr(self, 'group_names', []) :
            await self.channel_layer.group_discard(group_name, self.channel_name)

    @database_sync_to_async
    def get_groups_for_user(self, user):
        from classes.models import ClassGroup

        if user.role == user.Role.STUDENT:
            enrollment = getattr(user, 'enrollment', None)
            if not enrollment:
                return []
            return [f'doubts_class_{enrollment.class_group_id}']

        if user.role == user.Role.TEACHER:
            ids = ClassGroup.objects.filter(teacher_assignments__teacher=user).values_list('id', flat=True)
            return [f'doubts_class_{cid}' for cid in ids]

        if user.role == user.Role.DIRECTOR:
            ids = ClassGroup.objects.filter(organization=user.organization).values_list('id', flat=True)
            return [f'doubts_class_{cid}' for cid in ids]

        return []

    async def doubts_event(self, event):
        await self.send(text_data = json.dumps({"event" : event["event"], "data" : event["data"]}))
