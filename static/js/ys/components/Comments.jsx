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

  newReply = () => {
    const {user, comment, replies, point, addReply, archive} = this.props
    if (this.props.comment.level == 0){
      if (this.state.replying) {
        return <NewComment parent={comment} onSubmit={({text}) => addReply(text).then(() => this.setState({replying: false}))} onCancel={() => this.setState({replying: false})}/>
      } else {
        return <div>
          <button className="buttonUX2 buttonUX2RespIcon newCommentFormButton" onClick={() => this.setState({replying: true})}>Reply</button>
          {user && user.admin && <a onClick={archive}>Archive</a>}
        </div>
      }
    }
  }

  render(){
    const {comment, replies, point, addReply} = this.props
    const {id, userName, userUrl, date, text, parentID} = comment
    return <div>
      <a href={userUrl}>@{userName}</a> - <TimeAgo date={date + "Z"}/>
      <p>{text}</p>
      {replies && replies.sort((a, b) => a.date > b.date).map(reply => <Comment key={reply.id} comment={reply}/>)}
      {this.newReply()}
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
    comments: PropTypes.array
  }

  state = {commenting: false,
           showArchived: false}

  buildRepliesIndex = (comments) => comments && comments.reduce((a, c) => {
    const parentID = c.parentID
    if (parentID) {
      const r = (a[parentID] || [])
      r.push(c)
      a[parentID] = r
    }
    return a
  }, {})

  newComment = () => {
    const {point, add} = this.props
    if (this.state.commenting) {
      return <NewComment onSubmit={({text}) => add(point.id, text).then(() => this.setState({commenting: false}))} onCancel={() => this.setState({commenting: false})}/>
    } else {
      return <button className="buttonUX2 buttonUX2RespIcon newCommentFormButton" onClick={() => this.setState({commenting: true})}>New Comment</button>
    }
  }

  render(){
    const {comments, point, add, onCancel, archive} = this.props
    const replies = this.buildRepliesIndex(comments)
    return <div className="row-fluid claimEditArea pointCardPaddingH commentsArea ">
      <span className="claimEditAreaHeading">
        <span className="heading">Meta</span>
        <span className="editAreaClose"><a onClick={onCancel}><CloseLinkX/></a></span>
      </span>
      {comments && comments.filter(comment => comment.level == 0).map(comment => <Comment key={comment.id} comment={comment} replies={replies[comment.id]} addReply={text => add(point.id, text, comment.id)} archive={() => archive(point.id, comment.id)}/>)}
      {this.newComment()}
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
      comments: comments,
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

  })
)(CommentsListComponent)

export default class Comments extends React.Component {
  static propTypes = {
    point: PropTypes.object.isRequired,
    onCancel: PropTypes.func.isRequired
  }

  state = {showArchived: false}

  showArchived = () => {
    if (this.state.showArchived) {
        return <button onClick={() => this.setState({showArchived: false})}>Hide Archived</button>
    } else {
        return <button onClick={() => this.setState({showArchived: true})}>Show Archived</button>
    }
  }

  render(){
    return <div>
      {this.showArchived()}
      <CommentsList point={this.props.point} onCancel={this.props.onCancel} showArchived={this.state.showArchived}/>
    </div>
  }
}
