import constants
import os
import jinja2

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from django.template import Library
from google.appengine.ext import webapp

from webapp2 import Route, WSGIApplication

from google.appengine.ext.webapp.util import run_wsgi_app

from models.whysaurususer import WhysaurusUser
from handlers import MainPage, About, Help, Contact, Manifesto, ListSignUp, \
    Education, CommonCore, APUSH, Walkthrough, ContactSend, NewPoint,\
    DeletePoint, EditPoint, UnlinkPoint, ViewPoint, AddSupportingPoint,\
    LinkPoint, Vote, SetRibbon, TestPage, Search, \
    AjaxSearch, PointHistory, GetPointsList, AuthHandler, SetEditorPickSort, \
    UpdateSupportingPointsSchema, AaronTask, RebuildSearchIndex, \
    DBIntegrityCheck, Outliner, AddTree, Profile, AdminPage, Comments, \
    NotificationHandler, Chat, EventRecorder, CreatePrivateAreaPage, PointCard
from graphene_gae.webapp2 import GraphQLHandler
import schema

# Map URLs to handlers
routes = [
    Route('/', MainPage),
    Route('/graphql', GraphQLHandler),
    Route('/getMainPageLeft', 
          handler='WhySaurus.MainPage:getMainPageLeft', 
          name='getMainPageLeft'),
    Route('/getMainPageRight', 
          handler='WhySaurus.MainPage:getMainPageRight', 
          name='getMainPageRight'),
    Route('/about', About),
    Route('/manifesto', Manifesto),    
    Route('/listSignUp', ListSignUp),
    Route('/education', Education),
    Route('/commonCore', CommonCore),
    Route('/apushistory', APUSH),
    Route('/walkthrough', Walkthrough),
    Route('/team', About),
    Route('/help', Help),
    Route('/WhatIsWhysaurus', Help),
    Route('/contact', Contact),
    Route('/contactSend', ContactSend),
    Route('/newPoint', handler='WhySaurus.NewPoint:newPoint', name='newPoint'),
    Route('/deletePoint', DeletePoint),
    Route('/editPoint', EditPoint),
    Route('/changeEditorsPick', handler='WhySaurus.EditPoint:changeEditorsPick', name='changeEditorsPick'),
    Route('/makeFeatured', handler='WhySaurus.EditPoint:makeFeatured', name='makeFeatured'),
    Route('/refreshTopStatus', handler='WhySaurus.EditPoint:refreshTopStatus', name='refreshTopStatus'),
    Route('/unlinkPoint', UnlinkPoint),
    Route('/point/<pointURL>', ViewPoint),
    Route('/pointCard/<pointURL>', PointCard),
    Route('/api/point/<pointURL>',
          handler='WhySaurus.PointCard:apiPointGET',
          name='apiPointGET'),
    Route('/getPointContent', 
          handler='WhySaurus.ViewPoint:getPointContent', 
          name='getPointContent'),
    Route('/getPointComments', 
          handler='WhySaurus.ViewPoint:getPointComments', 
          name='getPointComments'),
    Route('/user/<userURL>', Profile),
    Route('/addSupportingPoint', AddSupportingPoint),
    Route('/linkPoint', LinkPoint),
    Route('/vote', Vote),
    Route('/relVote', handler='WhySaurus.Vote:relevanceVote', name='relevanceVote'),    
    Route('/setribbon', SetRibbon),
    Route('/search', Search),
    Route('/admin', AdminPage),
    Route('/roster', handler='WhySaurus.AdminPage:get_pa', name='get_pa'),    
    Route('/dailyReport', handler='WhySaurus.AdminPage:dailyReport', name='dailyReport'),    
    Route('/ajaxSearch', AjaxSearch),
    Route('/pointHistory', PointHistory),
    Route('/getPointCreator', handler='WhySaurus.PointHistory:getPointCreator', name='getPointCreator'), 
    Route('/getPointsList', GetPointsList),
    Route('/outliner', Outliner),
    Route('/addTree', AddTree),
    Route('/addNotifications', 
          handler='WhySaurus.NotificationHandler:AddNotification', name='addNotifications'),
    Route('/newNotificationChannel', 
          handler='WhySaurus.NotificationHandler:NewNotificationChannel', 
          name='newNotificationChannel'),
    Route('/clearNotifications', 
          handler='WhySaurus.NotificationHandler:ClearNotifications', 
          name='clearNotifications'),
    Route('/uploadUsers', handler='WhySaurus.AdminPage:uploadUsers', name='uploadUsers'),
    Route('/uploadUserPage', handler='WhySaurus.AdminPage:uploadUserPage', name='uploadUserPage'),
    Route('/job/testPage', TestPage),    
    Route('/job/setEditorPickSort', SetEditorPickSort),
    Route('/job/updateSupportingPointsSchema', UpdateSupportingPointsSchema),
    Route('/job/ArchiveAllComments', handler='WhySaurus.AaronTask:ArchiveAllComments'),  
    Route('/job/sendNotificationEmails', handler='WhySaurus.NotificationHandler:sendNotificationEmails'),  
    # Route('/job/MakeLinks', handler='WhySaurus.AaronTask:MakeLinks'),
    # Route('/job/MakeLinksAll', handler='WhySaurus.AaronTask:MakeLinksAllAreas'),    
    Route('/job/DBCheck', handler='WhySaurus.AaronTask:DBCheck'),   
    #Route('/DeleteDuplicateFollows', handler='WhySaurus.AaronTask:DeleteDuplicateFollows'),
    Route('/job/AaronTask', AaronTask),
    Route('/job/QueueTask', handler='WhySaurus.AaronTask:QueueTask', name='queueTask'),
    Route('/job/CalculateTopPoints', handler='WhySaurus.AaronTask:CalculateTopPoints'),
    Route('/job/RebuildSearchIndex', RebuildSearchIndex),
    Route('/job/DBIntegrityCheck', DBIntegrityCheck),
    Route('/job/addDBTask', 'WhySaurus.DBIntegrityCheck:addDBTask', name='addDBTask'),
    Route('/job/fixPoint/<pointURL>', 'WhySaurus.DBIntegrityCheck:fixPoint', name='fixPoint'),
    Route('/job/cleanDeadBacklinks/<pointURL>', 
          'WhySaurus.DBIntegrityCheck:cleanDeadBacklinks', 
          name='cleanDeadBacklinks'),
    Route('/job/cleanEmptyLinks/<pointURL>', 
          'WhySaurus.DBIntegrityCheck:cleanEmptyLinks', 
          name='cleanEmptyLinks'),
    Route('/job/addMissingBacklinks/<pointURL>', 
          'WhySaurus.DBIntegrityCheck:addMissingBacklinks', 
          name='addMissingBacklinks'),
    Route('/job/DBcheckPoint/<pointURL>', 
          'WhySaurus.DBIntegrityCheck:checkDBPoint', 
          name='checkDBPoint'),
    Route('/job/cleanCurrents/<pointURL>', 
          'WhySaurus.DBIntegrityCheck:cleanMultipleCurrent', 
          name='checkDBPoint'),
    Route('/enterChatRoom', handler='WhySaurus.Chat:enterChatRoom', 
          name='enterChatRoom'),
    Route('/leaveChatRoom', handler='WhySaurus.Chat:leaveChatRoom', 
          name='leaveChatRoom'),
    Route('/send', handler='WhySaurus.Chat:send', name='send'),
    Route('/broadcastChatroom', handler='WhySaurus.Chat:broadcastChatroom', 
          name='broadcastChatroom'),  
    Route('/recordEvent', handler='WhySaurus.EventRecorder:recordEvent', 
            name='recordEvent'),  
    # Private Areas
    Route('/switchArea/<area_name>', handler='WhySaurus.Profile:setArea', name='switchArea'),
    Route('/createArea', handler='WhySaurus.CreatePrivateAreaPage', name='createPrivateAreaPage'),
    Route('/area/<areaName>', handler='WhySaurus.AuthHandler:setPrivateAreaUser', name='setPrivateAreaUser'),
    Route('/saveComment', handler='WhySaurus.Comments:saveComment', name='saveComment'),
    Route('/archiveComments', handler='WhySaurus.Comments:archiveComments', name='archiveComments'),
    Route('/getArchivedComments', handler='WhySaurus.Comments:getArchivedComments', name='getArchivedComments'),    
    Route('/logout', handler='WhySaurus.AuthHandler:logout', name='logout'),
    Route('/signup', handler='WhySaurus.AuthHandler:signup', name='signup'),  
    Route('/login', handler='WhySaurus.AuthHandler:login', name='login'),  
    Route('/forgot', 'WhySaurus.AuthHandler:forgotPassword', name='forgot'),   
    Route('/password', 'WhySaurus.AuthHandler:changePassword', name='change'),
    Route('/resetPassword', 'WhySaurus.AuthHandler:resetPassword', name='change'),
    Route('/changePassword', 'WhySaurus.AuthHandler:passwordChangePage', name='changePage'),
    Route('/<type:v|p>/<user_id:\d+>-<signup_token:.+>',
                  handler='WhySaurus.AuthHandler:verify', name='verification'),
    Route('/auth/<provider>', handler='WhySaurus.AuthHandler:_simple_auth', name='auth_login'),
    Route('/auth/<provider>/callback', handler='WhySaurus.AuthHandler:_auth_callback', name='auth_callback'),
    
    Route('/.well-known/acme-challenge/<challenge>', handler='WhySaurus.AuthHandler:LetsEncryptHandler', name='letsEnrypt')
]

# webapp2 config
app_config = {
    'webapp2_extras.sessions': {
        'cookie_name': '_simpleauth_sess',
        'secret_key': constants.SESSION_KEY
    },
    'webapp2_extras.auth': {
        'user_attributes': [],
        'user_model': WhysaurusUser
    },
    'graphql_schema' : schema.schema
}


webapp.template.register_template_library('gae_mini_profiler.templatetags.profiler_tags')

app = WSGIApplication(routes=routes, config=app_config, debug=True)

if __name__ == '__main__':
    run_wsgi_app(app)
