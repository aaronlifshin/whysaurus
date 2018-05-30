import React from 'react';
import { graphql, compose, withApollo } from 'react-apollo';
import gql from 'graphql-tag';
import { Form, Text } from 'react-form';
import MediaQuery from 'react-responsive';
import { CSSTransitionGroup } from 'react-transition-group' // ES6
import AnimateOnChange from 'react-animate-on-change';

import * as validations from '../validations';
import * as schema from '../schema';
import { UnlinkPointMutation, DeletePointMutation, CurrentUserQuery, EditPointQuery, AddEvidenceQuery, VoteQuery, RelevanceVoteQuery, GetPoint, GetCollapsedPoint, EditorsPicks, NewPoints } from '../schema';
import config from '../config'

import {PointList} from './PointList'
import AddEvidence from './AddEvidence'
import EditPoint from './EditPoint'
import EditImage from './EditImage'
import EditSources from './EditSources'
import RelevanceRater from './RelevanceRater'
import Comments from './Comments'
import { CloseLinkX } from './common'
import Spinner from './Spinner'
import { withExpandedIndexForPoint } from './ExpandedIndex'

export const EvidenceType = Object.freeze({
    ROOT: Symbol("root"),
    SUPPORT:  Symbol("supporting"),
    COUNTER: Symbol("counter")
});


class Byline extends React.Component {
  constructor(props) {
    super(props)
    this.handleClickNoProp = this.handleClickNoProp.bind(this);
  }

  handleClickNoProp(e) {
    e.stopPropagation();
  }

  get point() {
    return this.props.point;
  }

  contributorsPlusAuthor() {
    let contributorsPlusAuthor = this.point.numUsersContributed + 1
    return contributorsPlusAuthor;
  }

  contributorsDropdown() {
    return <span>
      { (this.contributorsPlusAuthor() > 1) && <span className="bylineOtherUsers dropdown">
          <a onClick={this.handleClickNoProp} className="easierToClickOn dropdown-toggle" data-toggle="dropdown"><i className="far fa-user iconWithStat"></i></a>
          <ul id="" className="contributorsMenu dropdown-menu dropdown-menu-with-caret" role="menu" aria-labelledby="dropdownMenu">
            <div className="dropdown-caret"><div className="caret-outer"></div><div className="caret-inner"></div></div>
            <li><span><span className="number">{this.contributorsPlusAuthor()}</span> Contributors</span></li>
          </ul>
        </span>
      }
      </span>
  }

  render(){
    let topClass = `${(this.contributorsPlusAuthor() <= 1) && "cardTopRowItem" }`
    return <span className={topClass}>
      <span className="byline">
        <span>By <a className="bylineAuthor" target="_blank" tabIndex="-1" href={"/user/" + this.point.authorURL}>@{this.point.authorName}</a>{this.contributorsDropdown()}
        </span>
      </span>
    </span>
  }
}

class ShareIconArea extends React.Component {
  constructor(props) {
    super(props)
    //this.handleClickNoProp = this.handleClickNoProp.bind(this);
  }

  postOnFacebook = (e) => {
    var url = this.props.point.url;
    var pointTitle = this.props.point.title;
    var dialogParams = {
        app_id: 144595249045851,
        method: 'feed',
        link: "https://www.whysaurus.com/point/" + url,
        name: pointTitle,
        description: 'Debating on whysaurus: ' + pointTitle + ' \n Do you agree? Disagree? Got something to add to the debate?'
    };
    var imageUrl = this.props.point.imageURL || null;
    if (!imageUrl) {
        // if there is no image in the page, pass the logo
        imageUrl = window.location.protocol + "//" + window.location.host + "/static/img/whysaurus_logo.png";
        dialogParams['picture'] = imageUrl;
    } else {
        imageUrl = imageUrl.slice(2);
    }

    FB.ui(dialogParams, function(response){});
  }

  sharePointOnTwitter = (e) => {
    var url = this.props.point.url;
    var pointTitle = this.props.point.title;
    var len = pointTitle.length;
    var text = "";
    if (len > 115) {
        text = pointTitle.substring(0,114) + "..." + "https://www.whysaurus.com/point/" + url;
    } else {
        text = pointTitle + " https://www.whysaurus.com/point/" + url;
    }
    var webUrl = "http://twitter.com/intent/tweet?text="+encodeURIComponent(text);
    window.open(webUrl,'_blank');
  }

  render(){
    return <span className="shareIconArea">
       <a href={"https://www.whysaurus.com/point/" + this.props.point.url + "/"}>
        <div className="claimShareIcon fas fa-link"></div>
       </a>
      <a onClick={this.postOnFacebook}>
        <div className="claimShareIcon fab fa-facebook-square"></div>
      </a>
      <a onClick={this.sharePointOnTwitter}>
        <div className="claimShareIcon fab fa-twitter"></div>
      </a>
      <a target="_blank" href={"mailto:?subject=Someone is wrong on the internet&body=Hi,%0D%0A%0D%0ACheck out this argument on Whysaurus and add your voice!%0D%0A%0D%0A" + this.props.point.title + ". %0D%0Ahttps://www.whysaurus.com/point/" + this.props.point.url + ""}>
        <div className="claimShareIcon far fa-envelope"></div>
      </a>
    </span>
  }
}

