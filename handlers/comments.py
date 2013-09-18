import json

from authhandler import AuthHandler
from models.comment import Comment
from models.whysaurusexception import WhysaurusException 
from models.timezones import PST

class Comments(AuthHandler):
    def saveComment(self):
        results = {'result': False}
        text = self.request.get('commentText')
        pointRootUrlsafe = self.request.get('p')
        parentCommentUrlsafe = self.request.get('parentKey')
        
        user = self.current_user
        if user:
            try:
                comment = Comment.create(
                    text, user, pointRootUrlsafe, 
                    parentCommentUrlsafe)
                if comment:
                    pst_date = PST.convert(comment.date)
                    results = {
                               'result': True, 
                               'userName': user.name,
                               'userURL': user.url,
                               'avatar_url': user.avatar_url if hasattr(user, 'avatar_url') else '/static/img/icon_triceratops_black_47px.png',
                               'text': text,
                               'date': pst_date.strftime('%b. %d, %Y, %I:%M %p'),
                               'parentUrlsafe': parentCommentUrlsafe,
                               'myUrlSafe':comment.key.urlsafe(),
                               'level': comment.level
                               }
            except WhysaurusException as e:
                results['error'] = str(e)
        resultJSON = json.dumps(results)
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(resultJSON)
        