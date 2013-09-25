import json
import logging
from google.appengine.ext import ndb

from authhandler import AuthHandler
from models.whysaurusexception import WhysaurusException 
from models.timezones import PST
from models.notification import Notification
from models.follow import Follow

# This is called by the task queue
class NotificationHandler(AuthHandler):
    def AddNotification(self):
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
                
    def NewNotificationChannel(self):
        user = self.current_user
        results = {'result': False}
        if not user:
            results = {'result': False, 'error': 'User not logged in'}
        else:
            user.createChannel(saveUser=True)
            results = {'result': True, 'token': user.token}
        resultJSON = json.dumps(results)
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)

           
    def ClearNotifications(self):
        user = self.current_user
        latestTimestamp = self.request.get('latest')
        earliestTimestamp = self.request.get('earliest')
        logging.info('TL: %s, TE: %s' %(latestTimestamp, earliestTimestamp))
        results = {'result': False}
        if not user:
            results = {'result': False, 'error': 'User not logged in'}
        else:
            user.clearNotifications(float(latestTimestamp), 
                                    float(earliestTimestamp) if earliestTimestamp else None)
            results = {'result': True}
        resultJSON = json.dumps(results)
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)

        