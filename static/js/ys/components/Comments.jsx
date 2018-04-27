import React from 'react';
import PropTypes from 'prop-types'
import { graphql, compose } from 'react-apollo';
import { CloseLinkX } from './common'
import * as schema from '../schema';
import NewComment from './NewComment'

class Comment extends React.Component {
  static propTypes = {
    comment: PropTypes.object.isRequired,
    addReply: PropTypes.func.isRequired
  }

  render(){
    const {comment, point, addReply} = this.props
    const {id, text, parentID} = comment
    return <div>
      <span>{text}</span>
      <span>{parentID}</span>
      <NewComment parent={this.props.comment} onSubmit={({text}) => addReply(text)}/>
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

  state = {}

  render(){
    const {comments, point, add, onCancel} = this.props
    return <div className="row-fluid claimEditArea pointCardPaddingH commentsArea ">
      <span className="claimEditAreaHeading">
        <span className="heading">Meta</span>
        <span className="editAreaClose"><a onClick={onCancel}><CloseLinkX/></a></span>
      </span>
      {comments && comments.map(comment => <Comment key={comment.id} comment={comment} addReply={text => add(point.id, text, comment.id)}/>)}
      <NewComment onSubmit={({text}) => add(point.id, text)}/>
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
