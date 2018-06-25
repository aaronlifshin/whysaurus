import React from 'react';
import { graphql, compose, withApollo } from 'react-apollo';
import gql from 'graphql-tag';
import { Form, Text } from 'react-form';
import MediaQuery from 'react-responsive';
import { CSSTransitionGroup } from 'react-transition-group' // ES6
import AnimateOnChange from 'react-animate-on-change';
import { withAlert } from "react-alert";

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
import { CloseLinkX, timeAgoFormatter, timeAgoTitle } from './common'
import Spinner from './Spinner'
import { withExpandedIndexForPoint } from './ExpandedIndex'
import TimeAgo from 'react-timeago'

export const EvidenceType = Object.freeze({
    ROOT: Symbol("root"),
    SUPPORT:  Symbol("supporting"),
    COUNTER: Symbol("counter")
});


class Byline extends React.Component {

  handleClickNoProp = (e) => {
    e.stopPropagation();
  }

  contributorsPlusAuthor = () => {
    let contributorsPlusAuthor = this.props.point.numUsersContributed + 1
      return contributorsPlusAuthor;
  }
  
  contributorsToDisplayOnByline = () => {
    if (this.contributorsPlusAuthor() > 1)
      return this.contributorsPlusAuthor();
    else return "";
  }
  
  contributorsDropdown = () => {
    let contributorsTooltip = `${this.contributorsPlusAuthor()} Contributor${(this.contributorsPlusAuthor() > 1) ? "s" : ""}`
    return <span className="cardTopRowItem">
      <span className="dropdown">
          <a onClick={this.handleClickNoProp} className="easierToClickOn dropdown-toggle" title={contributorsTooltip} data-toggle="dropdown"><i className="far fa-user iconWithStat"></i><span className="number">{this.contributorsToDisplayOnByline()}</span></a>         
          <ul id="" className="contributorsMenu dropdown-menu dropdown-menu-with-caret" role="menu" aria-labelledby="dropdownMenu">
            <div className="dropdown-caret"><div className="caret-outer"></div><div className="caret-inner"></div></div>
            <li><span><span className="number">{this.contributorsPlusAuthor()}</span> Contributors</span></li>
          </ul>
        </span>
      </span>
  }
  
  timestampLastEdit = () => {
    let timestampTooltip = `Last Updated  ${timeAgoTitle(this.props.point.dateEdited)}`
    return <span className="cardTopRowItem easierToClickOn"><TimeAgo date={this.props.point.dateEdited + "Z"} title={timestampTooltip} minPeriod={300} formatter={timeAgoFormatter}/></span>
  }
  
  author = () => {
    return <span className="cardTopRowItem">By <a className="bylineAuthor" onClick={this.handleClickNoProp} target="_blank" tabIndex="-1" href={"/user/" + this.props.point.creatorURL}>@{this.props.point.creatorName}</a></span> 
  }

  // · 
  render(){
    return <span className="byline">
        {this.author()}{this.contributorsDropdown()}{this.timestampLastEdit()}
      </span>
  }
}

class ShareIconAreaComponent extends React.Component {
  postOnFacebook = (e) => {
    var url = this.props.point.url;
    var pointTitle = this.props.point.title;
    var dialogParams = {
        app_id: 144595249045851,
        method: 'feed',
        link: "https://www.whysaurus.com/claim/" + url,
        name: pointTitle,
        description: 'Debating on whysaurus: ' + pointTitle + ' \n Do you agree? Disagree? Got something to add to the debate?',
        display: 'popup'
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
        text = pointTitle.substring(0,114) + "..." + "https://www.whysaurus.com/claim/" + url;
    } else {
        text = pointTitle + " — here's why: https://www.whysaurus.com/claim/" + url;
    }
    var webUrl = "http://twitter.com/intent/tweet?text="+encodeURIComponent(text);
    window.open(webUrl,'_blank');
  }

  copyPointUrl = (e) => {
    e.preventDefault();
    var fullUrl = this.fullLinkUrl();

    navigator.clipboard.writeText(fullUrl).then(function() {
      console.log('Copied URL to clipboard: ' + fullUrl);
      //this.props.alert.show('Copied URL to clipboard: ' + fullUrl)
    }, function(err) {
      console.error('Couldnt copy URL to clipboard: ' + fullUrl, err);
      //this.props.alert.show('URL (unable to copy): ' + fullUrl)
    });

    //showAlert('Copied URL: ' + fullUrl);
    this.props.alert.show('Copied URL: ' + fullUrl);
  }

  fullLinkUrl = () => {
    var url = this.props.point.url;
    return "https://www.whysaurus.com/claim/" + url + "/";
  }

