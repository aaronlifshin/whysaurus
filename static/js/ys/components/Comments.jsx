import React from 'react';
import PropTypes from 'prop-types'
import { graphql, compose } from 'react-apollo';
import { CloseLinkX } from './common'
import * as schema from '../schema';
import NewComment from './NewComment'

class Comments extends React.Component {
  static propTypes = {
  }

  state = {}

  render(){
    const {comments, point, add, onCancel} = this.props
    return <div className="row-fluid claimEditArea pointCardPaddingH commentsArea ">
      <span className="claimEditAreaHeading">
        <span className="heading">Meta</span>
        <span className="editAreaClose"><a onClick={onCancel}><CloseLinkX/></a></span>
      </span>
      {comments && comments.map(({text}) => <div>{text}</div>)}
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
      add: (pointID, text) =>
        mutate({variables: {pointID, text},
                refetchQueries: [{query: schema.Comments, variables: {pointID: pointID}}]})
    })

  })
)(Comments)