function SupportingCount(props){
  return <span className="cardTopRowItem"><span className="iconWithStat"><span className="fas fa-level-up-alt"></span></span><span className="number">{props.point.supportedCount}</span> Other Links</span>
}

/*
        Code to check if current user is the point Author
          {this.props.data.currentUser &&
          this.props.data.currentUser.url == this.point.authorURL &&
          <a onClick={this.handleClickEditClaimText} className="editLink" >Edit</a>}
*/

// thanks, https://stackoverflow.com/questions/29981236/how-do-you-hover-in-reactjs-onmouseleave-not-registered-during-fast-hover-ove
const Hover = ({ onHover, children }) => (
    <span className="hover">
      <span className="hover__no-hover">{children}</span>
      <span className="hover__hover bringToFront">{onHover}</span>
    </span>
)

function RawScore(props){
  return <span className="cardTopRowItem"><span className="iconWithStat"><span className="fas fa-level-up-alt"></span></span>Raw Score: <span className="number">{props.point.pointValueRaw}</span></span>
}

function EngagementScore(props){
  return <span><span className="number">{props.point.engagementScore}</span><span> Engagement</span></span>
}

// Perhaps we should rename this to StatsCompontent? -JF
const VoteStatsComponent = ({point, user}) => (
    <div className="vote-stats">
      <p>
        <span className="number">{point.upVotes}</span> Agrees<br/>
        <span className="number">{point.downVotes}</span> Disagrees<br/>
      </p>
      <div className="menuDivider"></div>
      <p>
        <span className="number">{point.numSupporting}</span> Supporting Claim{point.numSupporting != 1 ? "s" : null}<br/>
        <span className="number">{point.numCounter}</span> Counter Claim{point.numCounter != 1 ? "s" : null}<br/>
      </p>
      {user && user.admin && <p className="admin">
          <span><EngagementScore point={point} /></span>
        </p>}
    </div>
)

const VoteStats = graphql(schema.CurrentUserQuery, {
  props: ({ownProps, data: {loading, currentUser, refetch}}) => ({
    userLoading: loading,
    user: currentUser,
    refetchUser: refetch
  })
})(VoteStatsComponent)

// used in PointCard and in PointList for the irrelevant claims links
export const LinkedItemBullet = () => (
  <div className={"dottedLine dottedLineElbow"}></div>
)

class PointComponent extends React.Component {
  constructor(props) {
    super(props)
    this.state = {saving: false}
    this.handleToggleEvidence = this.handleToggleEvidence.bind(this);
  }

  get point() {
    return this.props.point;
  }

  handleToggleEvidence(e) {
    e.stopPropagation(); // prevents click from passing up to parent, which seems to break the functionality (even though they do the same thing)
    console.log("PointComponent : toggle evidence!")
    this.props.onClick && this.props.onClick()
  }

  titleUI() {
    return <span className="pointTitle">
      <a tabIndex="-1" onClick={this.handleToggleEvidence}>{this.point.title}</a>
    </span>
  }

  // TODO: make it not animate when card redraws
  render(){
    const score = this.point.pointValue
    return <div className="claimTextDisplay pointCardPaddingH pointCardPaddingHExtra">
      {this.titleUI()}
        <span className="scoreAnimContainerMax score">
          <span className="scoreAnimContainerReset">
            <Hover onHover={<VoteStats point={this.point}/>}>
             <span className="ux2ScoreInLine number">
               <span className={score < 0 ? "negativeScore": "positiveScore"}>
                <AnimateOnChange baseClassName="scorePreAnimate" animationClassName="Score--bounce" animate={score.diff != 0}>
                  {score >= 0 && "+"}{score}
                </AnimateOnChange>
               </span>
              </span>
            </Hover>
          </span>
        </span>
      </div>
  }
}

const Point = compose(
  graphql(CurrentUserQuery),
)(PointComponent)

class Sources extends React.Component {
  render(){
    const sources = this.props.point.sources
    return <div className="sources pointCardPaddingH">
      {sources && sources.map(({name, url}, i) =>
        <a key={i} className="source" tabIndex="-1" target="_blank" href={url}>
          <span className="iconSourcesSmall">
            <span className="fas fa-book"></span>
          </span>
          <span className="sourceLabel">{name || url}</span>
        </a>
      )}
    </div>
  }
}


class CommentsLink extends React.Component {
  constructor(props) {
    super(props)
  }

  render(){
    return <span className="cardTopRowItem">
      <a className="commentLink easierToClickOn" onClick={this.props.onClick}>
          <span className="iconWithStat far fa-comment"></span>
          { (this.props.point.root.numComments > 0) && <span className="number inlineBlock">{this.props.point.root.numComments}</span> }
      </a>
    </span>
  }
}

class EvidenceLink extends React.Component {
  hasEvidence = () => {
    const {point} = this.props;
    return point.numSupporting > 0 || point.numCounter > 0;
  }

