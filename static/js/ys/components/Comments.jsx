import React from 'react';
import PropTypes from 'prop-types'
import { graphql, compose } from 'react-apollo';
import { CloseLinkX } from './common'
import * as schema from '../schema';

class Comments extends React.Component {
  static propTypes = {
  }

  render(){
    const comments = this.props.comments
    return <div className="row-fluid claimEditArea pointCardPaddingH commentsArea ">
      <span className="claimEditAreaHeading">
        <span className="heading">Meta</span>
        <span className="editAreaClose"><a onClick={this.props.onCancel}><CloseLinkX/></a></span>
      </span>
      {comments && comments.map(({text}) => <div>{text}</div>)}
      Here is where you comment!
    </div>
  }
}


export default graphql(schema.Comments, {
  options: ({point}) => ({
    variables: {pointID: point.id}
  }),
  props: ({ownProps, data: {loading, comments, refetch}}) => ({
    ...ownProps,
    loadingComments: loading,
    comments: comments,
    refetchComments: refetch
  })
})(Comments)
