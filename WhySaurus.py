import constants

from webapp2 import Route, WSGIApplication

from google.appengine.ext.webapp.util import run_wsgi_app

from models.whysaurususer import WhysaurusUser
from handlers import MainPage, About, Help, Contact, ContactSend, NewPoint,\
    DeletePoint, EditPoint, UnlinkPoint, ViewPoint, AddSupportingPoint,\
    SelectSupportingPoint, LinkPoint, Vote, SetRibbon, TestPage, Search, \
    AjaxSearch, PointHistory, GetPointsList, AuthHandler, SetEditorPickSort, \
    UpdateSupportingPointsSchema, AaronTask, RebuildSearchIndex, \
    DBIntegrityCheck, Outliner, AddTree, Profile, AdminPage, Comments, \
    NotificationHandler
    
    

# Map URLs to handlers
routes = [
    Route('/', MainPage),
    Route('/about', About),
    Route('/help', Help),
    Route('/contact', Contact),
    Route('/contactSend', ContactSend),
    Route('/newPoint', NewPoint),
    Route('/deletePoint', DeletePoint),
    Route('/editPoint', EditPoint),
    Route('/unlinkPoint', UnlinkPoint),
    Route('/point/<pointURL>', ViewPoint),
    Route('/user/<userURL>', Profile),
    Route('/addSupportingPoint', AddSupportingPoint),
    Route('/selectSupportingPoint', SelectSupportingPoint),
    Route('/linkPoint', LinkPoint),
    Route('/vote', Vote),
    Route('/setribbon', SetRibbon),
    Route('/testPage', TestPage),
    Route('/search', Search),
    Route('/admin', AdminPage),
    Route('/ajaxSearch', AjaxSearch),
    Route('/pointHistory', PointHistory),
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
    Route('/job/setEditorPickSort', SetEditorPickSort),
    Route('/job/updateSupportingPointsSchema', UpdateSupportingPointsSchema),
    Route('/MakeFollows', handler='WhySaurus.AaronTask:MakeFollows'),
    #Route('/DeleteDuplicateFollows', handler='WhySaurus.AaronTask:DeleteDuplicateFollows'),
    Route('/job/AaronTask', AaronTask),
    Route('/job/QueueTask', handler='WhySaurus.AaronTask:QueueTask', name='queueTask'),
    Route('/job/RebuildSearchIndex', RebuildSearchIndex),
    Route('/job/DBIntegrityCheck', DBIntegrityCheck),
    Route('/job/addDBTask', 'WhySaurus.DBIntegrityCheck:addDBTask', name='addDBTask'),
    Route('/job/fixPoint/<pointURL>', 'WhySaurus.DBIntegrityCheck:fixPoint', name='fixPoint'),
    Route('/job/cleanDeadBacklinks/<pointURL>', 
          'WhySaurus.DBIntegrityCheck:cleanDeadBacklinks', 
          name='cleanDeadBacklinks'),
    Route('/job/reconcileVersionArrays/<pointURL>', 
          'WhySaurus.DBIntegrityCheck:reconcileVersionArrays', 
          name='reconcileVersionArrays'),
    Route('/job/addMissingBacklinks/<pointURL>', 
          'WhySaurus.DBIntegrityCheck:addMissingBacklinks', 
          name='addMissingBacklinks'),
    Route('/switchArea', handler='WhySaurus.Profile:setArea', name='switchArea'),
    Route('/saveComment', handler='WhySaurus.Comments:saveComment', name='saveComment'),
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
    Route('/auth/<provider>/callback', handler='WhySaurus.AuthHandler:_auth_callback', name='auth_callback')
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
    }
}

app = WSGIApplication(routes=routes, config=app_config, debug=True)

if __name__ == '__main__':
    run_wsgi_app(app)
