import os
import constants
import logging
import json
import string

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from authhandler import AuthHandler
from models.whysaurususer import WhysaurusUser
from models.privateArea import PrivateArea
from models.areauser import AreaUser
from models.whysaurusexception import WhysaurusException
from models.reportEvent import DayEventSummary
from google.appengine.api import namespace_manager


class AssignmentHandler(AuthHandler):
    def newAssignmentPage(self):        
        user = self.current_user
        userNamespace = namespace_manager.get_namespace()        
        
        if user is None:
            self.response.out.write('Need to login.')
            return
            
        if ((not userNamespace) or (userNamespace == '')):
            self.response.out.write('Need to be in a private area.')
            return
                                     
        template_values = {
            'user': user,
            'currentArea':userNamespace,
            'currentAreaDisplayName': self.session.get('currentAreaDisplayName')
        }
        
        self.response.out.write(
            self.template_render('newAssignment.html', template_values))

