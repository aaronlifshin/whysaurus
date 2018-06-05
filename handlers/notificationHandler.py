import json
import logging
from google.appengine.ext import ndb
from google.appengine.api import app_identity

from authhandler import AuthHandler
from models.whysaurususer import WhysaurusUser
from models.whysaurusexception import WhysaurusException
from models.timezones import PST
from models.notification import Notification
from models.follow import Follow

class NotificationHandler(AuthHandler):
    # This is called by the task queue
    def AddNotification(self):
        rootKeyUrlsafe = self.request.get('rootKey')
        notifyReasonCode = self.request.get('notifyReasonCode')
        sourceUserUrlsafe = self.request.get('userKey')
        additionalText = self.request.get('additionalText')

        pointRootKey = ndb.Key(urlsafe=rootKeyUrlsafe)
        sourceUserKey = ndb.Key(urlsafe=sourceUserUrlsafe)
        follows = Follow.getActiveFollowsForPoint(pointRootKey)

        for f in follows:
            if f.user != sourceUserKey:
                Notification.createNotificationFromFollow(self,
                                                          f, pointRootKey,
                                                          sourceUserKey,
                                                          int(notifyReasonCode),
                                                          additionalText,
                                                           )

    def NewNotificationChannel(self):
        user = self.current_user
        results = {'result': False}
        if not user:
            results = {'result': False, 'error': 'User not logged in'}
        else:
            # user.createChannel(saveUser=True)
            results = {'result': True, 'token': user.token}
        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)


    def ClearNotifications(self):
        user = self.current_user
        latestTimestamp = self.request.get('latest')
        earliestTimestamp = self.request.get('earliest')
        results = {'result': False}
        if not user:
            results = {'result': False, 'error': 'User not logged in'}
        else:
            user.clearNotifications(float(latestTimestamp),
                                    float(earliestTimestamp) if earliestTimestamp else None)
            results = {'result': True}
        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)

    # send the notification emails
    # this one is protected by login:admin and called from the cron job
    # so it doesn't check user inside the handler
    def sendNotificationEmails(self):
        appId = app_identity.get_application_id()
        logging.info('GAE App Id: %s' % appId)
        if appId != 'whysaurus':
            logging.warning('Bypassing email notifications outside primary app. App Id: %s' % appId)
            self.response.out.write('Bypass!')
            return
        WhysaurusUser.sendNotificationEmails(self)
        self.response.out.write('') # succeed!

    def sendSingleNotificationEmail(self):
        user = self.current_user
        logging.info('Sending notification email for user %s' % user.name)
        user.sendSingleNotificationEmail(self)
        self.response.out.write('')  # succeed!
