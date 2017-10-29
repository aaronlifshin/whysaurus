# appengine_config.py
from google.appengine.ext import vendor

remoteapi_CUSTOM_ENVIRONMENT_AUTHENTICATION = (
    'HTTP_X_APPENGINE_INBOUND_APPID', ['whysaurus'])

appstats_CALC_RPC_COSTS = True

vendor.add('lib')

def webapp_add_wsgi_middleware(app):
  from google.appengine.ext.appstats import recording
  import gae_mini_profiler.profiler   
  app = gae_mini_profiler.profiler.ProfilerWSGIMiddleware(app)      
  app = recording.appstats_wsgi_middleware(app)
  return app

def gae_mini_profiler_should_profile_production():
    #from google.appengine.api import users
    #return users.is_current_user_admin()
    return False
      
def gae_mini_profiler_should_profile_development():
    return True
