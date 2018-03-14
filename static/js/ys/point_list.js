import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import { PointCard } from './point';
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
  }

  handleHideEvidence(point) {
    const i = this.state.expandedIndex
    i[point.url] = false
    this.setState({expandedIndex: i})
  }

  renderPoint(point) {
    if (this.isPointExpanded(point)) {
      return <PointCard key={point.url} url={point.url} point={point} expanded={true}
                        parentPoint={this.parentPoint}
                        onDelete={this.props.onDelete} onCollapse={() => this.handleHideEvidence(point)}/>
    } else {
      return <PointCard key={point.url} point={point} url={point.url} expanded={false}
                        parentPoint={this.parentPoint}
                        onDelete={this.props.onDelete} onExpand={() => this.handleSeeEvidence(point)}/>
    }
  }

  renderEdge(edge) {
    if (this.isPointExpanded(edge.node)) {
      return <PointCard key={edge.node.url} point={edge.node} url={edge.node.url} expanded={true}
                        link={edge.link} parentPoint={this.parentPoint}
                        onDelete={this.props.onDelete} onCollapse={() => this.handleHideEvidence(edge.node)}/>
    } else {
      return <PointCard key={edge.node.url} point={edge.node} url={edge.node.url} expanded={false}
                        link={edge.link} parentPoint={this.parentPoint}
                        onDelete={this.props.onDelete} onExpand={() => this.handleSeeEvidence(edge.node)}/>
    }
  }

  render(){
    if (this.props.point) {
      return this.renderPoint(this.props.point);
    } else if (this.props.points) {
      return <div>
        {this.props.points.map((point, i) => this.renderPoint(point))}
      </div>
    } else if (this.props.loading || (this.props.data && this.props.data.loading)) {
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
