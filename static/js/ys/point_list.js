import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import {GetPoint, EvidenceType, PointCard, ExpandedPointCard, Byline, newPointCard, expandedPointFieldsFragment} from './point';
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
    this.state = {expandedIndex: {}}
    this.isPointExpanded = this.isPointExpanded.bind(this);
    this.handleSeeEvidence = this.handleSeeEvidence.bind(this);
    this.handleHideEvidence = this.handleHideEvidence.bind(this);
  }

  isPointExpanded(point) {
    return this.state.expandedIndex[point.url]
  }

  handleSeeEvidence(point) {
    const i = this.state.expandedIndex
    i[point.url] = true
    this.setState({expandedIndex: i})
    console.log("see evidence for ", point.url)
  }

  handleHideEvidence(point) {
    const i = this.state.expandedIndex
    i[point.url] = false
    this.setState({expandedIndex: i})
    console.log("hide evidence for ", point.url)
  }

  renderPointCard(pointEdge, index) {
    return newPointCard(pointEdge,
                        {index: index,
                         expandedIndex: this.state.expandedIndex,
                         handleSeeEvidence: this.handleSeeEvidence,
                         handleHideEvidence:this.handleHideEvidence});
  }

  renderPointCards(data) {
    if (data.point) {
      return this.renderPointCard({node: data.point})
    } else if (data.points) {
      return this.renderPointCard(data.points.edges[0])
    } else {
        return <div>Could not find data.point or data.points, please check your query.</div>
    }
  }

  render(){
    console.log("render")
    if (this.props.loading) {
      return <div>Loading!</div>
    } else if (!(this.props.data.points || this.props.data.point)) {
      return <div>Loading points...</div>
    } else {
      return <div className="row">
        <div className="span12">
	{this.renderPointCards(this.props.data)}

        </div>
      </div>
    }
  }
}

function Post({edge, data}){
  let point = (data && !data.loading)? data.point : edge
  return <li key={point.title}>{point.title}({point.upVotes} votes)</li>
}

function PostList({data: {loading, points}}) {
  if (loading) {
    return <div>Loading</div>;
  } else {
  return (
      <div>
        <ul>
          {points.edges.map(edge =>
           <Post edge={edge} key={edge.node.title}/>
          )}
        </ul>
      </div>
  );
  }
}

const GetPoints = gql`
${expandedPointFieldsFragment}
query GetPoints {
  points(first: 1) {
    edges {
      node {
        ...pointFields
        ...evidenceFields
      }
    }
  }
}`;
//${pointFieldsFragment}

// return the "whysaurus url" for this page
function url(){
  let parts = window.location.pathname.split("/");
  return parts.pop() || parts.pop(); // the || accounts for a trailing slash
}
export const PointListWithPoints = graphql(GetPoints)(PointList);
export const PointListWithPoint = graphql(GetPoint, {options: {variables: {url: url()}}})(PointList);
export const PostListWithPoints = graphql(GetPoints)(PostList);



/*

    ...pointFields

    supportingPoints { edges { node { title, upVotes, ...pointFields }, relevance, type } },
    counterPoints { edges { node { title, upVotes, ...pointFields }, relevance, type } }

*/

