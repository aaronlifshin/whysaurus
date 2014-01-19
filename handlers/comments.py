import json

from authhandler import AuthHandler
from models.comment import Comment
from models.point import PointRoot, Point

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
                pointRoot = PointRoot.getByUrlsafe(pointRootUrlsafe) 
                if pointRoot:               
                    comment = Comment.create(
                        text, user, pointRoot, 
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
                        Point.addNotificationTask(pointRoot.key, user.key, 3, text)
                                   
                else:
                    results['error'] = 'Unable to find the point to add this comment'
            except WhysaurusException as e:
                results['error'] = str(e)
        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
        
    def archiveComments(self):
        results = {'result': False}
        pointRootUrlsafe = self.request.get('rootKey')
        parentCommentUrlsafe = self.request.get('parentKey')
        user = self.current_user
        
        if user and user.admin:
            pointRoot = PointRoot.getByUrlsafe(pointRootUrlsafe)
            if pointRoot:
                try:
                    numArchived = pointRoot.archiveComments(parentCommentUrlsafe)
                    results = {
                        'result': True,
                        'numArchived': numArchived
                    }
                    
                except WhysaurusException as e:
                    results['error'] = str(e)                    
            else:
                results['error'] = 'Unable to find point root'

        else:
            results['error'] = 'Not authorized to archive comments'
            
        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
        
    def getArchivedComments(self):
        results = {'result': False}
        pointRootUrlsafe = self.request.get('rootKey')
        pointRoot = PointRoot.getByUrlsafe(pointRootUrlsafe)
        if pointRoot:
            try: 
                template_values = {
                    'archivedComments': pointRoot.getArchivedComments()
                }
                html = self.template_render('archivedComments.html', template_values)
                results = {
                    'result': True,
                    'html': html
                }
            except WhysaurusException as e:
                results['error'] = str(e)
        else:
            results['error'] = 'Unable to find point root'
                
        resultJSON = json.dumps(results)
        self.response.headers["Content-Type"] = 'application/json; charset=utf-8'
        self.response.out.write(resultJSON)
        
    