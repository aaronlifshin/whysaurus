import os

# This is a session secret key used by webapp2 framework.
# Get 'a random and long string' from here: 
# http://clsc.net/tools/random-string-generator.php
# or execute this from a python shell: import os; os.urandom(64)
SESSION_KEY = "\x13f\xdaE\x86\xa7#\xe2\xd5\xd7\x04\x84\x18<\xe9\xbc9o\xa4\xb9?\x19\xe9Ie\xfd\xec~\xee\x03\xae]\xf7g\xcc^6\xa7i\xe0\x1a\xfa\xa3\xf7<\rk]'\xde6\xa8\xf5,u\x00Q;\x101\xd9\xc42\xd2"

# Google APIs
GOOGLE_APP_ID = '730565153520.apps.googleusercontent.com'
GOOGLE_APP_SECRET = 'hf4EB8dYf0NwfSJ04BVjak51'

DEV = os.environ['SERVER_SOFTWARE'].startswith('Development')
# Facebook auth apis
if DEV:
    FACEBOOK_APP_ID  = '460138394028773'
    FACEBOOK_APP_SECRET = 'ae64953822e937d9fed9daaa959390e9'
    FACEBOOK_CHANNEL_URL = '//localhost:8081/channel.html'
else:
    FACEBOOK_APP_ID = '437336826315160'
    FACEBOOK_APP_SECRET = 'd09e82124bccb0336237f2b62a5187c4'
    FACEBOOK_CHANNEL_URL = 'http://whysaurus-beta.appspot.com/channel.html'

# https://www.linkedin.com/secure/developer
LINKEDIN_CONSUMER_KEY = 'consumer key'
LINKEDIN_CONSUMER_SECRET = 'consumer secret'

# https://manage.dev.live.com/AddApplication.aspx
# https://manage.dev.live.com/Applications/Index
WL_CLIENT_ID = 'client id'
WL_CLIENT_SECRET = 'client secret'

# https://dev.twitter.com/apps
TWITTER_CONSUMER_KEY = 'oauth1.0a consumer key'
TWITTER_CONSUMER_SECRET = 'oauth1.0a consumer secret'

# config that summarizes the above
AUTH_CONFIG = {
  # OAuth 2.0 providers
  'google'      : (GOOGLE_APP_ID, GOOGLE_APP_SECRET,
                  'https://www.googleapis.com/auth/userinfo.profile'),
  'facebook'    : (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET,
                  'user_about_me'),
  'windows_live': (WL_CLIENT_ID, WL_CLIENT_SECRET,
                  'wl.signin'),

  # OAuth 1.0 providers don't have scopes
  'twitter'     : (TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET),
  'linkedin'    : (LINKEDIN_CONSUMER_KEY, LINKEDIN_CONSUMER_SECRET),

  # OpenID doesn't need any key/secret
}