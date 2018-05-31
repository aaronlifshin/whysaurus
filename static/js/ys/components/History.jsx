import React from 'react'
import PropTypes from 'prop-types'
import { graphql, compose } from 'react-apollo';

import * as schema from '../schema';
import Spinner from './Spinner'


class History extends React.Component {

  version = ({point, supportingPoints, counterPoints, sources}) => <div>
    <h5>VERSION {point.version}</h5>
    <h3>{point.title}</h3>
    <p>BY <a href={point.authorURL}>{point.authorName}</a></p>
    <p>CREATED {point.dateEdited}</p>
    <p>Image URL: {point.imageURL}</p>
    <p>Image Description: {point.imageDescription}</p>
    {sources && sources.map(source => <p>Source: <a href={source.url}>{source.name}</a></p>)}
    {supportingPoints && <h4>Supporting Claims</h4>}
    {supportingPoints && supportingPoints.map(p => <p>{p.title} - VERSION {p.version}</p>)}

    {counterPoints && <h4>Counter Claims</h4>}
    {counterPoints && counterPoints.map(p => <p>{p.title} - VERSION {p.version}</p>)}

    </div>

  render() {
    const versions = this.props.data.history
    return <div>{versions && versions.map((version, i) => <div key={i}>{this.version(version)}</div>)}</div>
  }
}

export default graphql(schema.History)(History)