  render(){
    return <span className="shareIconArea">
       <a onClick={this.copyPointUrl} href={this.fullLinkUrl()}>
        <div className="claimShareIcon fas fa-link"></div>
       </a>
      <a onClick={this.postOnFacebook}>
        <div className="claimShareIcon fab fa-facebook-square"></div>
      </a>
      <a onClick={this.sharePointOnTwitter}>
        <div className="claimShareIcon fab fa-twitter"></div>
      </a>
      <a target="_blank" href={"mailto:?subject=Someone is wrong on the internet&body=Check out this argument on Whysaurus and add your voice!%0D%0A%0D%0A" + this.props.point.title + ". %0D%0Ahttps://www.whysaurus.com/claim/" + this.props.point.url + ""}>
        <div className="claimShareIcon far fa-envelope"></div>
      </a>
    </span>
  }
}

const ShareIconArea = compose(
  withAlert,
)(ShareIconAreaComponent)

function SupportingCount(props){
  return <span className="cardTopRowItem"><span className="iconWithStat"><span className="fas fa-level-up-alt"></span></span><span className="number">{props.point.supportedCount}</span> Other Links</span>
}

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
  handleToggleEvidence = (e) => {
    e.stopPropagation(); // prevents click from passing up to parent, which seems to break the functionality (even though they do the same thing)
    this.props.onClick && this.props.onClick()
  }

  titleUI = () => {
    return <span className="pointTitle">
      <a tabIndex="-1" onClick={this.handleToggleEvidence}>{this.props.point.title}</a>
    </span>
  }

  // TODO: make it not animate when card redraws
  render(){
    const score = this.props.point.pointValue
    return <div className="claimTextDisplay pointCardPaddingH pointCardPaddingHExtra">
      {this.titleUI()}
        <span className="scoreAnimContainerMax score">
          <span className="scoreAnimContainerReset">
            <Hover onHover={<VoteStats point={this.props.point}/>}>
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
            <span className="fas fa-book-open"></span>
          </span>
          <span className="sourceLabel">{name || url}</span>
        </a>
      )}
    </div>
  }
}


