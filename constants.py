import os

# This is a session secret key used by webapp2 framework.
# Get 'a random and long string' from here:
# http://clsc.net/tools/random-string-generator.php
# or execute this from a python shell: import os; os.urandom(64)
SESSION_KEY = "\x13f\xdaE\x86\xa7#\xe2\xd5\xd7\x04\x84\x18<\xe9\xbc9o\xa4\xb9?\x19\xe9Ie\xfd\xec~\xee\x03\xae]\xf7g\xcc^6\xa7i\xe0\x1a\xfa\xa3\xf7<\rk]'\xde6\xa8\xf5,u\x00Q;\x101\xd9\xc42\xd2"


DEV = os.environ['SERVER_SOFTWARE'].startswith('Development')

if DEV:
    FACEBOOK_APP_ID = '460138394028773'
    FACEBOOK_APP_SECRET = 'ae64953822e937d9fed9daaa959390e9'
    FACEBOOK_CHANNEL_URL = '//localhost:8081/channel.html'
    GOOGLE_APP_ID = '730565153520.apps.googleusercontent.com'
    GOOGLE_APP_SECRET = 'hf4EB8dYf0NwfSJ04BVjak51'
else:
    FACEBOOK_APP_ID = '144595249045851'
    FACEBOOK_APP_SECRET = '0e837314cd9c8a181a077ada99866780'
    FACEBOOK_CHANNEL_URL = 'http://www.whysaurus.com/channel.html'
    GOOGLE_APP_ID = '341009833131.apps.googleusercontent.com'
    GOOGLE_APP_SECRET = 'Xp9EaXzljKhNwL549DuVzBdY'
TWITTER_APP_ID = '4063892'
TWITTER_APP_SECRET = 'VrFcSJpKa2vcPFOJUbQWeiL5oRPbq3Iiu3XFw2t1zoo'

# https://www.linkedin.com/secure/developer
# THIS IS DEPRECATED FOR NOW
LINKEDIN_CONSUMER_KEY = 'consumer key'
LINKEDIN_CONSUMER_SECRET = 'consumer secret'

# https://manage.dev.live.com/AddApplication.aspx
# https://manage.dev.live.com/Applications/Index
WL_CLIENT_ID = 'client id'
WL_CLIENT_SECRET = 'client secret'

# https://dev.twitter.com/apps
TWITTER_CONSUMER_KEY = 'xd43iFkn6CJISe5I8lbA'
TWITTER_CONSUMER_SECRET = 'VrFcSJpKa2vcPFOJUbQWeiL5oRPbq3Iiu3XFw2t1zoo'

# config that summarizes the above
AUTH_CONFIG = {
    # OAuth 2.0 providers
    'google': (GOOGLE_APP_ID, GOOGLE_APP_SECRET,
               'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email'),
    'facebook': (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET,
                 'user_about_me email'),
    'windows_live': (WL_CLIENT_ID, WL_CLIENT_SECRET,
                     'wl.signin'),

    # OAuth 1.0 providers don't have scopes
    'twitter': (TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET),
    'linkedin': (LINKEDIN_CONSUMER_KEY, LINKEDIN_CONSUMER_SECRET),

    # OpenID doesn't need any key/secret
}

SCORETHRESHOLDS = {
    'green': 2,
    'red': -2
}
