import 'babel-polyfill'
import React from 'react'
import ReactDOM from 'react-dom'
import Popup from "reactjs-popup"
import gql from 'graphql-tag'
import { Form, Text } from 'react-form'
import { Carousel } from 'react-responsive-carousel'
import MediaQuery from 'react-responsive'
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs'
import { graphql, compose } from 'react-apollo'

import { PointList } from './PointList'
import * as schema from '../schema'
import * as validations from '../validations'
import config from '../config';
import QuickCreateClaim from './QuickCreateClaim'
import NewClaim from './NewClaim'
import Spinner from './Spinner'
import { CloseLinkX } from './common'
import {withExpandedIndex} from './ExpandedIndex'

const EditorsPicks = graphql(schema.EditorsPicks, {
  props: ({ownProps, data: { loading, homePage }}) => ({
    loading: loading,
    points: homePage && homePage.editorsPicks
  })
})(PointList);

const newSectionPrefix = "new"
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

  constructor(props) {
    super(props);
    this.createNewPoint = this.createNewPoint.bind(this);
  }

  state = {
    terms_open: true,
    explanation_visible: true,
    tabIndex: 0
  }

  focusNewTab = () => this.setState({tabIndex: 0})

  createNewPoint = (pointData) => {
    if (this.props.CurrentUserQuery.currentUser){
      return this.props.mutate({
        variables: pointData,
        update: (proxy, {data: {newPoint: { point }}}) => {
          this.focusNewTab()
          this.props.expansion.expand(point, newSectionPrefix)
          this.setState({latestQuickCreate: point.url})
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
  closeExplanation = (e) => {
    this.setState({ explanation_visible: false })
    if (this.props.CurrentUserQuery.currentUser) {
      console.log('Confirming walkthrough')
      this.props.setUserFlag(this.props.CurrentUserQuery.currentUser.url, 'confirmHeaderWalkthrough', 1)
    } else {
      // Do we want to force/prompt a login?
      console.log('No user to confirm')
    }
  }
  renderIllustrationCloseX = () => {
    return <div id="gotItExplanation" className="explanationBlock" onClick={this.closeExplanation}>    
      <span className="editAreaClose">
        <a href='#' data-toggle="tooltip" title="Got It!"><CloseLinkX/></a>
      </span>
    </div>
  }
  renderIllustrationCloseButton = () => {
    return <div id="gotItExplanation" className="explanationBlock">  
      <button className="buttonUX2 buttonGotIt" onClick={this.closeExplanation}>Got It!</button>    
    </div>
  }  

  illustrations = () => {
    if (this.props.CurrentUserQuery.currentUser && this.props.CurrentUserQuery.currentUser.hasConfirmedHeaderWalkthrough) {
    
    }
    else {
      return this.state.explanation_visible &&
        <div className="row" id="explanationRowHomepage">
          <MediaQuery minWidth={singleColumnThresholdForCarousel}>
            <div className="">
              {this.renderIllustration1()}
              {this.renderIllustration2()}
              {this.renderIllustration3()}
              {this.renderIllustration4()}
              {this.renderIllustrationCloseX()}
            </div>
          </MediaQuery>
          <MediaQuery maxWidth={singleColumnThresholdForCarousel}>
            <Carousel autoPlay={false} interval={2500} infiniteLoop={false} showIndicators={true} showArrows={true}
                      showThumbs={false} showStatus={false} showIndicators={false} useKeyboardArrows={true}>
              <div>
                <span className="explanationLabel">This is how we do it:</span>
                {this.renderIllustration1()}
              </div>
              <div className="carouselMiddleSlide">
                {this.renderIllustration2()}
              </div>
              <div className="carouselMiddleSlide">
                {this.renderIllustration3()}
              </div>
              <div>
                <div className="carouselLastSlide">
                  {this.renderIllustration4()}
                  {this.renderIllustrationCloseButton()}
                </div>
              </div>
            </Carousel>
          </MediaQuery>
        </div>;
    }
  }

  confirmTerms = () => {
    console.log('Accepting Terms..')
    this.setState({ terms_open: false })
    this.props.acceptTerms(this.props.CurrentUserQuery.currentUser.url)
  }

  declineTerms = () => {
    console.log('Terms Declined')
    this.setState({ terms_open: false })
    window.location = '/logout';
  }

  // <button className="button" onClick={this.declineTerms}>Decline/Logout</button>
  termsAndConditionsPopup() {
  if (this.props.CurrentUserQuery.currentUser) {
      if (this.props.CurrentUserQuery.currentUser.hasConfirmedTermsAndConditions) {

      }
      else {
        return <span>
          <Popup modal open={!this.props.CurrentUserQuery.currentUser.hasConfirmedTermsAndConditions && this.state.terms_open}>
            <div id="termsPopup" className="modal reactjs-popup">
              <div className="modal-header">
                <span className="editAreaClose"><a onClick={this.declineTerms}><CloseLinkX/></a></span>
                <h3 className="header">We Value Transparency and Privacy</h3>
              </div>
              <div className="modal-body text-content">
                <p>Click "Agree" when you're ready —</p>
                <p>The key points:</p>
                <ul>
                  <li>* We store data including content you make, preferences and votes (which we keep anonymous), plus data about how you use Whysaurus which we use to make it better. </li>
                  <li>* We use cookies to help authenticate that you are you. </li>
                  <li>* Our <a target="_blank" href="/privacyPolicy">Privacy Policy</a> is based on a template designed for GDPR and gives all users the rights required by the EU. If you have questions you can always <a target="_blank" href="/contact">contact us</a>. </li>
                </ul>
              </div>
              <div className="modal-footer actions">
                <button className="btn btn-primary buttonUX2 pull-right" onClick={this.confirmTerms}>Agree</button>
              </div>
            </div>
          </Popup>
        </span>;
      }
    }
  }

  componentDidMount(){
    const params = new URLSearchParams(this.props.location.search)
    const focus = params.get("focusQuickCreate")
    if (focus == "true") {
      QuickCreateClaim.focus()
    }
  }

  render(){
    let homePage = this.props.data.homePage;
    let featuredPoint = homePage && homePage.featuredPoint;
    return <div className="infiniteWidth">
      {this.illustrations()}
      <div className="mainPageClaimCreationArea">
        <h3 className="mainPageClaimCreationLabel">We love good arguments</h3>
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
              <NewPoints pointsPerPage={config.newPointsPageSize} prefix={newSectionPrefix} latestQuickCreate={this.state.latestQuickCreate}/>
            </TabPanel>
            <TabPanel>
              <EditorsPicks/>
            </TabPanel>
          </Tabs>
        </div>
        {this.termsAndConditionsPopup()}
      </div>
    </div>
  }
}

export default compose(
  withExpandedIndex,
  graphql(schema.CurrentUserQuery, {name: 'CurrentUserQuery'}),
  graphql(schema.HomePage),
  graphql(schema.NewPoint),
  graphql(schema.AcceptTerms, {
    props: ({ mutate }) => ({
      acceptTerms: (userUrl) => mutate({variables: {userUrl}})
    })
  }),
  graphql(schema.SetUserFlag, {
    props: ({ mutate }) => ({
      setUserFlag: (userUrl, flag, value) => mutate({variables: {userUrl, flag, value}})
    })
  })
)(Home);
