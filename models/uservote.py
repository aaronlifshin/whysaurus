from google.appengine.ext import ndb
import logging
from models.whysaurusexception import WhysaurusException

class UserVote(ndb.Model):
    pointRootKey = ndb.KeyProperty(required=True)
    value = ndb.IntegerProperty(required=True, indexed=False)  # 1, 0, -1
    ribbon = ndb.BooleanProperty(default=False, indexed=False)        

class RelevanceVote(ndb.Model):    
    parentPointRootKey = ndb.KeyProperty(required=True)
    childPointRootKey = ndb.KeyProperty(required=True) 
    linkType = ndb.StringProperty()  
    value = ndb.IntegerProperty(required=True, indexed=False)  # 1, 0, -1
    dateCreated = ndb.DateTimeProperty(auto_now_add=True, indexed=False)
    dateEdited = ndb.DateTimeProperty(auto_now=True, indexed=False) 
        
    @classmethod
    def getExistingVotes(cls, fromRootKey, toRootKey, linkType):
        q = RelevanceVote.query(RelevanceVote.parentPointRootKey == fromRootKey,
           RelevanceVote.childPointRootKey == toRootKey, 
           RelevanceVote.linkType == linkType)
        votes, cursor, more = q.fetch_page(20)        
        while more:
            moreVotes, cursor, more = q.fetch_page(20, start_cursor=cursor)
            votes = votes + moreVotes
        return votes
            
    @classmethod
    def getExistingVoteNumbers(cls, fromRootKey, toRootKey, linkType, user):
        rVotes = cls.getExistingVotes(fromRootKey, toRootKey, linkType)
        voteCount = 0
        rating = 0        
        myVote = None
        if rVotes:
            myVotes = [v for v in rVotes if v.key.parent() == user.key] 
            if len(myVotes) > 1:
                raise WhysaurusException('Multiple relevance votes recorded for one user')
            else:
                myVote = myVotes[0]
            total = sum(vote.value for vote in rVotes)
            voteCount = len(rVotes)
            rating = total/voteCount
            logging.info('GEVN. Found %d existing votes. Returning %d, %d ' % ( len(rVotes), voteCount, rating))            
        return voteCount, rating, myVote
                    