  handleClickSee = (e) => {
    e.stopPropagation(); // prevents click from passing up to parent, which seems to break the functionality (even though they do the same thing)
    this.props.onSee && this.props.onSee()
    ga('send', 'event', 'Main Page', 'Expand Point', this.props.point.url);
  }

  handleClickHide = (e) => {
    e.stopPropagation(); // prevents click from passing up to parent, which seems to break the functionality (even though they do the same thing)
    this.props.onHide && this.props.onHide()
  }

  evidenceButton = () => {
    if (this.hasEvidence()) {
      if (this.props.expanded) {
        if (this.props.expansionLoading) {
          return <span className="cardBottomAction">Loading...</span>
        } else {
          return <a className="cardBottomAction hideEvidence" onClick={this.handleClickHide}>Hide Evidence</a>
        }
      } else {
        return <a className="cardBottomAction seeEvidence" onClick={this.handleClickSee} onMouseOver={this.props.mouseOverPreload}>See Evidence</a>
      }
    } else {
      if (this.props.expanded) {
        return <a className="cardBottomAction hideEvidence" onClick={this.handleClickHide}>Hide Buttons</a>
      } else {
        return <a className="cardBottomAction" onClick={this.handleClickSee}>Add Evidence</a>
      }
    }
  }

  render(){
    return <span className="evidenceContainer">{this.evidenceButton()}</span>
  }
}

class AgreeDisagreeComponent extends React.Component {
  constructor(props) {
    super(props);
    // This binding is necessary to make `this` work in the callback
    this.handleClickAgree = this.handleClickAgree.bind(this);
    this.handleClickDisagree = this.handleClickDisagree.bind(this);
  }

  // move focus to the next point card, uses tabbable.js plugin
  focusOnNextCard() {
    setTimeout(function () { $.tabNext() } , 900)
  }

  handleClickAgree(e) {
    e.stopPropagation(); // prevents click from passing up to the parent, which would toggle expansion
    console.log("AgreeDisagreeComponent : agree");
    if (this.props.data.currentUser){
      this.props.mutate({
        variables: {url: this.props.point.url,
                    vote: this.props.point.currentUserVote == 1 ? 0 : 1,
                    parentURL: this.props.parentPoint && this.props.parentPoint.url}
      }).then( res => {
        console.log(res)
      });
    this.focusOnNextCard()
    } else {
      $("#loginDialog").modal("show");
    }
  }

  handleClickDisagree(e) {
    e.stopPropagation(); // prevents click from passing up to the parent, which would toggle expansion
    console.log("AgreeDisagreeComponent : disagree");
    if (this.props.data.currentUser){
      this.props.mutate({
        variables: {url: this.props.point.url,
                    vote: this.props.point.currentUserVote == -1 ? 0 : -1,
                    parentURL: this.props.parentPoint && this.props.parentPoint.url}
      }).then( res => {
        console.log(res)
      });
    this.focusOnNextCard()
    } else {
      $("#loginDialog").modal("show");
    }
  }

  agreeClass(){
    return "cardBottomAction agree" + (this.props.point.currentUserVote == 1 ? " current-vote" : "")
  }

  disagreeClass(){
    return "cardBottomAction disagree" + (this.props.point.currentUserVote == -1 ? " current-vote" : "")
  }

  render(){
    return <span>
      <a className={this.agreeClass()} onClick={this.handleClickAgree}>Agree</a>
      <a className={this.disagreeClass()} onClick={this.handleClickDisagree}>Disagree</a>
      </span>
    }
}

const AgreeDisagree = compose(
  graphql(VoteQuery),
  graphql(CurrentUserQuery),
)(AgreeDisagreeComponent)

class PointCardComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      relevanceRater: false
    }
    this.handleSeeEvidence = this.handleSeeEvidence.bind(this);
    this.handleHideEvidence = this.handleHideEvidence.bind(this);
    this.handleToggleEvidence = this.handleToggleEvidence.bind(this);
    this.handleRelClick = this.handleRelClick.bind(this);
    this.handleClickEditClaimText = this.handleClickEditClaimText.bind(this);
    this.handleClickEditClaimSources = this.handleClickEditClaimSources.bind(this);
    this.handleClickEditClaimImage = this.handleClickEditClaimImage.bind(this);
    this.handleClickEditComments = this.handleClickEditComments.bind(this);
    this.handleCancelEditClaimText = this.handleCancelEditClaimText.bind(this);
    this.handleCancelEditClaimSources = this.handleCancelEditClaimSources.bind(this);
    this.handleCloseComments = this.handleCloseComments.bind(this);
    this.handleClickNoProp = this.handleClickNoProp.bind(this);
  }

  // TODO: this simple function is also defined in the EditPointComponent component - can/should it be declared in a single place somehow?
  handleClickNoProp(e) {
    e.stopPropagation();
  }

  handleClickEditClaimText(e) {
    e.stopPropagation();
    this.setState({editingClaimText: true})
  }
  handleClickEditClaimSources(e) {
    e.stopPropagation();
    this.setState({editingClaimSources: true})
  }
  handleClickEditClaimImage(e) {
    e.stopPropagation();
    this.setState({editingClaimImage: true})
  }
  handleClickEditComments(e) {
    e.stopPropagation();
    const expansion = this.props.expansion
    if (expansion.isExpanded(this.point, this.commentPrefix()))
      expansion.collapse(this.point, this.commentPrefix())
    else
      expansion.expand(this.point, this.commentPrefix())
  }

  handleCancelEditClaimText(e) {
    e.stopPropagation()
    this.setState({editingClaimText: false})
  }
  handleCancelEditClaimSources(e) {
    e.stopPropagation()
    this.setState({editingClaimSources: false})
  }
  handleCloseEditClaimImage = (e) => {
    e && e.stopPropagation()
    this.setState({editingClaimImage: false})
  }
  handleCloseComments(e) {
    e && e.stopPropagation()
    this.setState({editingComments: false})
  }

  editingSomething() {
    return (this.state.editingClaimText || this.state.editingClaimSources || this.state.editingClaimImage || this.state.editingComments)
  }

   //Assign focus - WIP

  // TO DO: make focus on the 1st point loaded (not the last one, as its currently doing) --> may need to happen in Evidence?
  scroll() {
    // this.cardToScrollTo.scrollIntoView({behavior: "smooth", block: "end", inline: "nearest"});
  }

  componentDidMount() {
    console.log("pointCard: componentDidMount()");
    //this.cardToFocusOn.focus();

    // scroll browser to unfolded claim
    // TO DO: currently scrolling to get bottom unfolded claim into view, but maybe we should be scrolling to get the
    //        unfolded claim into view and as many of its children as possible; wait till focus() is sorted before pursuing
    // TO DO: Note that our two refs inputs are writing over eachother; we need to build a container to hold them and edit that as per https://github.com/react-native-training/react-native-elements/issues/392
    // TO DO: "smooth" option not currently supported by Safari or iOS Safari
    //this.cardToScrollTo.scrollIntoView({behavior: "smooth", block: "start", inline: "nearest"});
    //setTimeout( this.scroll() , 3600);
  }
