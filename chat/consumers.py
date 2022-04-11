from channels.consumer import SyncConsumer, AsyncConsumer
from users.models import CustomeUsers
from chat.models import ChatSpace, Message
from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
import json


class PersonalChatCon(AsyncConsumer):
    async def websocket_connect(self, event):
        # Getting the username of the message recieving user from url 
        self.other_username = self.scope['url_route']['kwargs']['username'] 
        self.logged_user = self.scope['user']
        self.other_user = await sync_to_async(CustomeUsers.objects.get)(username = self.other_username) 
        self.chat_area = await sync_to_async(ChatSpace.objects.get_or_create_chat)(self.logged_user, self.other_user)
        self.room_name = f'personal_chat_{self.chat_area.id}'
        # Adding the connecting user to the group
        # For personal chat this group will only contain 2 members
        await self.channel_layer.group_add(self.room_name,self.channel_name)
        await self.send({
            'type':'websocket.accept',
        })
        print(self.channel_name,"-",'Connected')

    async def websocket_receive(self, event):
        print(self.channel_name,"-",event['text'])
        self.msgobj = await self.storeMsg(event['text'])
        self.msg  = json.dumps({
            'text':self.msgobj.body,
            'time':self.msgobj.created.strftime('%Y-%m-%dT%H:%M:%S'),
            'username':self.logged_user.username,
            
        })
        await self.channel_layer.group_send(self.room_name, {
            'type':'particularSend',
            'text':self.msg
        })

    async def particularSend(self,event):
        await self.send({
            'type':'websocket.send',
            'text':event['text']
        })    

    async def websocket_disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name,self.channel_name)
        print('Disconnnected...')  
    @database_sync_to_async
    def storeMsg(self, message):
        msg = Message.objects.create(
            chat=self.chat_area,
            sender=self.logged_user,
            body=message
        )
        return msg      