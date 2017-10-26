import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import {EvidenceType, PointCard, Byline} from './point';
const { Map, List, Seq } = require('immutable');
const prettyI = require("pretty-immutable");
import { gql, graphql } from 'react-apollo';

function* evidenceEdges(edges) {
  for (let edge of edges) {
    if (edge) {
      yield List(edge.node.supportingPoints ? edge.node.supportingPoints.edges : [])
      yield List(edge.node.counterPoints ? edge.node.counterPoints.edges : [])
    }
  }
}

export function evidenceRows(rowOfEdges) {
  let edges = List(evidenceEdges(rowOfEdges))
  return edges.first().zipAll(...edges.rest())
}

export function* edgeRows(rowOfEdges, depth = 0) {
  let row = List(rowOfEdges);
  if (row && !row.isEmpty()) {
    yield row.map(edge => Map(edge).set('depth', depth))
    for (let r of evidenceRows(row)) {
      for (let s of edgeRows(List(r), depth + 1)) {
	yield s
      }
    }
  }
}

class PointList extends React.Component {
  constructor(props) {
    super(props);
    this.handleSeeEvidence = this.handleSeeEvidence.bind(this);
    this.handleHideEvidence = this.handleHideEvidence.bind(this);
    this.renderPointCard = this.renderPointCard.bind(this);
    this.renderPointRow = this.renderPointRow.bind(this);
  }

  handleSeeEvidence(point) {
    console.log("see evidence for ", point.key)
  }

  handleHideEvidence(point) {
    console.log("hide evidence for ", point.key)
  }

  renderPointCard(pointEdge, index) {
    let point = pointEdge.get("node")
    if (point) {
      // TODO: use a different key for the div, probably
      return <div className="span5" key={point.title}>
        <PointCard point={point}
                   evidenceType={pointEdge.evidenceType}
                   handleSeeEvidence={this.handleSeeEvidence}
                   handleHideEvidence={this.handleHideEvidence}/>
	</div>
    } else {
      return <div className="span5" key={index}></div>
    }
  }

  renderPointRow(row, rowIndex) {
    return <div className="row-fluid" key={rowIndex} style={{marginLeft: `${row.depth}em`}}>
      {row.map(this.renderPointCard)}
    </div>
  }

  * edgesByRowAndColumn() {
    for (let row of edgeRows(List(this.props.data.points.edges))) {
      yield row
    }
  }

  render(){
    if (this.props.loading) {
      return <div>Loading!</div>
    } else if (!this.props.data.points) {
      return <div>Loading points...</div>
    } else {
      return <div className="row">
        <div className="span12">
	{Seq(this.edgesByRowAndColumn()).map(this.renderPointRow)}
        </div>
      </div>
    }
  }
}

function PostList({data: {loading, points}}) {
  if (loading) {
    return <div>Loading</div>;
  } else {
    return (
      <div>
        <ul>
          {points.map(point =>
            <li key={point.title}>
              {point.title}
              ({point.upVotes} votes)
            </li>
          )}
        </ul>
      </div>
    );
  }
}

const pointFieldsFragment = gql`
fragment pointFields on Point {
  title,
  authorName,
  authorURL,
  imageURL,
  upVotes,
  downVotes,
  numSupporting,
  numCounter,
  numComments,
  supportedCount
}
`

const getPoints = gql`
${pointFieldsFragment}
query Points {
  points(first: 1) {
    edges {
      node {
        ...pointFields

        supportingPoints { edges { node { title, upVotes, ...pointFields }, relevance, type } },
        counterPoints { edges { node { title, upVotes, ...pointFields }, relevance, type } }
      }
    }
  }
}`;

export const PointListWithPoints = graphql(getPoints)(PointList);
export const PostListWithPoints = graphql(getPoints)(PostList);