/*
  // uses tabbable.js plugin
  focusOnNextCard() {
    setTimeout(function () { $.tabNext() } , 1200);
    console.log("pointCard : focusOnNextCard() ")
  }
*/

  get point() {
    return (this.props.data && this.props.data.point) ? this.props.data.point : this.props.point
  }

  get evidenceType() {
    if (this.props.link){
      switch (this.props.link.type) {
        case "supporting":
          return EvidenceType.SUPPORT
        case "counter":
          return EvidenceType.COUNTER
        default:
          return null
      }
    }
  }

  // TODO: the "root" case doesn't seem to be working -JF
  evidenceTypeClass() {
    switch (this.evidenceType){
      case EvidenceType.ROOT:
        return "root";
      case EvidenceType.SUPPORT:
        return "support";
      case EvidenceType.COUNTER:
        return "counter";
      default:
        return "";
    }
  }

  get relevance() {
    return this.props.link && this.props.link.relevance
  }

  get sortScore() {
    return this.props.link && this.props.link.sortScore
  }

  get relevanceVoteCount() {
    return this.props.link && this.props.link.voteCount
  }

  // toggle Relevance Rater
  handleRelClick(e) {
    //console.log("toggle relevance ui");
    e.stopPropagation();
    if (this.state.relevanceRater) {
      this.setState({ relevanceRater: false })
    } else {
      this.setState({ relevanceRater: true })
    }
  }

  showRelevanceRater = (e) => {
    e.stopPropagation();
    this.setState({ relevanceRater: true })
  }

  hideRelevanceRater = (e) => {
    e.stopPropagation();
    this.setState({ relevanceRater: false })
  }

  relevanceCtrlUI() {
    if (this.props.parentPoint) {
      return <span>
        { this.state.relevanceRater ?
            <div className="relevanceCtrlArea">
              <RelevanceRater point={this.point} parentPoint={this.props.parentPoint} link={this.props.link}  onClose={this.hideRelevanceRater}/>
            </div> :
            <span className="noRelevanceCtrl"></span>
        }
      </span>
    }
  }

  // TODO: make animation only occur on the claim being manipulated (rather than on all relevance)
  //  code with animation:  <AnimateOnChange baseClassName="relevanceDisplay" animationClassName="Score--bounce" animate={this.relevance != -1}>{this.relevance}%</AnimateOnChange>
  relevanceLinkUI() {
    if (this.props.parentPoint) {
      let classesRelevanceLink = `relevanceLink ${this.evidenceTypeClass()}`
      return <a className={classesRelevanceLink} onClick={this.handleRelClick}>
        <div className="relevanceLinkArea">
          <div className="dottedLine dottedLineRelevanceLink"></div>
          <span className="relevanceDisplay number"><span className="positionRelDisplay">{this.relevance}<span className="perctSignSmallRelLink">%</span></span></span>
          <LinkedItemBullet />
        </div>
      </a>
    } else {
      return null
    }
  }

  expand(){
    this.props.onExpand()
  }

  collapse(){
    this.props.onCollapse()
  }

  handleSeeEvidence() {
    this.expand();
  }

  handleHideEvidence() {
    this.collapse();
  }

  // When user clicks on the pointTitle or the stackGroup
  // Disabled when the claim is being edited
  handleToggleEvidence() {
    if (!this.editingSomething()) {
      if (this.expanded()) {
        this.collapse()
      } else {
        this.expand()
      }
    }
  }

  expanded() {
    return this.props.expanded && !this.props.expansionLoading;
  }
  // TODO old django pointBox.html also checks if point.imageURL.strip exists - is that necessary here? -JF
  hasImage() {
    //console.log("hasImage() : " + this.point.imageURL  )
    return this.point.imageURL
  }
  displayImage() {
    return (this.hasImage() && !this.state.editingClaimText && !this.state.editingClaimSources)
  }
  image() {
  if (this.displayImage())
    return  <div className="span3 pointCardImageContainer"><img className="pointCardImage" src={this.point.fullPointImage} alt={this.point.imageDescription}></img></div>
  }
  textContentWidth() {
    if (this.displayImage()) {
      return "span9"
    } else {
      return "span12 fullWidthContent"
    }
  }

  // TODO: this is declared as a local function in two different componants - should it be a global fuction or a const? -JF
  numSupportingPlusCounter(){
    return ( this.point.numSupporting + this.point.numCounter)
  }
  hasSupportingEvidence = () => (
    this.point.supportingPoints && this.point.supportingPoints.edges.length > 0
  )
  hasCounterEvidence = () => (
    this.point.counterPoints && this.point.counterPoints.edges.length > 0
  )

  isChildExpanded = (child) =>
    !!this.props.expansion.isExpanded(child, this.childPrefix())

  childrenExpanded = (edgeName) => {
    const point = this.props.point
    return point && point[edgeName] && !!point[edgeName].edges.find(edge => this.isChildExpanded(edge.node))
  }

  supportingChildrenExpanded = (point) => this.childrenExpanded('supportingPoints')

  counterChildrenExpanded = (point) => this.childrenExpanded('counterPoints')

  relevantChildrenExpanded = (point) => this.childrenExpanded('relevantPoints')

  evidence() {
    if (this.expanded() ) {
      // If this is the first level down, remove an indent bc the Relevance widget effectively creates one when it appears for the first time
      let classesEvidenceBlock = `evidenceBlock ${!this.props.parentPoint ? "removeOneIndent" : ""}`
      //old idea:  <div className="arrowPointToSupport">{this.numSupportingPlusCounter() > 0 ? "↓" : null}</div>
      //console.log("pointCard : evidence() ")
      if (this.numSupportingPlusCounter() == 0) {
        return <div className={classesEvidenceBlock + " evidenceBlockEmpty"}>
          <AddEvidence point={this.point} type={"DUAL"}/>
        </div>
      } else {
        return <div className={classesEvidenceBlock}>
         {this.props.parentPoint && <div className="dottedLine dottedLineExpansionIndicator"></div>}
         {this.renderDottedLinesEvidenceHeaderOrMargin()}
         <MediaQuery minWidth={config.singleColumnThreshold}>
          {this.hasSupportingEvidence() && this.supportingPoints()}
          {this.hasCounterEvidence() && this.counterPoints()}
         </MediaQuery>
         <MediaQuery maxWidth={config.singleColumnThreshold}>
          {this.point.relevantPoints && this.relevantPoints()}
         </MediaQuery>
        </div>
      }
    }
  }

  renderDottedLinesEvidenceHeaderOrMargin() {
    return <div className="dottedLinesSplitEvidenceHeader">
      <MediaQuery minWidth={config.singleColumnThreshold}>
        {this.hasSupportingEvidence() && this.hasCounterEvidence() &&
          <div>
            <div className="dottedLinesSplitEvidenceSupport"></div>
            <div className="dottedLinesSplitEvidenceCounter"></div>
          </div>
        }
      </MediaQuery>
    </div>
  }

  prefix = () => this.props.prefix || ''

  childPrefix = () => this.prefix() + this.props.point.url

  commentPrefix = () => 'comments-'

  supportingPoints(){
    if (this.expanded() && this.point.supportingPoints) {
      return <div className="evidenceBlockSupport evidenceBlockFirstColAlignment">
        <div className="evidenceList">
          <div className="heading supportHeading">Evidence For</div>
          <PointList edges={this.point.supportingPoints.edges} parentPoint={this.point} relevanceThreshold={config.relevanceThreshold} prefix={this.childPrefix()}/>
          {!this.supportingChildrenExpanded() && (this.point.counterPoints.edges.length < 1 ? <AddEvidence point={this.point} type={"DUAL"}/> : <AddEvidence point={this.point} type={"SUPPORT"}/>)}
        </div>
      </div>
    }
  }

  counterPoints(){
    if (this.expanded() && this.point.counterPoints){
      let evidenceBlockCounterClasses = `evidenceBlockCounter ${this.point.supportingPoints.edges.length < 1 ? "evidenceBlockFirstColAlignment" : ""}`
      return <div className={evidenceBlockCounterClasses}>
        {this.point.supportingPoints.edges.length > 0 ? <div className="dottedLineCounterConnector"></div> : "" }
        <div className="evidenceList">
          <div className="heading counterHeading">Evidence Against</div>
          <PointList edges={this.point.counterPoints.edges} parentPoint={this.point} relevanceThreshold={config.relevanceThreshold} prefix={this.childPrefix()}/>
          {!this.counterChildrenExpanded() && (this.point.supportingPoints.edges.length < 1 ? <AddEvidence point={this.point} type={"DUAL"}/> : <AddEvidence point={this.point} type={"COUNTER"}/>) }
        </div>
      </div>
    }
  }

  // TODO: if users ask about this, add <span className="sortBy">Sorted by Relevance</span>
  relevantPoints(){
    if (this.expanded() && this.point.relevantPoints){
      return <div className="evidenceBlockBoth evidenceBlockFirstColAlignment">
        <div className="evidenceList">
          {this.point.relevantPoints.edges.length > 0 && <div className="heading supportHeading">Evidence</div>}
        <PointList edges={this.point.relevantPoints.edges} parentPoint={this.point} relevanceThreshold={config.relevanceThreshold} prefix={this.childPrefix()}/>
        {!this.relevantChildrenExpanded() && <AddEvidence point={this.point} type={"DUAL"}/>}
        </div>
      </div>
    }
  }


  // TODO: this is defined in the model point.py, so we could pass it up through GraphQL if that would be faster
  linksRatio() {
    let sup = this.point.numSupporting
    let cou = this.point.numCounter
    if (sup == 0 && cou == 0)
      return 50
    else if (cou == 0)
      return 100
    else if (sup == 0)
      return 0
    else {
      let ratio = sup/(sup + cou)
      //console.log("linksRatio : " + ratio)
      return ratio
    }
  }

  // TODO: this could be removed by moving its logic into render() and its DOM into <Sources>
  sources(){
    if (this.point.sources){
      return <div className="row-fluid">
        <div className="pointText span12">
          <Sources point={this.point}/>
        </div>
      </div>
    }
  }

  currentUserIsAdmin = () => (
    this.props.currentUser && this.props.currentUser.admin
  )

  hasParent = () => (this.props.parentPoint)

  hasBadge = () => (this.props.badge)

  handleClickDelete = (e) => {
    e.stopPropagation();
    this.setState({deleting: true})
    this.props.delete(this.point.url).
      then((success) => {
        console.log("Delete succeeded, affected queries should reload automatically.")
        console.log(success)
        this.props.onDelete && this.props.onDelete(success);
      },
           (error) => {
             console.log("Delete failed: " + error)
             this.setState({deleting: false})
           })
  }

  handleClickMakeFeatured = (e) => {
    e.stopPropagation();
    this.props.makeFeatured(this.point.id)
  }

  handleClickSetEditorsPick = (e) => {
    e.stopPropagation();
    this.props.setEditorsPick(this.point.id)
  }

  handleClickUnlink = (e) => {
    e.stopPropagation()
    this.setState({unlinking: true})
    this.props.unlink(this.props.parentPoint.url, this.point.url, this.props.link.type).then((success) => {
      console.log("unlink success")
    },
                             (error) => {
                               console.log("unlink error: " + error)
                             })
  }

  // TODO: Make SupportingCount work and move out of admin
  // using ascii &#9776; instead of font-awesome "bars" icon bc its more elegant
  moreMenu() {
    let moreMenuSourcesLabel = `${this.point.sources ? "Edit Sources" : "Add Sources"}`
    let moreMenuImageLabel = `${this.hasImage() ? "Edit Image" : "Add Image"}`
    return <span className="cardTopRowItem dropdown">
      <a onClick={this.handleClickNoProp} className="moreMenuLink easierToClickOn dropdown-toggle"  data-toggle="dropdown">&#9776;</a>
      <ul id="" className="moreMenu dropdown-menu dropdown-menu-with-caret" role="menu" aria-labelledby="dropdownMenu">
        <div className="dropdown-caret"><div className="caret-outer"></div><div className="caret-inner"></div></div>
        <li><a onClick={this.handleClickEditClaimText} className="" ><span className="iconWithStat"><span className="fas fa-pencil-alt"></span></span>Edit Claim</a></li>
        <li><a onClick={this.handleClickEditClaimSources} className="" ><span className="iconWithStat"><span className="fas fa-book"></span></span>{moreMenuSourcesLabel}</a></li>
        <li><a onClick={this.handleClickEditClaimImage} className="" ><span className="iconWithStat"><span className="far fa-image"></span></span>{moreMenuImageLabel}</a></li>
        <li className="divider"></li>
        { this.hasParent() && <li><a onClick={this.handleClickUnlink}><span className="iconWithStat"><span className="fa fa-unlink"></span></span>Unlink</a></li>  }
        <li><a onClick={this.handleClickNoProp} target="_blank" href={"/claim/" + this.point.url}><span className="iconWithStat"><span className="fas fa-external-link-alt"></span></span>Open in new tab</a></li>
        <li><a onClick={this.handleClickNoProp} target="_blank" href={"/history/" + this.point.url}><span className="iconWithStat"><span className="fas fa-external-link-alt"></span></span>History</a></li>
        { this.currentUserIsAdmin() && <li className="admin"><a onClick={this.handleClickDelete}><span className="iconWithStat"><span className="far fa-trash-alt"></span></span>Delete</a></li>  }
        { this.currentUserIsAdmin() && <li className="admin"><a onClick={this.handleClickMakeFeatured}><span className="iconWithStat"><span className="fas fa-star"></span></span>Make Featured</a></li>  }
        { this.currentUserIsAdmin() && <li className="admin"><a onClick={this.handleClickSetEditorsPick}><span className="iconWithStat"><span className="fas fa-ribbon"></span></span>Set Editor's Pick</a></li>  }
        { this.currentUserIsAdmin() && <li className="admin"><SupportingCount point={this.point} /></li> }
      </ul>
    </span>
  }

/*
        Code to check if current user is the point Author
          {this.props.data.currentUser &&
          this.props.data.currentUser.url == this.point.authorURL &&
          <a onClick={this.handleClickEditClaimText} className="editLink" >Edit</a>}
*/

  shareMenu() {
    return <span className="cardTopRowItem dropdown">
      <a onClick={this.handleClickNoProp} className="shareMenuLink dropdown-toggle"  data-toggle="dropdown"><i className="fas fa-share-alt"></i></a>
      <ul id="" className="dropdown-menu dropdown-menu-with-caret shareMenu" role="menu" aria-labelledby="dropdownMenu">
        <div className="dropdown-caret"><div className="caret-outer"></div><div className="caret-inner"></div></div>
        <li><a className="" ><span className="iconWithStat"><span className="fas fa-link"></span></span></a></li>
        <li><a className="" ><span className="iconWithStat"><span className="fab fa-facebook-square"></span></span></a></li>
        <li><a className="" ><span className="iconWithStat"><span className="fab fa-twitter"></span></span></a></li>
        <li><a className="" ><span className="iconWithStat"><span className="far fa-envelope"></span></span></a></li>
      </ul>
    </span>
  }

 pointTextComponent() {
    const point = this.point;
    if (this.state.editingClaimText){
      return <EditPoint point={point} onCancel={this.handleCancelEditClaimText}/>
    } else {
      return <Point point={point} onClick={this.handleToggleEvidence}/>
    }
  }

  preloadPoint = () => {
    console.log("preloading data for " + this.point.url)
    this.props.client && this.props.client.query({
      query: GetPoint,
      variables: {url: this.point.url}
    })
  }


  // TODO: ref being used on the pointCard to grab it for focus assignment, though that's not fully implemented yet
  render(){
    if (this.state.deleting) {
      return <div className="progressStateFeedback"><Spinner />Deleting...</div>
    } else if (this.state.unlinking) {
      return <div>Unlinking...</div>
    } else if (this.point){
      const point = this.point;
//      console.log("rendering " + point.url)
      let classesListedClaim = `listedClaim ${this.state.relevanceRater ? "relGroupHilite" : "relNotClicked"} ${this.evidenceTypeClass()=="support" ? "linkedClaim" : "rootClaim"}`
      let classesStackCardGroup = `stackCardGroup ${!this.editingSomething() && "stackCardGroupActive"} ${this.state.relevanceRater ? "relExtraMarginBottom" : "relNotClicked"}  ${this.state.editingComments && "commentsMarginBottom"}`
      let classesStackCard1 = `stackCard ${this.numSupportingPlusCounter() < 3 ? "stackCardHidden" : ""} ${this.linksRatio() <= 0.75 ? "counter" : ""} ${this.expanded() ? "stackCardDealBottom stackCardDealFade" : ""}`
      let classesStackCard2 = `stackCard ${this.numSupportingPlusCounter() < 2 ? "stackCardHidden" : ""} ${this.linksRatio() <= 0.50 ? "counter" : ""} ${this.expanded() ? "stackCardDealInvertXform stackCardDealFade" : ""}`
      let classesStackCard3 = `stackCard ${this.numSupportingPlusCounter() < 1 ? "stackCardHidden" : ""} ${this.linksRatio() <= 0.25 ? "counter" : ""} ${this.expanded() ? "stackCardDealInvertXform stackCardDealFade" : ""}`
      let classesPointCard = `point-card ${!this.editingSomething() && "pointCardActive"} stackCard ${this.expanded() ? "stackCardDealInvertXform" : ""} ${this.evidenceTypeClass()} row-fluid toggleChildVisOnHover`
      let classesRelevanceDot = `${this.props.parentPoint ? "cardBottomAction bottomActionDot" : "hidden" }`
      let classesRelevanceBottomLink = `${this.props.parentPoint ? "cardBottomAction relevanceVoteBottomAction" : "hidden" }`
      //console.log("linksRatio " + this.linksRatio() )

      //<div className="quickTestRect">Test rectangle!</div>

      return <div className={`listedClaimGroup ${this.props.latestQuickCreate && 'latestQuickCreate'}`}>
        <div className="listedClaimAndItsEvidence" ref={(input) => { this.cardToScrollTo = input; }}>
          <div className="relCtrlAndLinkAndStackCards">
            <div className={classesListedClaim} tabIndex="-1" >
              {this.relevanceCtrlUI()}
               <div className="relLinkAndStackCards">
                {this.relevanceLinkUI()}
                <div className={classesStackCardGroup} tabIndex="0" onClick={this.handleToggleEvidence} ref={(input) => { this.cardToFocusOn = input;}}>
                  <div className={classesStackCard1} tabIndex="-1">
                    <div className={classesStackCard2} tabIndex="-1">
                       <div className={classesStackCard3} tabIndex="-1">
                          <div className={classesPointCard} tabIndex="-1">
                            { this.state.editingClaimImage && <EditImage point={point} hasImage={this.hasImage()} onClose={this.handleCloseEditClaimImage}/> }
                            <div className="row-fluid inlineflexBox">
                            <div className={ this.textContentWidth()  }>
                                <div className="row-fluid">
                                  <div className="cardTopRow pointCardPaddingH span12">
                                    { this.hasBadge() &&
                                      <div className="fullWidth">
                                        <span className="claimBadge">
                                          <span className="claimBadgeIcon fas fa-star"></span><span className="claimBadgeLabel">{this.props.badge}</span>
                                        </span>
                                      </div> }
                                    <Byline point={point}/>
                                    <CommentsLink point={point} onClick={this.handleClickEditComments}/>
                                    { this.moreMenu() }
                                    <MediaQuery maxWidth={config.extraextraSmallScreenThreshold}>
                                      { this.expanded() && this.numSupportingPlusCounter() > 0 && this.shareMenu() }
                                    </MediaQuery>
                                  </div>
                                 </div>


                                 <div className="row-fluid">
                                  <div className="pointText span12">
                                    { this.pointTextComponent() }
                                  </div>
                                 </div>

                                 { !this.state.editingClaimSources ? this.sources() : <EditSources point={point} onCancel={this.handleCancelEditClaimSources}/> }

                                  <div className="row-fluid">
                                    <div className="cardBottomActionRow pointCardPaddingH" >
                                      <span><EvidenceLink point={point} expanded={this.props.expanded} expansionLoading={this.props.expansionLoading}
                                                        onSee={this.handleSeeEvidence} onHide={this.handleHideEvidence}
                                                        mouseOverPreload={this.preloadPoint}/>
                                      </span>
                                      <span className="cardBottomAction bottomActionDot">·</span>
                                      <span><AgreeDisagree point={point} parentPoint={this.props.parentPoint}/></span>
                                      <span className={classesRelevanceDot}>·</span>
                                      <a className={classesRelevanceBottomLink} onClick={this.handleRelClick}>Relevance</a>
                                    </div>
                                  </div>

                               </div>
                              {this.image()}
                            </div>
        { this.props.expansion.isExpanded(point, this.commentPrefix()) && <Comments point={point} onCancel={this.handleCloseComments}/> }
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <MediaQuery minWidth={config.extraextraSmallScreenThreshold}>
                { this.expanded() && this.numSupportingPlusCounter() > 0 && <ShareIconArea point={point}/> }
              </MediaQuery>
              <div className="evidenceRow row-fluid">
                {this.evidence()}
              </div>
            </div>
          </div>
    }
    else if (this.props.data && this.props.data.loading) {
      return <div>Loading...</div>
    }
    else {
      return <div>Something strange happened...</div>
    }
  }
}

