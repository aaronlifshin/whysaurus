import logging
import traceback

from authhandler import AuthHandler
from models.reportEvent import ReportEvent
from google.appengine.api.taskqueue import Task

class EventRecorder(AuthHandler):
    def recordEvent(self):
        userKeyUrlsafe = self.request.get('userKeyUrlsafe')
        entityKey1Urlsafe = self.request.get('entityKey1Urlsafe')
        entityKey2Urlsafe = self.request.get('entityKey2Urlsafe')
        eventName = self.request.get('eventName')
        
        ReportEvent.recordEvent(userKeyUrlsafe, entityKey1Urlsafe, entityKey2Urlsafe, eventName )