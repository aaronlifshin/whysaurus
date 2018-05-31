import React from 'react'
import PropTypes from 'prop-types'
import { graphql, compose } from 'react-apollo';

import * as schema from '../schema';
import Spinner from './Spinner'


class History extends React.Component {

  version = ({point, supportingPoints, counterPoints, sources}) => <div className="historyVersion">
    <h5 className="heading">VERSION <span className="number">{point.version}</span></h5>
    <h3 className="historyClaimText">{point.title}</h3>
    <div className="historySection">
      <p className="historyItem">By <a href={point.authorURL}>{point.authorName}</a></p>
      <p className="historyItem">Created {point.dateEdited}</p>
    </div>
    <div className="historySection">    
      <p className="historyItem">Image URL: {point.imageURL}</p>
      <p className="historyItem">Image Description: {point.imageDescription}</p>
    </div>
    <div className="historySection">
      {sources && sources.map(source => <p className="historyItem">Source: <a href={source.url}>{source.name}</a></p>)}
    </div>
    
    <div className="historySection">    
      {supportingPoints && <p className="historySubheading">Supporting Claims</p>}
      {supportingPoints && supportingPoints.map(p => <p className="historyItem">{p.title}<span className="historyClaimVersionTag">V<span className="number">{p.version}</span></span></p>)}
    </div>

    <div className="historySection">    
      {counterPoints && <p className="historySubheading">Counter Claims</p>}
      {counterPoints && counterPoints.map(p => <p className="historyItem">{p.title}<span className="historyClaimVersionTag">V<span className="number">{p.version}</span></span></p>)}
    </div>
    
    <div className="historyDivision"></div>

   </div>

  render() {
    const versions = this.props.data.history
    return <div className="historyContent">
      <h2 className="historyHeadline">History</h2>
      {versions && versions.map((version, i) => <div key={i}>{this.version(version)}</div>)}
    </div>
  }
}

export default graphql(schema.History)(History)
