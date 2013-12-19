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
    followReason = ndb.StringProperty(indexed=False)
    notificationReason = ndb.StringProperty(indexed=False)
    sourceUser = ndb.KeyProperty(indexed=False) # User who caused notification to be raised
    raisedDate = ndb.DateTimeProperty(auto_now_add=True)
    cleared = ndb.BooleanProperty(default=False)
    clearedDate = ndb.DateTimeProperty(default=None)
    additionalUserKeys = ndb.KeyProperty(repeated=True)
    notificationCategory = ndb.IntegerProperty() # Notifications are combined if they share a category
    
    
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
    def additionalUserCount(self):
        return len(self.additionalUsers)
        
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
                    'type': 'notification',
                    'notificationHTML': notificationHTML,
                    'timestamp': self.raisedDateSecs,
                    'pointURL': self.referencePoint.url,
                    'category': self.notificationCategory
                   }
        return json.dumps(message)

    @classmethod
    def getNotificationCategory(cls, reason):
        if reason == "edited":
            return 1
        elif reason == "agreed with" or reason == "awarded a ribbon to":
            return 2
        elif reason == "unlinked a supporting point" or reason == "unlinked a counter point":
            return 1
        elif reason == "commented on":    
            return 3
        else:
            return 4
            
    @classmethod
    def createNotificationFromFollow(cls, follow, pointKey, userKey, notificationReason):
        try:
            n = Notification.getSimilarNotification(
                    follow.user, 
                    pointKey, 
                    Notification.getNotificationCategory(notificationReason)
                )

            if n:               
                 
                if userKey != n.sourceUser:
                    logging.info('NCFF ' + 'not equal')
                    if not hasattr(n, 'additionalUsers') or n.additionalUsers is None:
                        n.additionalUsers = [userKey]
                    elif userKey not in n.additionalUsers: # A new user has triggered the notification
                        n.additionalUsers.push(userKey)
                
                n.raisedDate = datetime.datetime.now()

            else:
                n = Notification(targetUser=follow.user, 
                                 pointRoot = pointKey,
                                 followReason = follow.reason,
                                 notificationReason=notificationReason,                         
                                 sourceUser=userKey,
                                 notificationCategory=
                                     Notification.getNotificationCategory(
                                         notificationReason)
                                )
            n.put()
            targetUser = follow.user.get()
            if targetUser.token and targetUser.tokenExpires > datetime.datetime.now():
                channel.send_message(targetUser.token, n.notificationMessage)
                
        except Exception, e:
            logging.exception(e)
        
    @classmethod
    def getActiveNotificationsForUser(cls, userKey):
        q = cls.query(ndb.AND(cls.targetUser == userKey))
        q = q.order(-cls.raisedDate)     
        notifications = q.fetch(11)      
        newCount = sum(1 for n in notifications if not n.cleared)        
        moreExist = len(notifications) == 11
        return notifications[0:10], newCount, moreExist
    
    @classmethod
    def getAllNotificationsForUser(cls, userKey):
        q = cls.query(cls.targetUser == userKey)
        q = q.order(-cls.raisedDate)     
        notifications = q.fetch(100)           
        return notifications
    
    @classmethod
    def getSimilarNotification(cls, userKey, pointRootKey, category):
        q = cls.query(cls.targetUser == userKey).filter(cls.pointRoot == pointRootKey)
        q = q.filter(cls.cleared==False)
        q = q.filter(cls.notificationCategory==category)
        notification = q.fetch(1)
        return notification[0] if notification else None
        
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
                     



    
    