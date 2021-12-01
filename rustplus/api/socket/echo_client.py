from ws4py.client.threadedclient import WebSocketClient
import asyncio

from ..rustplus_pb2 import *
from ..structures import RustChatMessage

class EchoClient(WebSocketClient):

    def __init__(self, ip, port, api, protocols=None, extensions=None, heartbeat_freq=None, ssl_options=None, headers=None, exclude_headers=None):
        super().__init__(f"ws://{ip}:{port}", protocols=protocols, extensions=extensions, heartbeat_freq=heartbeat_freq, ssl_options=ssl_options, headers=headers, exclude_headers=exclude_headers)

        self.api = api

    def opened(self): 
        return 

    def closed(self, code, reason):
        return

    def received_message(self, message):

        app_message = AppMessage()
        app_message.ParseFromString(message.data)

        if app_message.broadcast.teamMessage.message.message == "":
            if app_message.response.seq not in self.api.ignored_responses:
                self.api.responses[app_message.response.seq] = app_message
            else:
                self.api.ignored_responses.remove(app_message.response.seq)
        else:
            message = RustChatMessage(app_message.broadcast.teamMessage.message)
            
            if message.message.startswith(self.api.prefix):
                asyncio.new_event_loop().run_until_complete(self.api.command_handler.run_command(message=message))
