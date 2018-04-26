import React from 'react';
import PropTypes from 'prop-types'
import { graphql, compose } from 'react-apollo';
import CloseLinkX from './Point'
import * as schema from '../schema';

class Comments extends React.Component {
  static propTypes = {
    render: PropTypes.func.isRequired
  }

  render(){
    return <div className="row-fluid claimEditArea pointCardPaddingH commentsArea ">
      <span className="claimEditAreaHeading">
      <span className="heading">Meta</span>
      <span className="editAreaClose"><a onClick={this.props.onCancel}><CloseLinkX/></a></span>
      </span>
      Here is where you comment!
    </div>
  }
}


export default Comments
//compose(graphql(schema.Comments))(Comments)
