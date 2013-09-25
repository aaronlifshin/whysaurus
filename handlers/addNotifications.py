import json
from google.appengine.ext import ndb

from authhandler import AuthHandler
from models.whysaurusexception import WhysaurusException 
from models.timezones import PST
from models.notification import Notification
from models.follow import Follow

# This is called by the task queue
class AddNotifications(AuthHandler):
    def post(self):
        rootKeyUrlsafe = self.request.get('rootKey')
        notifyReason = self.request.get('notifyReason')
        sourceUserUrlsafe = self.request.get('userKey')

        pointRootKey = ndb.Key(urlsafe=rootKeyUrlsafe)
        sourceUserKey = ndb.Key(urlsafe=sourceUserUrlsafe)
        follows = Follow.getActiveFollowsForPoint(pointRootKey)
        for f in follows:
            if f.user != sourceUserKey:
                Notification.createNotificationFromFollow(f, pointRootKey, 
                                                          sourceUserKey, 
                                                          notifyReason)
           
        