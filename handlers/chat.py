import logging
import traceback

from authhandler import AuthHandler
from models.chatUser import ChatUser
from google.appengine.api.taskqueue import Task



class Chat(AuthHandler):
    def enterChatRoom(self):
        user = self.current_user
        if user:
            try:
                cu = user.makeChatUser()
                cu.login(user)
            except:
                tb = traceback.format_exc()
                logging.error('Exception when logging into chat ' + tb)
                self.error(500)
        # Default response: 200
               
    def leaveChatRoom(self):
        user = self.current_user
        ChatUser.logout(user)        
        
    def send(self):
        user = self.current_user
        message = self.request.get('message')
        t = Task(url='/broadcastChatroom', 
                 params={'userName':user.name,
                         'message':message
                         })
        t.add(queue_name="notifications")
        
    def broadcastChatroom(self):
        userName = self.request.get('userName')
        message = self.request.get('message')
        ChatUser.messageChatUsers(userName, message)

            
