import re
import time
import logging
import random
import string

from google.appengine.ext import ndb
import webapp2_extras.appengine.auth.models as auth_models
from webapp2_extras import security
from google.appengine.api import namespace_manager
from google.appengine.api import mail


from whysaurusexception import WhysaurusException
from uservote import UserVote

class WhysaurusUser(auth_models.User):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    url = ndb.StringProperty(default=None)
    numCopies = ndb.IntegerProperty(default=0)
    admin = ndb.BooleanProperty(default=False)
    recentlyViewedRootKeys = ndb.KeyProperty(repeated=True)
    createdPointRootKeys = ndb.KeyProperty(repeated=True)
    editedPointRootKeys = ndb.KeyProperty(repeated=True)
    websiteURL =  ndb.StringProperty()
    areasOfExpertise =  ndb.StringProperty()
    currentProfession =  ndb.StringProperty()
    bio =  ndb.StringProperty()
    privateArea = ndb.StringProperty()
    password = ndb.StringProperty()
    # linkedInProfileLink = ndb.StringProperty()
    # facebookProfileLink =  ndb.StringProperty()
    # googleProfileLink =  ndb.StringProperty()
    # twitterProfileLink =  ndb.StringProperty()

    def filterKeylistByCurrentNamespace(self, keylist):        
        currentNamespace = namespace_manager.get_namespace()        
        return filter(lambda key: key.namespace() == currentNamespace, keylist)            

    def set_password(self, raw_password):
        """Sets the password for the current user
        
        :param raw_password:
            The raw password which will be hashed and stored
        """
        self.password = security.generate_password_hash(raw_password, length=12)

    def resetPassword(self):
        randomPassword = WhysaurusUser.random_password(8)
        self.set_password(randomPassword)
        self.put()
        return randomPassword


    @classmethod
    def signup(cls, handler, email, name, password, website, areas, profession, bio):
                   
        auth_id = '%s: %s' % ('name', name)
        url = WhysaurusUser.constructURL(name)
    
        unique_properties = ['email', 'url', 'name'] if email else ['url', 'name']
        
        if password is None:
            raise WhysaurusException('Unable to create user. No password supplied.')
            
        user_data = WhysaurusUser.create_user(auth_id,
          unique_properties,
          url=url, email=email, name=name, password_raw=password,
          websiteURL=website, areasOfExpertise=areas, currentProfession=profession, bio=bio, verified=False)
         
        if not user_data[0]: #user_data is a tuple
            if 'name' in user_data[1]:
                raise WhysaurusException('Unable to create user because the username %s is already in use' % name)
            elif 'email' in user_data[1]:
                raise WhysaurusException('Unable to create user because the email %s is already in use' % email)
            else:
                raise WhysaurusException('Unable to create user for email %s because of \
                    duplicate keys %s' % (auth_id, user_data[1]))
        else:    
            user = user_data[1]
            if email:
                user_id = user.get_id()
                user.auth_ids.append('%s: %s' % ('email', email))
                user.put()
            
                token = WhysaurusUser.create_signup_token(user_id)
        
                verification_url = handler.uri_for('verification', type='v', user_id=user_id,
                                                   signup_token=token, _full=True)
        
                mail.send_mail(sender='aaron@whysaurus.com',
                    to=email,
                    subject='Whysaurus Email Verification',
                    body="Thank you for signing up for Whysaurus. \n\
                        Please verify your email address by navigating to this link: \
                        %s\n\nAaron Lifshin \nCTO" % verification_url, 
                    html="Thank you for signing up for Whysaurus. <br>\
                        Please verify your email address by clicking on \
                        <a href=\"%s\">this link</a>.<br><br>Aaron Lifshin <br> \
                        CTO" % verification_url,                
                    reply_to="aaron@whysaurus.com"
                )            
                logging.info('Created a user. Email: %s. Verification URL was: %s' % (email, verification_url))
            else:
                logging.info('Created a username only user. Name: %s.' % name)
            return user # SUCCESS       

    @classmethod
    def get_by_auth_token(cls, user_id, token, subject='auth'):
        """Returns a user object based on a user ID and token.
        
        :param user_id:
            The user_id of the requesting user.
        :param token:
            The token string to be verified.
        :returns:
            A tuple ``(User, timestamp)``, with a user object and
            the token timestamp, or ``(None, None)`` if both were not found.
        """
        token_key = cls.token_model.get_key(user_id, subject, token)
        user_key = ndb.Key(cls, user_id)
        # Use get_multi() to save a RPC call.
        valid_token, user = ndb.get_multi([token_key, user_key])
        if valid_token and user:
            timestamp = int(time.mktime(valid_token.created.timetuple()))
            return user, timestamp       
        return None, None

    @classmethod
    def get_by_email(cls, email):
        qry = cls.gql("WHERE email= :1", email)
        return qry.get()     
    
    @classmethod
    def get_by_name(cls, name):
        qry = cls.gql("WHERE name= :1", name)
        return qry.get()        

    @property
    def emailUser(self):
        auth_ids = self.auth_ids
        emailUser = False
        for auth_id in auth_ids:
            if 'email' in auth_id:
                emailUser = True
                break
            elif 'name' in auth_id:
                emailUser = True
                break
        return emailUser
        
    @property
    def createdCount(self):
        return len(self.createdPointRootKeys)
 
    @property
    def editedCount(self): 
        return len(self.editedPointRootKeys)
         
    @property
    def userVotes(self):
        if not hasattr(self, "_userVotes"):
            votes = UserVote.query(ancestor=self.key)
            # votes = qry.run()
            self._userVotes = {}
            if votes:
                for vote in votes:
                    self._userVotes[vote.pointRootKey] = vote
        return self._userVotes

    def updatePrivateArea(self, newPA):
        self.privateArea = newPA
        self.put()
        
    def addVote(self, point, voteValue, updatePoint=True):
        pointRootKey = point.key.parent()
        previousVoteValue = 0
        newVote = None
        if pointRootKey in self.userVotes:  # Vote already exists. Update
            previousVoteValue = self.userVotes[pointRootKey].value
            newVote = self.userVotes[pointRootKey]
            newVote.value = voteValue
        if not newVote:  # Create a brand new one
            newVote = UserVote(
                pointRootKey=pointRootKey,
                value=voteValue,
                parent=self.key
            )
        newVote.put()

        if updatePoint:
            if previousVoteValue == 0 and voteValue == 1:  # UPVOTE
                point.upVotes = point.upVotes + 1
            if previousVoteValue == 0 and voteValue == -1:  # DOWNVOTE
                point.downVotes = point.downVotes + 1
            if previousVoteValue == 1 and voteValue == 0:  # CANCEL UPVOTE
                point.upVotes = point.upVotes - 1
            if previousVoteValue == -1 and voteValue == 0:  # CANCEL DOWNVOTE
                point.downVotes = point.downVotes - 1
            if previousVoteValue == -1 and voteValue == 1:  # DOWN TO UP
                point.downVotes = point.downVotes - 1
                point.upVotes = point.upVotes + 1
            if previousVoteValue == 1 and voteValue == -1:  # UP TO DOWN
                point.downVotes = point.downVotes + 1
                point.upVotes = point.upVotes - 1
            point.voteTotal = point.upVotes - point.downVotes
            point.put()

        return newVote

    def setRibbon(self, point, ribbonValue, updatePoint=True):
        pointRootKey = point.key.parent()
        previousRibbon = False
        newVote = None
        if pointRootKey in self.userVotes:  # Vote already exists. Update
            previousRibbon = self.userVotes[pointRootKey].ribbon
            newVote = self.userVotes[pointRootKey]
            newVote.ribbon = ribbonValue
        if not newVote:  # Create a brand new one
            newVote = UserVote(
                pointRootKey=pointRootKey,
                value=0,
                ribbon=ribbonValue,
                parent=self.key
            )
        newVote.put() 
        if updatePoint:
            if not previousRibbon and ribbonValue:
                point.ribbonTotal = point.ribbonTotal + 1
                point.put()
            elif previousRibbon and not ribbonValue:
                point.ribbonTotal = point.ribbonTotal - 1
                point.put()
        return newVote
            

    def _updateRecentlyViewed(self, pointRootKey):
        addedToList = False

        if not self.recentlyViewedRootKeys:
            self.recentlyViewedRootKeys = [pointRootKey]
            addedToList = True

        if pointRootKey in self.recentlyViewedRootKeys:
            self.recentlyViewedRootKeys.remove(pointRootKey)
            self.recentlyViewedRootKeys.insert(0, pointRootKey)
        else:
            self.recentlyViewedRootKeys.insert(0, pointRootKey)
            addedToList = True

        if len(self.recentlyViewedRootKeys) > 10:
            self.recentlyViewedRootKeys.pop()
        
        return addedToList

    
    def updateRecentlyViewed(self, pointRootKey):
        self._updateRecentlyViewed(pointRootKey)
        self.put()
        return self.recentlyViewedRootKeys
    
    def recordCreatedPoint(self, pointRootKey):
        self._updateRecentlyViewed(pointRootKey)
        if not self.createdPointRootKeys:
            self.createdPointRootKeys = [pointRootKey]
        else:
            self.createdPointRootKeys.insert(0, pointRootKey)
        self.put()
        
    def recordEditedPoint(self, pointRootKey, write=True):
        if not self.editedPointRootKeys:
            self.editedPointRootKeys = [pointRootKey]
        else:
            if not pointRootKey in self.editedPointRootKeys:
                self.editedPointRootKeys.insert(0, pointRootKey)
            else:
                self.editedPointRootKeys.remove(pointRootKey)
                self.editedPointRootKeys.insert(0, pointRootKey)
        if write:
            self.put()
        return self.editedPointRootKeys


    def getRecentlyViewed(self, excludeList=None):
        recentlyViewedPoints = []
        keysToGet = self.filterKeylistByCurrentNamespace(self.recentlyViewedRootKeys)
        if excludeList:
            for x in excludeList:
                try:
                    keysToGet.remove(x)
                except ValueError:
                    pass
        pointRoots = ndb.get_multi(keysToGet)
        for pointRoot in pointRoots:
            if pointRoot:
                recentlyViewedPoints = recentlyViewedPoints + [
                    pointRoot.getCurrent()]
        return recentlyViewedPoints
    
    def getCreated(self):
        createdPoints = []
        rootKeys = self.filterKeylistByCurrentNamespace(self.createdPointRootKeys)
        pointRoots = ndb.get_multi(rootKeys[0:10])
        for pointRoot in pointRoots:
            createdPoints = createdPoints + [pointRoot.getCurrent()]
        return createdPoints

    def getEdited(self):
        editedPoints = []
        rootKeys = self.filterKeylistByCurrentNamespace(self.editedPointRootKeys)
        pointRoots = ndb.get_multi(rootKeys[0:10])
        for pointRoot in pointRoots:
            editedPoints = editedPoints + [pointRoot.getCurrent()]
        return editedPoints
    
    def update(self, newWebsiteURL, newUserAreas, newUserProfession, newUserBio):
        # self.name = newName if newName.strip() != "" else None
        self.websiteURL =  newWebsiteURL if newWebsiteURL.strip() != "" else None
        self.areasOfExpertise = newUserAreas if newUserAreas.strip() != "" else None
        self.currentProfession = newUserProfession if newUserProfession.strip() != "" else None
        self.bio = newUserBio if newUserBio.strip() != "" else None
        self.put()
        
    @staticmethod
    def constructURL(name):
        userURL = name.replace(" ", "_")
        userURL = re.sub('[\W]+', '', userURL)
        # Check if it already exists
        userQuery = WhysaurusUser.gql("WHERE url= :1", userURL)
        existingUser = userQuery.get()
    
        if existingUser:
            # Existing URL notes how many URLs+number exist for that URL
            existingUser.numCopies = existingUser.numCopies + 1
            userURL = userURL + str(existingUser.numCopies)
            existingUser.put()
        return userURL
            
    @staticmethod
    def getByUrl(url):
        qry = WhysaurusUser.gql("WHERE url= :1", url)
        return qry.get()

    @staticmethod
    def random_password(length=8):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        password = ''
        for i in range(length):
            password += random.choice(chars)
        return password

    
