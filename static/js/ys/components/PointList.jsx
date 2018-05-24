import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import gql from 'graphql-tag';
import { graphql } from 'react-apollo';
import { withRouter } from 'react-router';
import InfiniteScroll from 'react-infinite-scroll-component';
import PropTypes from 'prop-types';


import Spinner from './Spinner'
import { GetPoint } from '../schema';
import { PointCard, LinkedItemBullet } from './Point';
import config from '../config'

class PointListComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hideIrrelevant: true
    }
  }

  get parentPoint() {
    return this.props.parentPoint;
  }

  prefix = () => this.props.prefix || ''

  renderPoint = (point, badge) => {
    return <PointCard key={point.url} url={point.url} point={point}
                      parentPoint={this.parentPoint} prefix={this.prefix()}
                      onDelete={this.props.onDelete} badge={badge} />
  }

  renderEdge = (edge) => {
    return <PointCard key={edge.node.url} point={edge.node} url={edge.node.url}
                      link={edge.link} parentPoint={this.parentPoint} prefix={this.prefix()}
                      onDelete={this.props.onDelete}/>
  }

  renderPoints = (points) => this.props.points.map((point, i) => this.renderPoint(point))

  renderInfinitePoints = (points) => (
      <InfiniteScroll next={this.props.loadMorePoints} hasMore={this.props.hasMore}
                      loader={<div className="spinnerPointList"><Spinner /></div>} endMessage={<span className="pointListEndMessage">You've reached the end. Time to start a new argument!</span>}>
        {this.renderPoints(points)}
      </InfiniteScroll>
  )

  renderPointsWithMoreLink = (points) => <div>
    {this.renderPoints(points)}
    <a onClick={this.props.loadMorePoints}>Load More...</a>
  </div>

  renderEdges = (edges) => edges.map((edge, i) => this.renderEdge(edge))

  showIrrelevant = () => this.setState({hideIrrelevant: false})

  hideIrrelevant = () => this.setState({hideIrrelevant: true})

  relevanceThreshold = () => this.props.relevanceThreshold

  renderShowIrrelevantLink = () => <div className="listedClaimGroup">
    <LinkedItemBullet />
    <a className="toggleLowRelClaims" onClick={this.showIrrelevant}>Show Claims Below <span className="number">{this.relevanceThreshold()}%</span> Relevance</a>
  </div>

  renderHideIrrelevantLink = () => <div className="listedClaimGroup">
    <LinkedItemBullet />
    <a className="toggleLowRelClaims" onClick={this.hideIrrelevant}>Hide Claims Below <span className="number">{this.relevanceThreshold()}%</span> Relevance</a>
  </div>

  renderRelevantEdges = () => {
    const threshold = this.relevanceThreshold()
    if (threshold) {
      let relevantEdges = this.props.edges.filter(({link: {relevance}}) => relevance > threshold)
      if (relevantEdges.length != this.props.edges.length) {
        return <div>
          {this.renderEdges(this.state.hideIrrelevant ? relevantEdges : this.props.edges)}
          <span className="noRelevantClaimsArea">
            {(this.state.hideIrrelevant && relevantEdges.length == 0) && <span className="noRelevantClaimsMessage">No Relevant Claims.</span>}
            {this.state.hideIrrelevant ? this.renderShowIrrelevantLink() : this.renderHideIrrelevantLink()}
          </span>
        </div>
      } else {
        return this.renderEdges(this.props.edges)
      }
    } else {
      return this.renderEdges(this.props.edges)
    }
  }


  render(){
    if (this.props.point) {
      return this.renderPoint(this.props.point, this.props.badge);
    } else if (this.props.points) {
      if (this.props.loadMorePoints) {
        if (this.props.infiniteScroll) {
          return this.renderInfinitePoints(this.props.points)
        } else {
          return this.renderPointsWithMoreLink(this.props.points)
        }
      } else {
        return <div>
          {this.renderPoints(this.props.points)}
        </div>
      }
    } else if (this.props.loading || (this.props.data && this.props.data.loading)) {
      return <div className="spinnerPointList"><Spinner /></div>
    } else if (this.props.data && this.props.data.point) {
      return this.renderPoint(this.props.data.point);
    } else if (this.props.edges) {
      return this.renderRelevantEdges()
    } else {
      return <div>dunno what to do...</div>
    }
  }
}

const PointList = withRouter(PointListComponent);

export {PointList};
export const PointListWithPoint = graphql(GetPoint)(PointList);
