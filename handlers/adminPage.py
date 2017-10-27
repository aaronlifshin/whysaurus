import os
import constants
import logging
import json
import string

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from authhandler import AuthHandler
from models.whysaurususer import WhysaurusUser
from models.privateArea import PrivateArea
from models.areauser import AreaUser
from models.whysaurusexception import WhysaurusException
from models.reportEvent import DayEventSummary
from google.appengine.api import namespace_manager


class AdminPage(AuthHandler):
    def createPrivateArea(self, newName, newDisplayName):
        results = {'result': False}
        try:
            PrivateArea.create(newName, newDisplayName) 
            results = {
                'result': True,
                'newNamespace': newName
            }
        except WhysaurusException as e:
            results['error'] = str(e)     
        
        return results
    
    def saveUsers(self, users):

        for user in users:
            u = WhysaurusUser.getByUrl(user['url'])
            if u:
                u.updateUserSettings(user['privateAreas'], user['role'])
            else:
                results = {
                    'result': False, 
                    'error': "Could not find user %s. Other users may have been updated." % user['userAuthIDs']
                } 
                return results     
        
        return {'result': True}

    
    def post(self):
        
        userNamespace = namespace_manager.get_namespace()        
        namespace_manager.set_namespace('')

        
        results = {'result': False}
        user = self.current_user  
        
        action=self.request.get('action')
        if (action == 'createPrivateArea'):
            # Anyone can create a private area
            newName = self.request.get('privateAreaName')
            newDisplayName = self.request.get('privateAreaDisplayName')
            results = self.createPrivateArea(newName, newDisplayName)
        elif (action == 'saveUsers'): 
            if user.isAdmin:
                users = json.loads(self.request.get('newUserValues'))
                results = self.saveUsers(users)
            else:
                results['error'] = "User must be admin."
        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
        
        namespace_manager.set_namespace(userNamespace)   
          
    
    def get(self):
        userNamespace = namespace_manager.get_namespace()        
        namespace_manager.set_namespace('')
   
        user = self.current_user
        if user is None:
            self.response.out.write('Need to login.')
            return

        if not user.isAdmin:
            self.response.out.write('User not authorized.')
            return

        queryUsr = WhysaurusUser.query().order(-WhysaurusUser.lastLogin)
        areas = PrivateArea.query()
        users = []
        i = 0
        for yUser in queryUsr.iter():
            users = users + [{'u':yUser, 'index':i, 'userKey': yUser.key.urlsafe()}]
            i = i+1
            
        paginator = Paginator(users, 25) 
        page = self.request.get('page')

        try:
            paginatedUsers = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            paginatedUsers = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            paginatedUsers = paginator.page(paginator.num_pages)

            
        template_values = {
            'user': user,
            'users': paginatedUsers,
            'areas': areas,
            'currentArea':self.session.get('currentArea'),
            'currentAreaDisplayName':self.session.get('currentAreaDisplayName')
        }

        self.response.out.write(
            self.template_render('admin.html', template_values))

        namespace_manager.set_namespace(userNamespace)

    def adminTest(self):
        user = self.current_user

        if user.canSendUserEmail():
            logging.info('Sending Admin Test Email: %s' % user.name)
            user.sendUserNotificationEmailTest()
        else:
            logging.info('Unable To Send User Email For Admin Test: %s' % user.name)

    def uploadUserPage(self):

        userNamespace = namespace_manager.get_namespace()        
        namespace_manager.set_namespace('')

        areas = PrivateArea.query()        
        user = self.current_user

        template_values = {
            'user': user,
            'areas':areas,
            'currentArea':self.session.get('currentArea'),
            'currentAreaDisplayName':self.session.get('currentAreaDisplayName')
        }
        if user and user.isAdmin:                
            self.response.out.write(
                self.template_render('uploadUsers.html', template_values)) 
        else:
            self.response.out.write('User not authorized. ')
            
        namespace_manager.set_namespace(userNamespace)       
        
        
    def uploadUsers(self):

        userNamespace = namespace_manager.get_namespace()        
        namespace_manager.set_namespace('')
        
        loggedInUser = self.current_user
        if loggedInUser and loggedInUser.isAdmin:                    
            userNames=self.request.get('userNames')
            privateArea = self.request.get('areaToAdd')
            userLines = string.split(userNames, '\n')
            
            bigMessage = []
            if privateArea:
              bigMessage.append('Creating users in classroom %s' % privateArea)
            bigMessage.append('username,password')
            for userLine in userLines:
                userFields = string.split(userLine, ',')
                numFields = len(userFields)
                username = userFields[0].strip()
                try:
                    newPassword = ''
                    if numFields == 1:                      
                      newPassword = WhysaurusUser.random_password(8)
                    else:
                      newPassword = userFields[1].strip()
                    if username != '':
                      user = WhysaurusUser.signup(self, email=username, name=username, 
                                                  password=newPassword, website=None, areas=None, 
                                                  profession=None, bio=None)
                      user.updateUserSettings([privateArea])
                      bigMessage.append('%s,%s' % ( username, newPassword))
                except WhysaurusException as e:
                    bigMessage.append('Could not create user: %s. Error was:%s' % (username, str(e)))
                
            template_values = {
                'user': loggedInUser,
                'messages': bigMessage
            }    
            self.response.out.write(
                self.template_render('message.html', template_values))   
        else:
            self.response.out.write('User not authorized. ')

        namespace_manager.set_namespace(userNamespace)
            
    def dailyReport(self):
        user = self.current_user      
        if user and user.isAdmin:    
            template_values = {
                'user': user,
                'dayReportTable': DayEventSummary.getReport()
            }   
            self.response.out.write(
                self.template_render('dailyReport.html', template_values))        

                
    def get_pa(self):
        userNamespace = namespace_manager.get_namespace()        
        namespace_manager.set_namespace('')
        
        user = self.current_user
        if user is None:
            self.response.out.write('Need to login.')
            return

        userIds = []
        queryUsrIds = AreaUser.query().filter(AreaUser.privateArea == userNamespace)
        for userArea in queryUsrIds.iter():
            userIds.append(ndb.Key(urlsafe=userArea.userKey))
                        
        queryUsr = ndb.get_multi(userIds)
        users = []
        i = 0        
        for yUser in queryUsr:
            if yUser.isAdmin != True:
                users = users + [{'u':yUser, 'index':i, 'userKey': yUser.key.urlsafe()}]
                i = i+1

        paginator = Paginator(users, 35) 
        page = self.request.get('page')

        try:
            paginatedUsers = paginator.page(page)
        except PageNotAnInteger:
            paginatedUsers = paginator.page(1)
        except EmptyPage:
            paginatedUsers = paginator.page(paginator.num_pages)
                    
        template_values = {
            'user': user,
            'users': paginatedUsers,
            'currentArea':userNamespace,
            'currentAreaDisplayName': self.session.get('currentAreaDisplayName')
        }
        
        namespace_manager.set_namespace(userNamespace)   
        self.response.out.write(
            self.template_render('adminPrivateArea.html', template_values))
                