import logging

from google.appengine.ext import ndb
from whysaurusexception import WhysaurusException
from models.timezones import PST
from models.follow import Follow


class Comment(ndb.Model):
    date = ndb.DateTimeProperty(auto_now_add=True)
    text = ndb.TextProperty()
    userName = ndb.StringProperty()
    userUrl = ndb.StringProperty()
    avatar_url = ndb.StringProperty()
    parentComment = ndb.KeyProperty(kind='Comment')
    level = ndb.IntegerProperty(default=0)

    @property
    def PSTdateText(self):
        return PST.convert(self.date).strftime('%b. %d, %Y, %I:%M %p')

    @classmethod
    @ndb.transactional(xg=True)
    def transactionalCreate(cls, pointRoot, comment):
        comment.put()
        pointRoot.addComment(comment)
        return comment


    @classmethod
    def create(cls, text, user, pointRoot, parent = None):
        parentCommentKey = None
        parentComment = None
        if parent:
            parentCommentKey = ndb.Key(urlsafe=parent)
            parentComment =  parentCommentKey.get()
            if not parentComment:
                raise WhysaurusException("Bad parent comment key supplied.")
            elif parentComment.level >= 8:
                raise WhysaurusException("9 levels of replies are maximum for now.")

        if pointRoot:
            comment = Comment(parent=parentCommentKey, text=text, userName = user.name, userUrl=user.url,
                              avatar_url = user.avatar_url if hasattr(user, 'avatar_url') else '/static/img/icon_triceratops_black_47px.png',
                              parentComment = parentCommentKey,
                              level = parentComment.level + 1 if parentComment else 0)
            newComment = comment.transactionalCreate(pointRoot, comment)
            Follow.createFollow(user.key, pointRoot.key, "commented on")
            return newComment
        else:
            return None
