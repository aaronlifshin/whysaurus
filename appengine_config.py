remoteapi_CUSTOM_ENVIRONMENT_AUTHENTICATION = (
    'HTTP_X_APPENGINE_INBOUND_APPID', ['whysaurus-beta'])

appstats_CALC_RPC_COSTS = True

def webapp_add_wsgi_middleware(app):
  from google.appengine.ext.appstats import recording
  app = recording.appstats_wsgi_middleware(app)
  return app

def gae_mini_profiler_should_profile_production():
    #from google.appengine.api import users
    #return users.is_current_user_admin()
    return False
      
def gae_mini_profiler_should_profile_development():    
    return True
    
    
