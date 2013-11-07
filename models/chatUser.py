import json
import logging

from google.appengine.ext import ndb
from google.appengine.api import channel


class ChatUser(ndb.Model):
    loggedIn = ndb.DateTimeProperty(auto_now_add=True)
    token = ndb.StringProperty(indexed=False)  
    tokenExpires = ndb.DateTimeProperty(indexed=False) 
    
    @classmethod
    def messageChatUsers(cls, userName, message):
        q = ChatUser.query()        
        for cu in q.iter():     
            logging.info('Messaging token: ' + cu.token)
            messageParams = {
                             'type':'chat',
                             'userName': userName,
                             'message': message
                             }
            channel.send_message(cu.token, json.dumps(messageParams))
       
    @classmethod
    def logout(cls, parentUser):
        q = cls.query(ancestor=parentUser.key)
        q = q.order(cls.loggedIn)
        # there should only ever be one, unless some concurrency issue 
        # we'll clean up at most two here
        chatUserRecords = q.fetch(2) 
        for cu in chatUserRecords:
            cu.delete()
         
    # Chat users are stored in the DB while they are logged in       
    def login(self, parentUser):
        q = ChatUser.query(ancestor=parentUser.key).order(ChatUser.loggedIn)
        # there should only ever be one, unless some concurrency issue 
        # we'll clean up any seconds here
        chatUserRecords = q.fetch(2)        
        if chatUserRecords:
            # Update the first one with the token and delete the 
            chatUserRecords[0].token = self.token
            chatUserRecords[0].tokenExpires = self.tokenExpires
            chatUserRecords[0].put()
            # Delete the other one
            if len(chatUserRecords) > 1:
                chatUserRecords[1].delete()
        else:        
            self.put()
            
    
            

