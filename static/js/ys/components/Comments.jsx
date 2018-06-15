import React from 'react';
import PropTypes from 'prop-types'
import { graphql, compose } from 'react-apollo';
import { CloseLinkX } from './common'
import * as schema from '../schema';
import NewComment from './NewComment'
import TimeAgo from 'react-timeago'

class CommentComponent extends React.Component {
  static propTypes = {
    comment: PropTypes.object.isRequired,
    addReply: PropTypes.func,
    replies: PropTypes.array
  }

  state = {replying: false}

  commentActions = () => {
    const {user, comment, replies, point, addReply, archive} = this.props
    if (this.props.comment.level == 0){
      if (this.state.replying) {
        return <NewComment parent={comment} onSubmit={({text}) => addReply(text).then(() => this.setState({replying: false}))} onCancel={() => this.setState({replying: false})}/>
      } else {
        let classes = `commentBottomRowActions ${replies ? "commentIndent" : ""}`
        return <div className={classes}>
          <a className="editAreaLink" onClick={() => this.setState({replying: true})}>Reply</a>
          {user && user.admin && !comment.archived && <a className="editAreaLink admin" onClick={archive}>Archive</a>}
        </div>
      }
    }
  }

  render(){
    const {comment, replies, point, addReply} = this.props
    const {id, userName, userUrl, date, text, parentID} = comment
    let classes = `comment ${(this.props.comment.level > 0) ? "commentIndent" : ""}`
    return <div className={classes}>
      { (this.props.comment.level == 0) && <div className="divider"></div> }
      <div className="byline"><a href={userUrl}>@{userName}</a> · <TimeAgo date={date + "Z"} minPeriod={300}/></div>
      <div className="commentText">{text}</div>
      {replies && replies.sort((a, b) => a.date > b.date).map(reply => <Comment key={reply.id} comment={reply}/>)}
      {this.props.user && this.commentActions()}
    </div>
  }
}

const Comment = graphql(schema.CurrentUserQuery, {
  props: ({ownProps, data: {loading, currentUser, refetch}}) => ({
    userLoading: loading,
    user: currentUser,
    refetchUser: refetch
  })
})(CommentComponent)

class CommentsListComponent extends React.Component {
  static propTypes = {
    point: PropTypes.object.isRequired,
    onCancel: PropTypes.func.isRequired,
    add: PropTypes.func.isRequired,
    toggleArchived: PropTypes.func.isRequired,
    comments: PropTypes.array
  }

  state = {commenting: false}

  buildRepliesIndex = (comments) => comments && comments.reduce((a, c) => {
    const parentID = c.parentID
    if (parentID) {
      const r = (a[parentID] || [])
      r.push(c)
      a[parentID] = r
    }
    return a
  }, {})

  onAddContinue = () => {
    this.setState({commenting: false})
    ga('send', 'event', 'Comment', 'Submit Comment', this.point.url);
    console.log('GA Comment Event Sent')
  }

  newComment = () => {
    const {point, add} = this.props
    if (this.state.commenting) {
      return <NewComment onSubmit={({text}) => add(point.id, text).then(this.onAddContinue)} onCancel={() => this.setState({commenting: false})}/>
    } else {
      return <span className="newCommentButons">
          <button className="buttonSecondaryUX2blue newCommentButton" onClick={() => this.setState({commenting: true})}>Clarification</button>
          <button className="buttonSecondaryUX2blue newCommentButton" onClick={() => this.setState({commenting: true})}>Needs Evidence</button>
          <button className="buttonSecondaryUX2blue newCommentButton" onClick={() => this.setState({commenting: true})}>Other Comment</button>
        </span>
    }
  }

  toggleArchivedControl = () => {
    const {showArchived, toggleArchived} = this.props
    if (showArchived) {
      return <span><div className="divider"></div><a className="editAreaLink" onClick={toggleArchived}>Hide Archived Comments</a></span>
    } else {
      return <span><div className="divider"></div><a className="editAreaLink" onClick={toggleArchived}>Show Archived Comments</a></span>
    }
  }

  render(){
    const {comments, point, add, onCancel, hasArchived, archive} = this.props
    const replies = this.buildRepliesIndex(comments)
    return <div className="">
      <span className="claimEditAreaHeading">
        <span className="heading">Meta</span>
        <span className="editAreaClose"><a onClick={onCancel}><CloseLinkX/></a></span>
      </span>
      <div className="claimEditAreaNote">Discuss how to improve this claim.</div>
      {this.props.user && this.newComment()}
      <div className="commentsList">
        {comments && comments.filter(comment => comment.level == 0).map(comment => <Comment key={comment.id} comment={comment} replies={replies[comment.id]} addReply={text => add(point.id, text, comment.id)} archive={() => archive(point.id, comment.id)}/>)}
      </div>
      {hasArchived && this.toggleArchivedControl()}
    </div>
  }
}


const CommentsList = compose(
  graphql(schema.Comments, {
    options: ({point, showArchived}) => ({
      variables: {pointID: point.id, showArchived: !!showArchived}
    }),
    props: ({ownProps, data: {loading, comments, refetch}}) => ({
      ...ownProps,
      loadingComments: loading,
      comments: comments && comments.comments,
      hasArchived: comments && (comments.archivedCount > 0),
      refetchComments: refetch
    })
  }),
  graphql(schema.NewComment, {
    props: ({ mutate, ownProps: {showArchived} }) => ({
      add: (pointID, text, parentCommentID) => {
        return mutate({variables: {pointID, text, parentCommentID},
                       refetchQueries: [{query: schema.Comments, variables: {pointID, showArchived: !!showArchived}}]})
      }
    })

  }),
  graphql(schema.ArchiveComment, {
    props: ({ mutate, ownProps: {showArchived} }) => ({
      archive: (pointID, commentID) =>
        mutate({variables: {pointID, commentID},
                refetchQueries: [{query: schema.Comments, variables: {pointID, showArchived: !!showArchived}}]})
    })

  }),
  graphql(schema.CurrentUserQuery, {
    props: ({ownProps, data: {loading, currentUser, refetch}}) => ({
      userLoading: loading,
      user: currentUser,
      refetchUser: refetch
    })
  })
)(CommentsListComponent)

export default class Comments extends React.Component {
  static propTypes = {
    point: PropTypes.object.isRequired,
    onCancel: PropTypes.func.isRequired
  }

  state = {showArchived: false}

  toggleShowArchived = () => {
    this.setState({showArchived: !this.state.showArchived})
  }

  render(){
    let classesCommentsIndent = `${this.props.parentPoint && "addOneIndent"}` 
    console.log('parentPoint: ' + this.props.parentPoint);    
    return <div className={classesCommentsIndent}>
      <div className="row-fluid claimEditArea pointCardPaddingH commentsArea hideBorderTop" onClick={e => e.stopPropagation()}>      
        <CommentsList point={this.props.point} onCancel={this.props.onCancel}
                      showArchived={this.state.showArchived}
                      toggleArchived={this.toggleShowArchived}/>
      </div>
    </div>
  }
}