class CommentsLink extends React.Component {
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
          return <a className="cardBottomAction" onClick={this.handleClickHide}><MediaQuery minWidth={config.extraextraSmallScreenThreshold}>Hide </MediaQuery>Evidence</a>
        }
      } else {
        return <a className="cardBottomAction" onClick={this.handleClickSee} onMouseOver={this.props.mouseOverPreload}><MediaQuery minWidth={config.extraextraSmallScreenThreshold}>See </MediaQuery>Evidence</a>
      }
    } else {
      if (this.props.expanded) {
        return <a className="cardBottomAction" onClick={this.handleClickHide}>Hide Buttons</a>
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
  // move focus to the next point card, uses tabbable.js plugin
  focusOnNextCard = () => {
    setTimeout(function () { $.tabNext() } , 900)
  }

  handleClickAgree = (e) => {
    e.stopPropagation(); // prevents click from passing up to the parent, which would toggle expansion
    console.log("AgreeDisagreeComponent : agree");
    if (this.props.point.currentUserVote == 1) {
      ga('send', 'event', 'Vote', 'NeutralFromUp', this.props.point.url, 0);
    }
    else {
      ga('send', 'event', 'Vote', 'Up', this.props.point.url, 1);
    }
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

  handleClickDisagree = (e) => {
    e.stopPropagation(); // prevents click from passing up to the parent, which would toggle expansion
    console.log("AgreeDisagreeComponent : disagree");
    if (this.props.point.currentUserVote == -1) {
      ga('send', 'event', 'Vote', 'NeutralFromDown', this.props.point.url, 0);
    }
    else {
      ga('send', 'event', 'Vote', 'Down', this.props.point.url, -1);
    }
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

  agreeClass = () => "cardBottomAction agree" + (this.props.point.currentUserVote == 1 ? " current-vote" : "")

  disagreeClass = () => "cardBottomAction disagree" + (this.props.point.currentUserVote == -1 ? " current-vote" : "")

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
  state = {
    relevanceRater: false,
    displayImageBig: false // is declaring this up here needed/best practice? -JF
  }
  handleClickNoProp = (e) => {
    e.stopPropagation();
  }

  handleClickEditClaimText = (e) => {
    e.stopPropagation();
    if (this.props.currentUser){
      this.setState({editingClaimText: true})
    } else {
      console.log('Logon Required')
      $("#loginDialog").modal("show");
      ga('send', 'event', 'Required login ',  'Require login add source')
    }
  }

  handleClickEditClaimSources = (e) => {
    e.stopPropagation();
    if (this.props.currentUser){
      this.setState({editingClaimSources: true})
    } else {
      console.log('Logon Required')
      $("#loginDialog").modal("show");
    }
  }

  handleClickEditClaimImage = (e) => {
    e.stopPropagation();
    if (this.props.currentUser){
      this.setState({editingClaimImage: true})
    } else {
      console.log('Logon Required')
      $("#loginDialog").modal("show");
      ga('send', 'event', 'Required login ',  'Require login add image')
    }
  }

  showComments = () => this.props.expansion.expand(this.point, this.commentPrefix())

  hideComments = () => this.props.expansion.collapse(this.point, this.commentPrefix())

  handleClickEditComments = (e) => {
    e.stopPropagation();
    const expansion = this.props.expansion
    if (expansion.isExpanded(this.point, this.commentPrefix())) {
      this.hideComments()
      ga('send', 'event', 'Comment', 'Hide Comments', this.point.url);
    }
    else {
      this.showComments()
      ga('send', 'event', 'Comment', 'Show Comments', this.point.url);
    }
  }

  handleCancelEditClaimText = (e) => {
    e.stopPropagation()
    this.setState({editingClaimText: false})
  }
  handleCancelEditClaimSources = (e) => {
    e.stopPropagation()
    this.setState({editingClaimSources: false})
  }
  handleCloseEditClaimImage = (e) => {
    e && e.stopPropagation()
    this.setState({editingClaimImage: false})
  }
  handleCloseComments = (e) => {
    e && e.stopPropagation()
    this.hideComments()
    ga('send', 'event', 'Comment', 'Hide Comments', this.point.url);
  }

  editingSomething = () => {
    return (this.state.editingClaimText || this.state.editingClaimSources || this.state.editingClaimImage || this.state.editingComments)
  }

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

  get relevance() {
    return this.props.link && this.props.link.relevance
  }

  get sortScore() {
    return this.props.link && this.props.link.sortScore
  }

  get relevanceVoteCount() {
    return this.props.link && this.props.link.voteCount
  }

  // TODO: the "root" case doesn't seem to be working -JF
  evidenceTypeClass = () => {
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

  // toggle Relevance Rater
  handleRelClick = (e) => {
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

  relevanceCtrlUI = () => {
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
  relevanceLinkUI = () => {
    if (this.props.parentPoint) {
      let classesRelevanceLink = `relevanceLink ${this.evidenceTypeClass()}`
      let classesDottedLine = `${this.evidenceTypeClass()} dottedLine dottedLineRelevanceLink`
      return <a className={classesRelevanceLink} onClick={this.handleRelClick}>
        <div className="relevanceLinkArea">
          <div className={classesDottedLine}></div>
          <span className="relevanceDisplay number"><span className="positionRelDisplay">{this.relevance}<span className="perctSignSmallRelLink">%</span></span></span>
          <LinkedItemBullet />
        </div>
      </a>
    } else {
      return null
    }
  }

  expand = () => {
    this.props.onExpand()
  }

  collapse = () => {
    this.props.onCollapse()
  }

  handleSeeEvidence = () => {
    this.expand();
  }

  handleHideEvidence = () => {
    this.collapse();
  }

  // When user clicks on the pointTitle or the stackGroup
  // Disabled when the claim is being edited
  handleToggleEvidence = () => {
    if (!this.editingSomething()) {
      if (this.expanded()) {
        this.collapse()
      } else {
        this.expand()
      }
    }
  }

  expanded = () => {
    return this.props.expanded && !this.props.expansionLoading;
  }
  
  // bigImage
  handleImageClick = (e) => {
    e.stopPropagation();
    if (this.state.displayImageBig) {
      this.setState({ displayImageBig: false })
    } else {
      this.setState({ displayImageBig: true })
    }
  }
  // TODO old django pointBox.html also checks if point.imageURL.strip exists - is that necessary here? -JF
  hasImage = () => {
    //console.log("hasImage() : " + this.point.imageURL  )
    return this.point.imageURL
  }
  displayImage = () => {
    return (this.hasImage() && !this.state.editingClaimText && !this.state.editingClaimSources)
  }
  image = () => {
    if (this.displayImage()) {
      let classesImageContainer = `imageContainer hideBorderBottom ${this.state.displayImageBig && !this.state.editingClaimImage && "imageContainerBig"}`
      let classesImage = `claimImage ${this.state.editingClaimImage && "imageFaded"}`
      let classesImageCaption = `${this.state.displayImageBig ? "imageCaption" : "hidden"}`      
      return  <div className={classesImageContainer}>
          <a onClick={this.handleImageClick}><img className={classesImage} src={this.point.fullPointImage} alt={this.point.imageDescription}></img></a>
          <span className={classesImageCaption}>{this.point.imageDescription}</span>
        </div>
    }
  }
  textContentWidth = () => {
    if (this.displayImage() && (!this.state.displayImageBig || this.state.editingClaimImage) ) {
      return "contentWithImage"
    } else {
      return "contentNoImage"
    }
  }

  // TODO: this is declared as a local function in two different componants - should it be a global fuction or a const? -JF
  numSupportingPlusCounter = () => {
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

  currentUserIsAdmin = () => (
    this.props.currentUser && this.props.currentUser.admin
  )

  hasParent = () => (this.props.parentPoint)

  hasBadge = () => (this.props.badge)
  
  evidence = () => {
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
          { !this.hasParent() && <div className="moreClaimsDivision"></div> }
        </div>
      }
    }
  }

  renderDottedLinesEvidenceHeaderOrMargin = () => {
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

  commentPrefix = () => this.prefix() + 'comments-'

  supportingPoints = () => {
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

  counterPoints = () => {
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
  relevantPoints = () => {
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
  linksRatio = () => {
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
  sources = () => {
    if (this.point.sources){
      return <div className="row-fluid">
          <Sources point={this.point}/>
        </div>
    }
  }

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
  //      <a onClick={this.handleClickNoProp} className="moreMenuLink easierToClickOn dropdown-toggle"  data-toggle="dropdown">&#9776;</a>
  moreMenu = () => {
    let moreMenuSourcesLabel = `${this.point.sources ? "Edit Sources" : "Add Sources"}`
    let moreMenuImageLabel = `${this.hasImage() ? "Edit Image" : "Add Image"}`
    return <span className="cardTopRowItem dropdown">
      <a onClick={this.handleClickNoProp} className="moreMenuLink easierToClickOn dropdown-toggle"  data-toggle="dropdown"><span className="fas fa-ellipsis-h"></span></a>
      <ul id="" className="moreMenu dropdown-menu dropdown-menu-with-caret" role="menu" aria-labelledby="dropdownMenu">
        <div className="dropdown-caret"><div className="caret-outer"></div><div className="caret-inner"></div></div>
        <li><a onClick={this.handleClickEditClaimText} className="" ><span className="iconWithStat"><span className="fas fa-pencil-alt"></span></span>Edit Claim</a></li>
        <li><a onClick={this.handleClickEditClaimSources} className="" ><span className="iconWithStat"><span className="fas fa-book-open"></span></span>{moreMenuSourcesLabel}</a></li>
        <li><a onClick={this.handleClickEditClaimImage} className="" ><span className="iconWithStat"><span className="far fa-image"></span></span>{moreMenuImageLabel}</a></li>
        <li className="divider"></li>
        { this.hasParent() && <li><a onClick={this.handleClickUnlink}><span className="iconWithStat"><span className="fa fa-unlink"></span></span>Unlink</a></li>  }
        <li><a onClick={this.handleClickNoProp} target="_blank" href={"/history/" + this.point.url}><span className="iconWithStat"><span className="fas fa-history"></span></span>History</a></li>
        <li><a onClick={this.handleClickNoProp} target="_blank" href={"/claim/" + this.point.url}><span className="iconWithStat"><span className="fas fa-external-link-alt"></span></span>Open in new tab</a></li>
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

  shareMenu = () => {
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

 pointTextComponent = () => {
    const point = this.point;
    if (this.state.editingClaimText){
      return <EditPoint point={point} onCancel={this.handleCancelEditClaimText}/>
    } else {
      return <Point point={point} onClick={this.handleToggleEvidence}/>
    }
  }

  
  relevanceBottomLinkLabel = () => {
    return <span>
      <MediaQuery maxWidth={config.extraextraSmallScreenThreshold - 1 }>
        Relv
      </MediaQuery>
      <MediaQuery minWidth={config.extraextraSmallScreenThreshold}>
        Relevance
      </MediaQuery>       
      </span>
  }                                                                     
  
  preloadPoint = () => {
    console.log("preloading data for " + this.point.url)
    this.props.client && this.props.client.query({
      query: GetPoint,
      variables: {url: this.point.url}
    })
  }
  
  // Is there a crafty way to do this with concatenation?
  stackMarginBottomClass = () => {
    if (this.numSupportingPlusCounter() == 0)
      return "stackMarginBottom0"
    else if (this.numSupportingPlusCounter() == 1)
      return "stackMarginBottom1"  
    else if (this.numSupportingPlusCounter() == 2)
      return "stackMarginBottom2"
    else return "stackMarginBottom3"
  }  

  render(){
    if (this.state.deleting) {
      return <div className="progressStateFeedback"><Spinner />Deleting...</div>
    } else if (this.state.unlinking) {
      return <div>Unlinking...</div>
    } else if (this.point){
      const point = this.point;
      let classesListedClaimGroup = `listedClaimGroup ${this.props.latestQuickCreate && 'latestQuickCreate'} ${!this.props.parentPoint && this.stackMarginBottomClass() }`
      let classesListedClaim = `listedClaim ${this.state.relevanceRater ? "relGroupHilite" : "relNotClicked"} ${this.evidenceTypeClass()=="support" ? "linkedClaim" : "rootClaim"}`
      let classesStackCardGroup = `stackCardGroup ${!this.editingSomething() && "stackCardGroupActive"} ${this.state.relevanceRater ? "relExtraMarginBottom" : "relNotClicked"}`
      let classesStackCard1 = `stackCard ${this.numSupportingPlusCounter() < 3 ? "stackCardHidden" : ""} ${this.linksRatio() <= 0.75 ? "counter" : ""} ${this.expanded() ? "stackCardDealBottom stackCardDealFade" : ""}`
      let classesStackCard2 = `stackCard ${this.numSupportingPlusCounter() < 2 ? "stackCardHidden" : ""} ${this.linksRatio() <= 0.50 ? "counter" : ""} ${this.expanded() ? "stackCardDealInvertXform stackCardDealFade" : ""}`
      let classesStackCard3 = `stackCard ${this.numSupportingPlusCounter() < 1 ? "stackCardHidden" : ""} ${this.linksRatio() <= 0.25 ? "counter" : ""} ${this.expanded() ? "stackCardDealInvertXform stackCardDealFade" : ""}`
      let classesPointCard = `point-card ${!this.editingSomething() && "pointCardActive"} stackCard ${this.expanded() ? "stackCardDealInvertXform" : ""} ${this.evidenceTypeClass()} ${this.state.editingClaimImage && "hideBorderTop"} ${this.props.expansion.isExpanded(point, this.commentPrefix()) && "hideBorderBottom"}  row-fluid toggleChildVisOnHover`
      let classesRelevanceDot = `${this.props.parentPoint ? "cardBottomAction bottomActionDot" : "hidden" }`
      let classesRelevanceBottomLink = `${this.props.parentPoint ? "cardBottomAction relevanceVoteBottomAction" : "hidden" }`

      return <div className={classesListedClaimGroup}>
        <div className="listedClaimAndItsEvidence" ref={(input) => { this.cardToScrollTo = input; }}>
          { this.state.editingClaimImage && <EditImage point={point} parentPoint={this.props.parentPoint} hasImage={this.hasImage()} onClose={this.handleCloseEditClaimImage}/> }
          <div className="listedClaimAndShare">
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
                              {this.image()}
                              <div className="row-fluid inlineflexBox">
                              <div className={ this.textContentWidth()  }>
                                  <div className="row-fluid">
                                    <div className="cardTopRow pointCardPaddingH">
                                      { this.hasBadge() &&
                                        <div className="fullWidth">
                                          <span className="claimBadge">
                                            <span className="claimBadgeIcon fas fa-star"></span><span className="claimBadgeLabel">{this.props.badge}</span>
                                          </span>
                                        </div> }
                                      <Byline point={point}/>
                                      <CommentsLink point={point} onClick={this.handleClickEditComments}/>
                                      { this.moreMenu() }
                                      <MediaQuery maxWidth={config.extraextraSmallScreenThreshold - 1 }>
                                        { this.expanded() && this.numSupportingPlusCounter() > 0 && this.shareMenu() }
                                      </MediaQuery>
                                    </div>
                                   </div>
                                   
                                   <div className="row-fluid">
                                    <div className="pointText">
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
                                        <a className={classesRelevanceBottomLink} onClick={this.handleRelClick}>{this.relevanceBottomLinkLabel()}</a>
                                      </div>
                                    </div>

                                 </div>
                                
                              </div>                             
                              </div>                           
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <MediaQuery minWidth={config.extraextraSmallScreenThreshold}>
                  { this.expanded() && !this.state.relevanceRater && <ShareIconArea point={point} /> }
                </MediaQuery>
              </div>
              { this.props.expansion.isExpanded(point, this.commentPrefix()) && <Comments point={point} parentPoint={this.props.parentPoint} onCancel={this.handleCloseComments}/> }
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