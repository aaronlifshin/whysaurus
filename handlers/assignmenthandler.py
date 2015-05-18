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
from models.assignment import Assignment
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
            self.response.out.write('Need to be in a classroom.')
            return
                                     
        template_values = {
            'user': user,
            'currentArea':userNamespace,
            'currentAreaDisplayName': self.session.get('currentAreaDisplayName')
        }
        
        self.response.out.write(
            self.template_render('newAssignment.html', template_values))

    def saveAssignment(self, assignmentData):
        userNamespace = namespace_manager.get_namespace()   
        results = {'result': False}
                     
        if (userNamespace == '' ):
            results['error'] = "Must be inside of a classroom to create assignemnt."
        else:
            pa = PrivateArea.getAreaByName(userNamespace)
            if pa:
                logging.info(str(assignmentData))
                Assignment.addAssignment(
                    assignmentData['title'], 
                    assignmentData['summary'], 
                    assignmentData['directions'], 
                    assignmentData['documents'])
                results = {'result': True}
            else:
                results['error'] = "Could not find classroom."                
        return results
        
    def assignmentList(self):
        if 'currentAssignment' in self.session: del self.session['currentAssignment']

        user = self.current_user
        userNamespace = namespace_manager.get_namespace()        
        
        if user is None:
            self.response.out.write('Need to login.')
            return
            
        if ((not userNamespace) or (userNamespace == '')):
            self.response.out.write('Need to be in a classroom.')
            return
                           
        assignments = Assignment.getAll()
        logging.info(str(assignments))
        
        template_values = {
            'user': user,
            'currentArea':userNamespace,
            'assignments': assignments,            
            'currentAreaDisplayName': self.session.get('currentAreaDisplayName')
        }
        
        self.response.out.write(
            self.template_render('assignmentList.html', template_values))

    def post(self):        
        userNamespace = namespace_manager.get_namespace()                
        results = {'result': False}
        user = self.current_user  
        
        action=self.request.get('action')
        if (action == 'saveAssignment'): 
            if user.isAdmin or user.isTeacher:
                documentData = json.loads(self.request.get('assignmentData'))
                results = self.saveAssignment(documentData)
            else:
                results['error'] = "User must be admin or teacher."
        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
        