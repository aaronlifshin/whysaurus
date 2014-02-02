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
    notificationReasonCode = ndb.IntegerProperty()
    notificationReason = ndb.StringProperty()
    sourceUser = ndb.KeyProperty(indexed=False) # User who caused notification to be raised
    raisedDate = ndb.DateTimeProperty(auto_now_add=True)
    cleared = ndb.BooleanProperty(default=False)
    clearedDate = ndb.DateTimeProperty(default=None)
    additionalUserKeys = ndb.KeyProperty(repeated=True)
    additionalActions = ndb.IntegerProperty(indexed=False, default=0)    
    additionalText = ndb.StringProperty(indexed=False, default=None)
    
    @webapp2.cached_property
    def pointRootFull(self):
        return self.pointRoot.get()
        
    @webapp2.cached_property
    def sourceUserFull(self):
        return self.sourceUser.get()

    @webapp2.cached_property
    def referencePoint(self):
        return self.pointRootFull.getCurrent()
    
    def additionalUserCount(self):
        return len(self.additionalUserKeys)
        
    @property
    def notificationReasonText(self):
        c = self.notificationReasonCode
        plural = False
        if hasattr(self, 'additionalUserKeys') and self.additionalUserKeys:
            plural = True
        if hasattr(self, 'additionalActions') and self.additionalActions != 0:
            plural = True            
            
        if c == 0:
            return "edited"
        elif c == 1:
            return "agreed with"
        elif c == 2:
            return "awarded a ribbon to"
        elif c == 3:
            return "commented on"
        elif c == 4:
            return "added supporting points to" if plural else "added a supporting point to"
        elif c == 5:
            return "added counter points to" if plural else "added a counter point to"
        elif c == 6:
            return "unlinked counter points from" if plural else "unlinked a counter point from"
        elif c == 7:
            return "unlinked supporting points from" if plural else "unlinked a supporting point from"
        else:
            return "changed" # could raise exception here instead?
        
    @property
    def raisedDateSecs(self):
        epoch = datetime.datetime.utcfromtimestamp(0)
        delta = self.raisedDate - epoch  
        return int(delta.total_seconds())        
       
    def timeText(self):        
        delta = datetime.datetime.now() - self.raisedDate
        delta_mins = delta.total_seconds() / 60
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
        notificationHTML = self.handler.template_render(
            'notificationMenu.html', 
            { 'notification': self})
        message = {
                    'type': 'notification',
                    'notificationHTML': notificationHTML,
                    'timestamp': self.raisedDateSecs,
                    'pointURL': self.referencePoint.url,
                    'notificationReasonCode': self.notificationReasonCode
                   }
        return json.dumps(message)
            
    @classmethod
    def createNotificationFromFollow(cls, handler, follow, pointKey, userKey, notificationReasonCode, additionalText=None):
        try:
            if notificationReasonCode == 3: # commented on does not "stack" with similar notifications
                n = None
            else:
                n = Notification.getSimilarNotification(
                        follow.user, 
                        pointKey,
                        notificationReasonCode )

            if n:                                
                if userKey != n.sourceUser:
                    if not hasattr(n, 'additionalUserKeys') or n.additionalUserKeys is None:
                        n.additionalUserKeys = [userKey]
                    elif userKey not in n.additionalUserKeys: 
                        # A new user has triggered the notification
                        n.additionalUserKeys =  n.additionalUserKeys + [userKey]
                else:
                    logging.info('NCFF ' + 'adding an action')                    
                    # additional actions by the initial user that caused the notification
                    n.additionalActions = n.additionalActions + 1 if n.additionalActions else 1
                
                n.raisedDate = datetime.datetime.now()
                if n.additionalText and additionalText:
                    n.additionalText = n.additionalText + "; " + additionalText

            else:
                n = Notification(targetUser=follow.user, 
                                 pointRoot = pointKey,
                                 followReason = follow.reason,
                                 notificationReasonCode=notificationReasonCode,                         
                                 sourceUser=userKey,                          
                                 additionalText = additionalText                                 
                                )
            n.put()
            targetUser = follow.user.get()
            if targetUser.token and targetUser.tokenExpires > datetime.datetime.now():
                n.handler = handler
                channel.send_message(targetUser.token, n.notificationMessage)
                
        except Exception, e:
            logging.exception(e)
        
    @classmethod
    def getLatestNotificationsForUser(cls, userKey):
        q = cls.query(cls.targetUser == userKey)
        q = q.order(-cls.raisedDate)     
        notifications = q.fetch(11)      
        newCount = sum(1 for n in notifications if not n.cleared)        
        moreExist = len(notifications) == 11
        return notifications[0:10], newCount, moreExist 
        
    @classmethod
    def getUnreadNotificationsForUser(cls, userKey):
        q = cls.query(ndb.AND(cls.targetUser == userKey, cls.cleared==False))        
        q = q.order(-cls.raisedDate)     
        notifications = q.fetch(11)      
        newCount = len(notifications)        
        moreExist = len(notifications) == 11
        return notifications[0:10], newCount, moreExist  
           
    @classmethod
    def getAllNotificationsForUser(cls, userKey):
        q = cls.query(cls.targetUser == userKey)
        q = q.order(-cls.raisedDate)     
        notifications = q.fetch(100)           
        return notifications
    
    @classmethod
    def getSimilarNotification(cls, userKey, pointRootKey, reasonCode):
        q = cls.query(cls.targetUser == userKey).filter(cls.pointRoot == pointRootKey)
        q = q.filter(cls.cleared==False)
        q = q.filter(cls.notificationReasonCode==int(reasonCode))
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
                     



    
    