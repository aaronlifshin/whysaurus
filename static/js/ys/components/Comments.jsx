import React from 'react';
import PropTypes from 'prop-types'
import { graphql, compose } from 'react-apollo';
import { CloseLinkX } from './common'
import * as schema from '../schema';
import NewComment from './NewComment'

class Comment extends React.Component {
  static propTypes = {
    comment: PropTypes.object.isRequired,
    addReply: PropTypes.func,
    replies: PropTypes.array
  }

  state = {replying: false}

  newReply = () => {
    const {comment, replies, point, addReply} = this.props
    if (this.props.comment.level == 0){
      if (this.state.replying) {
        return <NewComment parent={comment} onSubmit={({text}) => addReply(text).then(() => this.setState({replying: false}))} onCancel={() => this.setState({replying: false})}/>
      } else {
        return <button className="buttonUX2 buttonUX2RespIcon newCommentFormButton"
                       onClick={() => this.setState({replying: true})}>Reply</button>
      }
    }
  }

  render(){
    const {comment, replies, point, addReply} = this.props
    const {id, text, parentID} = comment
    return <div>
      <span>{text}</span>
      {replies && replies.map(reply => <Comment key={reply.id} comment={reply}/>)}
      {this.newReply()}
    </div>
  }
}

class Comments extends React.Component {
  static propTypes = {
    point: PropTypes.object.isRequired,
    onCancel: PropTypes.func.isRequired,
    add: PropTypes.func.isRequired,
    parentComment: PropTypes.object,
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

  newComment = () => {
    const {point, add} = this.props
    if (this.state.commenting) {
      return <NewComment onSubmit={({text}) => add(point.id, text)} onCancel={() => this.setState({commenting: false})}/>
    } else {
      return <button className="buttonUX2 buttonUX2RespIcon newCommentFormButton" onClick={() => this.setState({commenting: true})}>New Comment</button>
    }
  }

  render(){
    const {comments, point, add, onCancel} = this.props
    const replies = this.buildRepliesIndex(comments)
    return <div className="row-fluid claimEditArea pointCardPaddingH commentsArea ">
      <span className="claimEditAreaHeading">
        <span className="heading">Meta</span>
        <span className="editAreaClose"><a onClick={onCancel}><CloseLinkX/></a></span>
      </span>
      {comments && comments.filter(comment => comment.level == 0).map(comment => <Comment key={comment.id} comment={comment} replies={replies[comment.id]} addReply={text => add(point.id, text, comment.id)}/>)}
      {this.newComment()}
    </div>
  }
}


export default compose(
  graphql(schema.Comments, {
    options: ({point}) => ({
      variables: {pointID: point.id}
    }),
    props: ({ownProps, data: {loading, comments, refetch}}) => ({
      ...ownProps,
      loadingComments: loading,
      comments: comments,
      refetchComments: refetch
    })
  }),
  graphql(schema.NewComment, {
    props: ({ mutate }) => ({
      add: (pointID, text, parentCommentID) =>
        mutate({variables: {pointID, text, parentCommentID},
                refetchQueries: [{query: schema.Comments, variables: {pointID: pointID}}]})
    })

  })
)(Comments)