export const PointCard = compose(
  withApollo,
  withExpandedIndexForPoint,
  graphql(schema.GetPoint, {
    skip: ({expanded}) => !expanded,
    props: ({ownProps, data: { loading, ...rest }}) => ({
      expansionLoading: loading,
      ...rest
    })

  }),
  graphql(schema.CurrentUserQuery, {
    name: 'CurrentUserQuery',
    props: ({ownProps, CurrentUserQuery: { loading, currentUser, refetch }}) => ({
      currentUserLoading: loading,
      currentUser: currentUser,
      refetchCurrentUser: refetch
    })
  }),
  graphql(schema.DeletePointMutation, {
    props: ({ mutate }) => ({
      delete: (url) => mutate({variables: {url},
                               refetchQueries: [{query: EditorsPicks}, {query: NewPoints, variables: {limit: config.newPointsPageSize}}]})
    })
  }),
  graphql(schema.MakeFeatured, {
    props: ({ mutate }) => ({
      makeFeatured: (id) => mutate({variables: {id},
                                   refetchQueries: [{query: schema.HomePage}]})
    })
  }),
  graphql(schema.SetEditorsPick, {
    props: ({ mutate }) => ({
      setEditorsPick: (id) => mutate({variables: {id},
                                     refetchQueries: [{query: EditorsPicks}]})
    })
  }),
  graphql(schema.UnlinkPointMutation, {
    props: ({ mutate }) => ({
      unlink: (parentURL, url, linkType) => mutate({variables: {parentURL, url, linkType},
                                                    refetchQueries: [{query: GetPoint, variables: {url: parentURL}}]})
    })
  })
)(PointCardComponent)
