import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'react-apollo'
import * as schema from '../schema'

class HeaderSearch extends React.Component {
  static propTypes = {
    render: PropTypes.func.isRequired
  }

  renderMatchingPoints = () => {
    
  }

  render(){
    const {search, loading} = this.props.data || {}
    return (
      //this.props.render({results: search, searching: loading})
      // but SearchBox can't send us a render prop, b/c it's loading this component via redirect!
      // so, I need to render <SearchResults> and pass it a render prop as well as search and loading:
      <SearchResults results={search} searching={loading} 
                     render={({suggestions, searching}) => this.renderMatchingPoints(suggestions, searching)}/>
    )
  }
}

export default graphql(schema.FullPointSearch, {
  skip: (ownProps) => !ownProps.query || (ownProps.query == '')
})(HeaderSearch)
