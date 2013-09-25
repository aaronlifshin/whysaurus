import webapp2
import datetime
import logging
import constants
import os
import json

from google.appengine.ext import ndb
from follow import Follow
from google.appengine.api import channel
from google.appengine.ext.webapp import template



class Notification(ndb.Model):
    targetUser = ndb.KeyProperty()
    pointRoot = ndb.KeyProperty()
    followReason = ndb.StringProperty()
    notificationReason = ndb.StringProperty()
    sourceUser = ndb.KeyProperty() # User who caused notification to be raised
    raisedDate = ndb.DateTimeProperty(auto_now_add=True)
    cleared = ndb.BooleanProperty(default=False)
    clearedDate = ndb.DateTimeProperty(default=None)
    
    @webapp2.cached_property
    def pointRootFull(self):
        return self.pointRoot.get()
        
    @webapp2.cached_property
    def sourceUserFull(self):
        return self.sourceUser.get()

    @webapp2.cached_property
    def referencePoint(self):
        return self.pointRootFull.getCurrent()
    
    @property
    def raisedDateSecs(self):
        epoch = datetime.datetime.utcfromtimestamp(0)
        delta = self.raisedDate - epoch  
        return int(delta.total_seconds())
       
    def timeText(self):        
        delta = datetime.datetime.now() - self.raisedDate
        delta_mins = delta.seconds / 60
        if delta_mins == 1:
            return "1 minute ago"
        elif delta_mins < 60:                    
            return "%d minutes ago" % delta_mins
        elif delta_mins < 1440:
            delta_hrs = int(delta_mins / 60)
            return "%d hours ago" % delta_hrs if delta_hrs != 1 else "1 hour ago"
        else:
            delta_days = int(delta_mins / 1440)
            return "%d days ago" % delta_days if delta_days != 1 else "1 day ago"

    @property
    def notificationMessage(self):
        path = os.path.join(constants.ROOT, 'templates/notificationMenu.html')
        notificationHTML = template.render(path, { 'notification': self})
        message = {
                    'notificationHTML': notificationHTML,
                    'timestamp': self.raisedDateSecs
                   }
        return json.dumps(message)

    @classmethod
    def createNotificationFromFollow(cls, follow, pointKey, userKey, notificationReason):
        n = Notification(targetUser=follow.user, 
                         pointRoot = pointKey,
                         followReason = follow.reason,
                         notificationReason=notificationReason,                         
                         sourceUser=userKey)
        n.put()
        targetUser = follow.user.get()
        if targetUser.token and targetUser.tokenExpires > datetime.datetime.now():
            channel.send_message(targetUser.token, n.notificationMessage)
        
    @classmethod
    def getActiveNotificationsForUser(cls, userKey):
        q = cls.query(ndb.AND(cls.targetUser == userKey, cls.cleared == False))
        q = q.order(-cls.raisedDate)     
        notifications = q.fetch(11)              
        return notifications
    
    @classmethod
    def getAllNotificationsForUser(cls, userKey):
        q = cls.query(cls.targetUser == userKey)
        q = q.order(-cls.raisedDate)     
        notifications = q.fetch(100)           
        return notifications
    
    @classmethod
    def clearNotifications(cls, userKey, latestTimestamp, earliestTimestamp=None):
        latest = datetime.datetime.fromtimestamp(latestTimestamp+1)        
        earliest = datetime.datetime.fromtimestamp(earliestTimestamp) if earliestTimestamp else None    
        if earliest:
            q = cls.query(ndb.AND(cls.targetUser == userKey, 
                                  cls.cleared == False, 
                                  cls.raisedDate <= latest,
                                  cls.raisedDate > earliest)) # EARLIEST TIMESTAMP REMAINS UNREAD
        else: 
            q = cls.query(ndb.AND(cls.targetUser == userKey, 
                                  cls.cleared == False, 
                                  cls.raisedDate <= latest))
            
        notifications = q.fetch(50)  
        logging.info('Clearing %d notifications. Latest: %s. Earliest %s. ' % (len(notifications), str(latest), str(earliest)))
        for n in notifications:
            n.cleared = True
            n.clearedDate = datetime.datetime.now()
            n.put()
                     



    
    