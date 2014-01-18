import re
import time
import logging
import random
import string
import datetime
import webapp2

from google.appengine.ext import ndb
import webapp2_extras.appengine.auth.models as auth_models
from webapp2_extras.appengine.auth.models import Unique

from webapp2_extras import security
from google.appengine.api import namespace_manager
from google.appengine.api import mail
from google.appengine.api import channel

from models.notification import Notification
from models.chatUser import ChatUser
from models.point import getCurrent_async

from whysaurusexception import WhysaurusException
from uservote import UserVote
from uservote import RelevanceVote
from timezones import PST


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
    token = ndb.StringProperty()  
    tokenExpires = ndb.DateTimeProperty()  
    lastLogin = ndb.DateTimeProperty()
    notificationFrequency = ndb.StringProperty(default=None)
    _notifications = None
    
    # linkedInProfileLink = ndb.StringProperty()
    # facebookProfileLink =  ndb.StringProperty()
    # googleProfileLink =  ndb.StringProperty()
    # twitterProfileLink =  ndb.StringProperty()

    @property
    def PSTupdated(self):
        return PST.convert(self.updated)
    
    @property
    def PSTlastlogin(self):
        return PST.convert(self.lastLogin)
        
    @property
    def notifications(self):
        return self._notifications
    
    @property
    def newNotificationCount(self):
        return self._newNotificationCount
 
    @property
    def moreNotificationsExist(self):
        return self._moreNotificationsExist
       
    def getActiveNotifications(self):
        self._notifications, self._newNotificationCount, \
            self._moreNotificationsExist = \
                Notification.getActiveNotificationsForUser(self.key)
        return self._notifications

    # A small subset of user stuff to store the relevant information for chat
    def makeChatUser(self):
        return ChatUser(parent = self.key,
                        token = self.token,
                        tokenExpires=self.tokenExpires,
                        )

    def clearNotifications(self, latest, earliest=None):
        Notification.clearNotifications(self.key, latest, earliest)

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
    
    def login(self):
        # Update last login time
        self.lastLogin = datetime.datetime.now()
        now = datetime.datetime.now()
        # Create And Store Token    
        if not self.token or self.tokenExpires < now: 
            self.createChannel()                 
        self.put()
        return
    
    def createChannel(self, saveUser=False):
        now = datetime.datetime.now()
        self.token = channel.create_channel(self.url, duration_minutes=1440)
        self.tokenExpires = now + datetime.timedelta(days=1)
        logging.info('Creating new token for user %s: %s' % (self.url, self.token))        
        if saveUser:
            self.put()
        return self            
        
            
    
    @classmethod
    def signup(cls, handler, email, name, password, website, areas, profession, bio):
                   
        auth_id = '%s: %s' % ('name', name)
        url = WhysaurusUser.constructURL(name)
    
        unique_properties = ['email', 'url', 'name'] if email else ['url', 'name']
        
        if password is None:
            raise WhysaurusException('Unable to create user. No password supplied.')
            
        result, creationData = WhysaurusUser.create_user(auth_id,
          unique_properties,
          url=url, email=email, name=name, password_raw=password,
          websiteURL=website, areasOfExpertise=areas, currentProfession=profession, bio=bio, verified=False)
         
        if not results: #user_data is a tuple
            if 'name' in creationData:
                raise WhysaurusException('Unable to create user because the username %s is already in use' % name)
            elif 'email' in creationData:
                raise WhysaurusException('Unable to create user because the email %s is already in use' % email)
            else:
                raise WhysaurusException('Unable to create user for email %s because of \
                    duplicate keys %s' % (auth_id, user_data[1]))
        else:    
            user = creationData
            if email:
                user_id = user.get_id()
                user.auth_ids.append('%s: %s' % ('email', email))
                user.put()            
                WhysaurusUser.send_verification_email(handler, user_id, email, "signing up for Whysaurus")
                
            else:
                logging.info('Created a username only user. Name: %s.' % name)
            return user # SUCCESS       


    @staticmethod
    def send_verification_email(handler, user_id, email, reason):
        token = WhysaurusUser.create_signup_token(user_id)

        verification_url = handler.uri_for('verification', type='v', user_id=user_id,
                                           signup_token=token, _full=True)

        mail.send_mail(sender='Whysaurus Admin <aaron@whysaurus.com>',
            to=email,
            subject='Whysaurus Email Verification',
            body="Thank you for %s. \n\
                Please verify your email address by navigating to this link: \
                %s\n\nAaron Lifshin \nCTO" % (reason, verification_url), 
            html="Thank you for %s. <br>\
                Please verify your email address by clicking on \
                <a href=\"%s\">this link</a>.<br><br>Aaron Lifshin <br> \
                CTO" % (reason, verification_url),                
            reply_to="aaron@whysaurus.com"
        )            
        logging.info('Sending verification email for %s. Email: %s. Verification URL was: %s' % \
            (reason, email, verification_url))

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

    @webapp2.cached_property
    def notificationFrequencyText(self):
        if self.notificationFrequency:
            return self.notificationFrequency
        else:
            return "Never"
        
    @webapp2.cached_property
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

    def getVoteFuture(self, pointRootKey):
        return UserVote.query(            
            UserVote.pointRootKey==pointRootKey, ancestor=self.key).get_async()

    @ndb.tasklet
    def getVote_async(self, pointRootKey):
        vote = yield UserVote.query(            
            UserVote.pointRootKey==pointRootKey, ancestor=self.key).get_async()
        raise ndb.Return(vote)

    def getVoteValues(self, pointRootKey):
        vote = UserVote.query(            
            UserVote.pointRootKey==pointRootKey, ancestor=self.key).get()
        if vote:
            return vote.value, vote.ribbon
        else:
            return 0, False                    

    def updatePrivateArea(self, newPA):
        self.privateArea = newPA
        self.put()
       
       
    def _getOrCreateVote(self, pointRootKey):
        vote = UserVote.query(             
            UserVote.pointRootKey==pointRootKey, ancestor=self.key).get()            
        if not vote:  # No vote yet, create a new one
            vote = UserVote(
                pointRootKey=pointRootKey,
                value=0,
                ribbon=False,
                parent=self.key
            )        
        return vote
        
    def addVote(self, point, voteValue, updatePoint=True):
        pointRootKey = point.key.parent()
        vote = self._getOrCreateVote(pointRootKey)
        previousVoteValue = vote.value
        vote.value = voteValue
        vote.put()
        
        # We only send notifications for agrees at the moment
        if voteValue == 1:
            point.addNotificationTask(pointRootKey, self.key, 1)

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

        return vote

    def setRibbon(self, point, ribbonValue, updatePoint=True):
        pointRootKey = point.key.parent()
        vote = self._getOrCreateVote(pointRootKey)
        previousRibbon = vote.ribbon
        vote.ribbon = ribbonValue            
        vote.put() 
        if updatePoint:
            if not previousRibbon and ribbonValue:
                point.ribbonTotal = point.ribbonTotal + 1
                point.put()
            elif previousRibbon and not ribbonValue:
                point.ribbonTotal = point.ribbonTotal - 1
                point.put()
                
        # Only send a notification if a ribbnon is awarded
        if ribbonValue:
            point.addNotificationTask(pointRootKey, self.key, 2)

        return vote
            
    def addRelevanceVote(self, parentRootURLsafe, childRootURLsafe, linkType, vote):
        parentRootKey = ndb.Key(urlsafe=parentRootURLsafe)
        childRootKey = ndb.Key(urlsafe=childRootURLsafe)
        pointRoot = parentRootKey.get()
        curPoint = pointRoot.current.get()
        
        oldRelVote = RelevanceVote.query(
            RelevanceVote.parentPointRootKey == parentRootKey,
            RelevanceVote.childPointRootKey == childRootKey,
            RelevanceVote.linkType == linkType,
            ancestor=self.key).get()
            
        newRelVote = RelevanceVote(
            parent=self.key,
            parentPointRootKey = parentRootKey,
            childPointRootKey = childRootKey,
            value = vote,
            linkType=linkType)
        return self.transactionalAddRelevanceVote(
            curPoint, oldRelVote, newRelVote)
        
    def getRelevanceVotes(self, parentPoint):
        parentRootKey = parentPoint.key.parent();
        maxNumVotes = parentPoint.numSupporting + parentPoint.numCounter;
        
        rVotes = None
        if maxNumVotes > 0:
            # MULTIPLY numVotes * 2 because the current set of points may be smaller
            # than the set for a given version
            rVotes = RelevanceVote.query(
                RelevanceVote.parentPointRootKey == parentRootKey, 
                ancestor = self.key).fetch(maxNumVotes*2)
        return rVotes

    @ndb.tasklet
    def getRelevanceVotes_async(self, parentPoint):
        parentRootKey = parentPoint.key.parent();
        maxNumVotes = parentPoint.numSupporting + parentPoint.numCounter;
        
        rVotes = None
        if maxNumVotes > 0:
            # MULTIPLY numVotes * 2 because the current set of points may be smaller
            # than the set for a given version
            rVotes = yield RelevanceVote.query(
                RelevanceVote.parentPointRootKey == parentRootKey, 
                ancestor = self.key).fetch_async(maxNumVotes*2)
        raise ndb.Return(rVotes)
        
    
    # Returns: true/false, new vote value, new number of votes on this line 
    @ndb.transactional(xg=True)
    def transactionalAddRelevanceVote(self, parentPoint, oldRelVote, newRelVote):
        # This will write to the point version's link array
        try: 
            result, newRelevance, voteCount = parentPoint.addRelevanceVote(
                oldRelVote, newRelVote)
            if result:                
                if oldRelVote:
                    # Update the user's vote for this link
                    oldRelVote.value = newRelVote.value
                    oldRelVote.put()
                    logging.info('TARV: Updating existing vote.')
                else:
                    logging.info('TARV: Adding new vote.')
                    newRelVote.put()
                return True, newRelevance, voteCount
        except Exception as e:
            logging.exception('Could not write to NDB during transactionalAddRelevanceVote')
            return False, None, None
        

            

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
        self.put_async()
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
    
    @ndb.tasklet
    def getRecentlyViewed_async(self, excludeList=None):
        recentlyViewedPoints = []
        keysToGet = self.filterKeylistByCurrentNamespace(self.recentlyViewedRootKeys)
        if excludeList:
            for x in excludeList:
                try:
                    keysToGet.remove(x)
                except ValueError:
                    pass
        recentlyViewedPoints = yield map(lambda x: getCurrent_async(x), (yield ndb.get_multi_async(keysToGet)))
        raise ndb.Return(recentlyViewedPoints)             
        
    def getCreated(self):
        createdPoints = []
        # logging.info("Create point root keys: %d" % len(self.createdPointRootKeys))
        rootKeys = self.filterKeylistByCurrentNamespace(self.createdPointRootKeys)
        # logging.info("Filtered root keys by %s: %d" %  \
        #    (namespace_manager.get_namespace(), len(rootKeys)))
        # logging.info("Root key list " + str(rootKeys))
        pointRoots = ndb.get_multi(rootKeys[0:50])
        for pointRoot in pointRoots:
            if pointRoot:
                createdPoints = createdPoints + [pointRoot.getCurrent()]
        return createdPoints
        

    def getEdited(self):
        editedPoints = []
        rootKeys = self.filterKeylistByCurrentNamespace(self.editedPointRootKeys)
        pointRoots = ndb.get_multi(rootKeys[0:50])
        for pointRoot in pointRoots:
            if pointRoot:
                editedPoints = editedPoints + [pointRoot.getCurrent()]
        return editedPoints
    
    def update(self, handler, newWebsiteURL, newUserAreas, newUserProfession, newUserBio, newEmail, newNotificationFrequency):
        # self.name = newName if newName.strip() != "" else None
        self.websiteURL =  newWebsiteURL if newWebsiteURL.strip() != "" else None
        self.areasOfExpertise = newUserAreas if newUserAreas.strip() != "" else None
        self.currentProfession = newUserProfession if newUserProfession.strip() != "" else None
        self.bio = newUserBio if newUserBio.strip() != "" else None
        self.notificationFrequency = newNotificationFrequency if newNotificationFrequency.strip() != "" else None
        if newEmail != self.email:
            new_auth_id = '%s: %s' % ('email', newEmail)            
            # Make sure that email is unique
            success = Unique.create(new_auth_id)                                
            if success:    
                if (self.emailUser):
                    # Replace the email in the auth ID array
                    new_auth_ids = [x for x in self.auth_ids if not 'email' in x]
                    new_auth_ids.append(new_auth_id)
                    self.auth_ids = new_auth_ids
                # send a validation email 
                WhysaurusUser.send_verification_email(
                    handler, 
                    self.get_id(), 
                    newEmail, 
                    "updating your email address")
                self.email = newEmail if newEmail.strip() != "" else None                
            else:
                raise WhysaurusException("The email address %s already exists" % newEmail)                       
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

    
