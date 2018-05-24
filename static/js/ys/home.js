import 'babel-polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
const { Map, List, Seq } = require('immutable');
const prettyI = require("pretty-immutable");
import gql from 'graphql-tag';
import { graphql, compose } from 'react-apollo';
import { PointList } from './components/PointList';
import * as schema from './schema';
import { Form, Text } from 'react-form';
import { Carousel } from 'react-responsive-carousel';
import MediaQuery from 'react-responsive';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import * as validations from './validations';
import config from './config';
import QuickCreateClaim from './components/QuickCreateClaim'
import NewClaim from './components/NewClaim'
import Spinner from './components/Spinner'


const EditorsPicks = graphql(schema.EditorsPicks, {
  props: ({ownProps, data: { loading, homePage }}) => ({
    loading: loading,
    points: homePage && homePage.editorsPicks
  })
})(PointList);

const newPointsDefaultPageSize = 7
const NewPoints = graphql(schema.NewPoints, {
  options: ({pointsPerPage}) => ({variables: {limit: pointsPerPage || newPointsDefaultPageSize}}),
  props: ({ownProps: {pointsPerPage}, data: { loading, newPoints = {}, fetchMore}}) => ({
    loading: loading,
    points: newPoints.points,
    hasMore: newPoints.hasMore,
    infiniteScroll: true,
    loadMorePoints: () => {
      return fetchMore({
        query: schema.NewPoints,
        variables: {cursor: newPoints.cursor, limit: pointsPerPage || newPointsDefaultPageSize},
        updateQuery: (previousResult, { fetchMoreResult }) => {
          fetchMoreResult.newPoints.points = [...previousResult.newPoints.points, ...fetchMoreResult.newPoints.points]
          return fetchMoreResult
        }
      })
    }
  })
})(PointList);

// For Responsive
const singleColumnThresholdForCarousel = 767.01;

class Home extends React.Component {

  state = {tabIndex: 0}

  focusNewTab = () => this.setState({tabIndex: 0})

  createNewPoint = (pointData) => {
    if (this.props.CurrentUserQuery.currentUser){
      return this.props.mutate({
        variables: pointData,
        update: (proxy, {data: {newPoint: { point }}}) => {
          this.focusNewTab()
          const variables = {limit: config.newPointsPageSize}
          const data = proxy.readQuery({ query: schema.NewPoints, variables: variables});
          data.newPoints.points.unshift(point);
          proxy.writeQuery({query: schema.NewPoints, variables: variables, data: data});
        }
      });
    } else {
      $("#loginDialog").modal("show");
      return Promise.reject("User not logged in");
    }
  }

  renderIllustration1 = () => {
     return <div className="explanationBlock">
       <img className="explanationImageCentered" src="/static/img/homePageIllustration_UX2_v02_2x_ClaimByClaim.png"/>
       <div className="explanationTextCentered">Make Arguments<br/>Claim-by-Claim</div>
     </div>
  }
  renderIllustration2 = () => {
     return  <div className="explanationBlock">
      <img className="explanationImageCentered" src="/static/img/homePageIllustration_UX2_v02_2x_Collaborate.png"/>
      <div className="explanationTextCentered lessWidth">Collaborate to get<br/>other perspectives</div>
     </div>
  }
  renderIllustration3 = () => {
     return  <div className="explanationBlock">
       <img className="explanationImageCentered flip" src="/static/img/homePageIllustration_UX2_v02_2x_Reuse.png"/>
       <div className="explanationTextCentered lessWidth">Re-use Claims in<br/>New Arguments</div>
     </div>
  }
  renderIllustration4 = () => {
     return  <div className="explanationBlock">
       <img className="explanationImageCentered" src="/static/img/homePageIllustration_UX2_v02_2x_FindUseful.png"/>
       <div className="explanationTextCentered lessWidth">Find useful<br/>Arguments</div>
     </div>
  }

  illustrations = () => {
    return <div className="row" id="explanationRowHomepage">
      <MediaQuery minWidth={singleColumnThresholdForCarousel}>
        <div className="">
            {this.renderIllustration1()}
            {this.renderIllustration2()}
            {this.renderIllustration3()}
            {this.renderIllustration4()}
        </div>
      </MediaQuery>
      <MediaQuery maxWidth={singleColumnThresholdForCarousel}>
      <Carousel autoPlay={false} interval={2500} infiniteLoop={true} showIndicators={true} showArrows={true} showThumbs={false} showStatus={false} showIndicators={false} useKeyboardArrows={true}>
          <div>
            {this.renderIllustration1()}
          </div>
          <div>
            {this.renderIllustration2()}
          </div>
          <div>
            {this.renderIllustration3()}
          </div>
          <div>
            {this.renderIllustration4()}
          </div>
        </Carousel>
      </MediaQuery>
    </div>;
  }

  render(){
    let homePage = this.props.data.homePage;
    let featuredPoint = homePage && homePage.featuredPoint;
    return <div className="infiniteWidth">
      {this.illustrations()}
      <div className="mainPageClaimCreationArea">
        <h3 className="mainPageClaimCreationLabel">Make an Argument You Want to Prove</h3>
        <QuickCreateClaim onSubmit={this.createNewPoint}/>
      </div>
      <div className="mainPageContentArea">
        <div id="mainPageFeaturedArea" className="mainPageContentArea">
          { featuredPoint ? <PointList point={featuredPoint} badge="Featured" prefix="featured"/> : <div className="spinnerPointList">Loading Featured Claim...</div> }
        </div>
        <div id="mainPageMainArea">
          <Tabs selectedTabClassName="tabUX2_selected" selectedIndex={this.state.tabIndex} onSelect={tabIndex => this.setState({ tabIndex })}>
            <TabList>
              <Tab className="tabUX2">New</Tab>
              <Tab className="tabUX2">Editor's Picks</Tab>
            </TabList>
            <TabPanel>
              <NewPoints pointsPerPage={config.newPointsPageSize} prefix="new"/>
            </TabPanel>
            <TabPanel>
              <EditorsPicks/>
            </TabPanel>
          </Tabs>
        </div>
      </div>
    </div>
  }
}

export const HomePage = compose(
  graphql(schema.CurrentUserQuery, {name: 'CurrentUserQuery'}),
  graphql(schema.HomePage),
  graphql(schema.NewPoint)
)(Home);
