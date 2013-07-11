import fix_path
import constants

from webapp2 import Route, WSGIApplication

from google.appengine.ext.webapp.util import run_wsgi_app

from models.whysaurususer import WhysaurusUser
from handlers import MainPage, About, Help, Contact, ContactSend, NewPoint,\
    DeletePoint, EditPoint, UnlinkPoint, ViewPoint, AddSupportingPoint,\
    SelectSupportingPoint, LinkPoint, Vote, SetRibbon, TestPage, Search, AjaxSearch,\
    PointHistory, GetPointsList, AuthHandler, SetEditorPickSort, UpdateSupportingPointsSchema, \
    AaronTask, DBIntegrityCheck
    

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
    Route('/addSupportingPoint', AddSupportingPoint),
    Route('/selectSupportingPoint', SelectSupportingPoint),
    Route('/linkPoint', LinkPoint),
    Route('/vote', Vote),
    Route('/setribbon', SetRibbon),
    Route('/testPage', TestPage),
    Route('/search', Search),
    Route('/ajaxSearch', AjaxSearch),
    Route('/pointHistory', PointHistory),
    Route('/getPointsList', GetPointsList),
    Route('/job/setEditorPickSort', SetEditorPickSort),
    Route('/job/updateSupportingPointsSchema', UpdateSupportingPointsSchema),
    Route('/job/AaronTask', AaronTask),
    Route('/job/DBIntegrityCheck', DBIntegrityCheck),
    # Route('/profile', handler='handlers.ProfileHandler', name='profile'),
    Route('/logout', handler='WhySaurus.AuthHandler:logout', name='logout'),  # , handler_method='logout', name='logout'),
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
