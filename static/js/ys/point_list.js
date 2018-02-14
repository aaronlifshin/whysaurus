import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import { EvidenceType, PointCard, Byline,  ExpandedPointCard } from './point';
const { Map, List, Seq } = require('immutable');
const prettyI = require("pretty-immutable");
import gql from 'graphql-tag';
import { graphql } from 'react-apollo';
import { GetPoint } from './schema.js';

class PointList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {expandedIndex: {}}
    this.isPointExpanded = this.isPointExpanded.bind(this);
    this.handleSeeEvidence = this.handleSeeEvidence.bind(this);
    this.handleHideEvidence = this.handleHideEvidence.bind(this);
  }

  get parentPoint() {
    return this.props.parentPoint;
  }

  isPointExpanded(point) {
    return this.state.expandedIndex[point.url]
  }

  handleSeeEvidence(point) {
    const i = this.state.expandedIndex
    i[point.url] = true
    this.setState({expandedIndex: i})
    console.log("point list see evidence for ", point.url)
  }

  handleHideEvidence(point) {
    const i = this.state.expandedIndex
    i[point.url] = false
    this.setState({expandedIndex: i})
    console.log("point list hide evidence for ", point.url)
  }

  renderPoint(point) {
    if (this.isPointExpanded(point)) {
      return <ExpandedPointCard point={point} url={point.url} parentPoint={this.parentPoint} expanded={true}
                                onCollapse={() => this.handleHideEvidence(point)}/>
    } else {
      return <PointCard point={point} url={point.url} parentPoint={this.parentPoint}
                        onExpand={() => this.handleSeeEvidence(point)}/>
    }
  }

  renderEdge(edge) {
    if (this.isPointExpanded(edge.node)) {
      return <ExpandedPointCard point={edge.node} url={edge.node.url} link={edge.link} parentPoint={this.parentPoint} expanded={true}
                                onCollapse={() => this.handleHideEvidence(edge.node)}/>
    } else {
      return <PointCard point={edge.node} url={edge.node.url} link={edge.link} parentPoint={this.parentPoint} onExpand={() => this.handleSeeEvidence(edge.node)}/>
    }
  }

  render(){
    console.log("render")
    if (this.props.point) {
      return this.renderPoint(this.props.point);
    } else if (this.props.points) {
      return <div>
        {this.props.points.map((point, i) => this.renderPoint(point))}
      </div>
    } else if (this.props.data && this.props.data.loading) {
      return <div>Loading!</div>
    } else if (this.props.data && this.props.data.point) {
      return this.renderPoint(this.props.data.point);
    } else if (this.props.edges) {
      return <div>
        {this.props.edges.map((edge, i) => this.renderEdge(edge))}
        </div>
    } else {
      return <div>dunno what to do...</div>
    }
  }
}

export {PointList};

export const PointListWithPoint = graphql(GetPoint)(PointList);
