import os
import constants
import logging
import json

from google.appengine.ext.webapp import template
from authhandler import AuthHandler
from models.whysaurususer import WhysaurusUser
from models.privateArea import PrivateArea
from models.whysaurusexception import WhysaurusException

class AdminPage(AuthHandler):
    def createPrivateArea(self, newName):
        results = {'result': False}
        try:
            PrivateArea.create(newName) 
            results = {
                'result': True,
                'newNamespace': newName
            }
        except WhysaurusException as e:
            results['error'] = str(e)
        else:
            results['error'] = "New name must not be longer that 100 and may only include alphanumeric characters and . - _"
        return results
    
    def saveUsers(self, users):
        for user in users:
            u = WhysaurusUser.getByUrl(user['url'])
            if u:
                u.updatePrivateArea(user['newPrivateArea'])
            else:
                results = {
                    'result': False, 
                    'error': "COuld not find user %s. Other users may have been updated." % user['userAuthIDs']
                } 
                return results       
        return {'result': True}

    
    def post(self):
        results = {'result': False}
        user = self.current_user  
        if user.admin:
            action=self.request.get('action')
            if (action == 'createPrivateArea'):
                newName=self.request.get('privateAreaName')
                results = self.createPrivateArea(newName)
            elif (action == 'saveUsers'): 
                users = json.loads(self.request.get('newUserValues'))
                results = self.saveUsers(users)
        else:
            results['error'] = "User must be admin."
        resultJSON = json.dumps(results)
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)
          
    
    def get(self):
        user = self.current_user
        queryUsr = WhysaurusUser.query()
        areas = PrivateArea.query().fetch(50)
        users = []
        i = 0
        for yUser in queryUsr.iter():            
            users = users + [{'u':yUser, 'index':i, 'userKey': yUser.key.urlsafe()}]
            i = i+1
        template_values = {
            'user': user,
            'users': users,
            'areas': areas
        }

        if user and user.admin:                
            path = os.path.join(constants.ROOT, 'templates/admin.html')
            self.response.out.write(template.render(path, template_values)) 
        else:
            self.response.out.write('User not authorized. ')
            
            
            