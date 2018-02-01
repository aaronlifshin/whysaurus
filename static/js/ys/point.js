import React from 'react';
import ReactDOM from 'react-dom';
import { graphql, compose } from 'react-apollo';
import gql from 'graphql-tag';
import { Form, Text } from 'react-form';
import MediaQuery from 'react-responsive';

import AnimateOnChange from 'react-animate-on-change';

const CurrentUserQuery = gql`
query CurrentUser {
  currentUser { url }
}`

export const pointFieldsFragment = gql`
fragment pointFields on Point {
  id,
  url,
  title,
  authorName,
  authorURL,
  imageURL,
  fullPointImage,
  upVotes,
  downVotes,
  pointValue,
  numSupporting,
  numCounter,
  numComments,
  supportedCount,
  sources {url, name},
  rootURLsafe,
  currentUserVote
}
`
export const evidenceEdgesFragment = gql`
fragment evidenceEdges on SubPointConnection {
  edges { node { title, upVotes, ...pointFields }, link { id, type, relevance, relevanceVote, parentURLsafe, childURLsafe }}
}`


export const expandedPointFieldsFragment = gql`
${pointFieldsFragment}
${evidenceEdgesFragment}
fragment evidenceFields on Point {
 supportingPoints { ...evidenceEdges },
 counterPoints { ...evidenceEdges },
 relevantPoints { ...evidenceEdges }
}`

export const EvidenceType = Object.freeze({
    ROOT: Symbol("root"),
    SUPPORT:  Symbol("supporting"),
    COUNTER: Symbol("counter")
});

function Byline(props){
  return <span className="cardTopRowItem"><span>By </span><a className="byline" target="_blank" tabIndex="-1" href={"/user/" + props.point.authorURL}>@{props.point.authorName}</a></span>
}

// TODO: should we localize these icons instead of relying on fontawesome (the fa class)? -JF
function CommentCount(props){
  return <span className="cardTopRowItem"><span className="iconWithStat fa fa-comment-o"></span>{props.point.numComments}</span>
}
function ShareIcon(props){
  return <span className="cardTopRowItem"><span className="fa fa-share-alt"></span></span>
}
function SupportingCount(props){
  return <span className="cardTopRowItem"><span className="iconWithStat fa fa-level-up"></span>{props.point.supportedCount}</span>
}

/*
        Code to check if current user is the point Author
          {this.props.data.currentUser &&
          this.props.data.currentUser.url == this.point.authorURL &&
          <a onClick={this.handleClickEdit} className="editLink" >Edit</a>}
*/


// thanks, https://stackoverflow.com/questions/29981236/how-do-you-hover-in-reactjs-onmouseleave-not-registered-during-fast-hover-ove
const Hover = ({ onHover, children }) => (
    <span className="hover bringToFront">
      <span className="hover__no-hover">{children}</span>
      <span className="hover__hover">{onHover}</span>
    </span>
)

const VoteStats = ({point}) => (
    <div className="vote-stats">
      <p>
        {point.upVotes} Agrees<br/>
        {point.downVotes} Disagrees<br/>
      </p>
      <div className="menuDivider"></div>
      <p>
        {point.numSupporting} Supporting Claim{point.numSupporting != 1 ? "s" : null}<br/>
        {point.numCounter} Counter Claim{point.numCounter != 1 ? "s" : null}<br/>
      </p>
    </div>
)

export const EditPointQuery = gql`
mutation EditPoint($url: String!, $title: String) {
  editPoint(pointData: {url: $url, title: $title}) {
    point {
      id,
      title,
      url
    }
  }
}
`

const EditTitleForm = ( props ) => {
  return (
      <Form onSubmit={props.onSubmit}>
      { formApi => (
          <form onSubmit={formApi.submitForm} id="form1" className="editPointTextForm">
          <Text field="title" id="editPointTextField" />
          <button type="submit">Save</button>
          </form>
      )}
    </Form>
  );
}

class EditPointComponent extends React.Component {
  constructor(props) {
    super(props)
    this.state = {saving: false}
    this.handleClickSave = this.handleClickSave.bind(this);
  }

  get point() {
    return this.props.point;
  }

  handleClickSave(values, e, formApi) {
    values.url = this.point.url
    this.setState({saving: true})
    this.props.mutate({
      variables: values
    })
    // this component will be replaced after save, so we don't need to update state
  }

  titleUI() {
    if (this.state.saving) {
      return <span>Saving...</span>
    } else {
      return <span>
        <EditTitleForm onSubmit={this.handleClickSave}/>
      </span>
    }
  }

  render(){
    const score = this.point.pointValue
    return <div>
      {this.titleUI()}
	  <button  onClick={this.props.onCancel} type="cancel" className="cancelButton">Cancel</button>
    </div>
  }
}

const EditPoint = compose(
  graphql(EditPointQuery),
)(EditPointComponent)

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

  // To turn animation off change the logic in this line: animate={score == prevScore}
  // TODO: set prevScore correctly, somehow
  render(){
    const score = this.point.pointValue
	const prevScore = this.point.pointValue
    return <div>
      {this.titleUI()}
    <span className="scoreAnimContainerMax">
    <span className="scoreAnimContainerReset">
      <Hover onHover={<VoteStats point={this.point}/>}>
       <span className="ux2ScoreInLine"><span className={score < 0 ? "negativeScore": "positiveScore"}><AnimateOnChange baseClassName="scorePreAnimate" animationClassName="Score--bounce" animate={score == prevScore}>{score > 0 && "+"}{score}</AnimateOnChange></span></span>
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
  constructor(props) {
    super(props)
    this.state = {editing: false}
    this.handleClickEdit = this.handleClickEdit.bind(this);
    this.handleClickSave = this.handleClickSave.bind(this);
  }

  get point() {
    return this.props.point;
  }

  handleClickEdit(e) {
    // TODO: not working, make work
    console.log("edit");
    this.setState({editing: true})
  }

  handleClickSave(values, e, formApi) {
    // TODO: not working, make work
    console.log("saving edits")
    values.url = this.point.url
    this.props.mutate({
      variables: values
    })
      .then( res => {
        console.log(res)
      });
    this.setState({editing: false})
  }

  render(){
    return <div className="sources">
      {this.point.sources && this.point.sources.map(({name, url}, i) =>
        <div key={i} className="source"><img className="iconSourcesSmall" src="/static/img/sourcesIconSmall_grey.png"/><a tabIndex="-1" target="_blank" href={url}>{name}</a></div>
      )}
    </div>
  }
}

class EvidenceLink extends React.Component {
  constructor(props) {
    super(props)
    this.handleClickSee = this.handleClickSee.bind(this);
    this.handleClickHide = this.handleClickHide.bind(this);
    this.handleClickToggle = this.handleClickToggle.bind(this);
  }

  get point() {
    return this.props.point;
  }

  hasEvidence() {
    return this.point.numSupporting > 0 || this.point.numCounter > 0;
  }

  // TODO: can this be replaced by handleClickToggle? -JF
  handleClickSee(e) {
	e.stopPropagation(); // prevents click from passing up to parent, which seems to break the functionality (even though they do the same thing)
    console.log("EvidenceLink : handleClickSee");
    this.props.onSee && this.props.onSee()
  }

  // TODO: can this be replaced by handleClickToggle? -JF
  handleClickHide(e) {
	e.stopPropagation(); // prevents click from passing up to parent, which seems to break the functionality (even though they do the same thing)
	console.log("EvidenceLink: handleClickHide");
    this.props.onHide && this.props.onHide()
  }

  handleClickToggle(e) {
	e.stopPropagation(); // prevents click from passing up to parent, which seems to break the functionality (even though they do the same thing)
	console.log("EvidenceLink : handleClickToggle");
    this.props.onToggle && this.props.onToggle()
  }

  whichEvidenceButton() {
    if (this.hasEvidence()) {
      if (this.props.expanded) {
        return <a className="cardBottomAction hideEvidence" onClick={this.handleClickHide}>Hide Evidence</a>
      } else {
        return <a className="cardBottomAction seeEvidence" onClick={this.handleClickSee}>See Evidence</a>
      }
    } else {
      return <a className="cardBottomAction" onClick={this.handleClickToggle}>Add Evidence</a>
    }
  }

  render(){
  return <span className="evidenceContainer">{this.whichEvidenceButton()}</span>
  }
}

// TODO: make cancel button work
// TODO: if we are adding a counter point, then add class .buttonUX2Red to the submit button
const AddEvidenceForm = ( props ) => {
  return (
    <div className="addEvidenceFormGroup">
    <div className="arrowAddEvidenceForm">&#x21B3;</div>
      <Form onSubmit={props.onSubmit}>
      { formApi => (
          <form onSubmit={formApi.submitForm} id="form1" className="addEvidenceForm">
          <Text field="title" id="title" className="addEvidenceFormTextField" placeholder='Make a claim, eg "Dogs can learn more tricks than cats."' />
          <button type="submit" className="buttonUX2 addEvidenceFormButton">Add</button>
		  <button type="cancel" className="cancelButton">Cancel</button>
          </form>
      )}
    </Form>
  </div>
  );
}

class AddEvidenceCard extends React.Component {
  constructor(props) {
    super(props)
    this.state = {adding: false}
    this.handleClickAddEvidence = this.handleClickAddEvidence.bind(this)
    this.handleClickSave = this.handleClickSave.bind(this)
  }

  get point() {
    return this.props.point;
  }

  handleClickAddEvidence(e) {
    console.log("add evidence")
    if (this.props.data.currentUser){
      this.setState({adding: true})
    } else {
      $("#loginDialog").modal("show");
    }
  }

  handleClickSave(values, e, formApi) {
    console.log("saving evidence")
    let parentURL = this.point.url
    values.parentURL = parentURL
    values.linkType = this.linkType
    this.setState({saving: true})
    this.props.mutate({
      variables: values,
      update: (proxy, { data: { addEvidence: { newEdges } }}) => {
        const data = proxy.readQuery({ query: GetPoint, variables: {url: parentURL} })
        data.point.relevantPoints.edges = data.point.relevantPoints.edges.concat(newEdges.edges)
        if (this.linkType == 'counter') {
          data.point.counterPoints.edges = data.point.counterPoints.edges.concat(newEdges.edges)
        } else {
          data.point.supportingPoints.edges = data.point.supportingPoints.edges.concat(newEdges.edges)
        }
        proxy.writeQuery({ query: GetPoint,
                           variables: {url: parentURL},
                           data: data });
      }
    })
      .then( res => {
        this.setState({saving: false,
                       adding: false})
        console.log(res)
      });
  }

  get evidenceType(){
    return this.props.type
  }

  get linkType(){
    switch (this.evidenceType) {
      case EvidenceType.SUPPORT:
        return "supporting"
      case EvidenceType.COUNTER:
        return "counter"
      default:
        return null
    }
  }

  get addText(){
    switch (this.evidenceType){
      case EvidenceType.ROOT:
        return "Add Evidence"
      case EvidenceType.SUPPORT:
        return "Add Evidence For"
      case EvidenceType.COUNTER:
        return "Add Evidence Against";
      default:
        return "Add Evidence"
    }
  }

  // TODO: this is declared as a local function in two different componants - should it be a global fuction or a const? -JF
  numSupportingPlusCounter(){
    return ( this.point.numSupporting + this.point.numCounter)
  }

  render(){
    if (this.state.adding) {
      if (this.state.saving) {
        return <div>
          Saving...
          </div>
      } else {
        return <div>
          <AddEvidenceForm onSubmit={this.handleClickSave}/>
          </div>
      }
    } else {
    let classesButtonGrp = `addEvidenceButtonGrp ${this.linkType=="counter" ? "addEvidenceButtonGrpCounter" : "" }`
    let classesLine = `dottedLine dottedLineAddEvidenceButton ${this.linkType=="counter" ? "dottedLineAddCounter" : "dottedLineAddSupport" }  ${this.numSupportingPlusCounter() < 1 ? "dottedLineNoEvidence" : "" }`
    let classesButton = `buttonUX2 ${this.linkType=="counter" ? "buttonUX2Red" : ""} addEvidenceButton`
	let nameButton = `${this.linkType=="counter" ? "addCounterEvidenceButton" : "addSupportingEvidenceButton" }`
	  return <a onClick={this.handleClickAddEvidence}>
        <div className={classesButtonGrp}>
          <div className={classesLine}></div>
          <div className="arrowAddEvidenceButton">&#x21B3;</div>
          <button type="button" name={nameButton} tabIndex="0" className={classesButton}>{this.addText}</button>
        </div>
         </a>
    }
  }
}

export const AddEvidenceQuery = gql`
${pointFieldsFragment}
${evidenceEdgesFragment}
mutation AddEvidence($title: String!, $linkType: String, $parentURL: String, $imageURL: String, $imageAuthor: String, $imageDescription: String, $sourceURLs: [String], $sourceNames: [String]) {
  addEvidence(pointData: {title: $title, content: $title, summaryText: $title, imageURL: $imageURL, imageAuthor: $imageAuthor, imageDescription: $imageDescription, sourceURLs: $sourceURLs, sourceNames: $sourceNames, linkType: $linkType, parentURL: $parentURL}) {
    newEdges { ...evidenceEdges }
    parent { id, numSupporting, numCounter } 
  }
}
`

const AddEvidence = compose(
  graphql(AddEvidenceQuery),
  graphql(CurrentUserQuery),
)(AddEvidenceCard)

export const VoteQuery = gql`
mutation Vote($url: String!, $vote: Int!, $parentURL: String) {
  vote(url: $url, vote: $vote, parentURL: $parentURL) {
    point {
      id
      pointValue
      upVotes
      downVotes
      currentUserVote
    }
    parentPoint {
      id
      pointValue
    }
  }
}
`

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


export const RelevanceVoteQuery = gql`
mutation RelevanceVote($linkType: String!, $parentRootURLsafe: String!, $rootURLsafe: String!, $url: String!, $vote: Int!) {
  relevanceVote(linkType: $linkType, rootURLsafe: $rootURLsafe, parentRootURLsafe: $parentRootURLsafe, url: $url, vote: $vote) {
    point {
      id
    }

    link {
      id,
      type,
      relevance,
      relevanceVote,
      parentURLsafe,
      childURLsafe
    }
  }
}
`

class RelevanceComponent extends React.Component {
  constructor(props) {
    super(props);
    // This binding is necessary to make `this` work in the callback
    this.handleClick0 = this.handleClick0.bind(this);
    this.handleClick33 = this.handleClick33.bind(this);
    this.handleClick66 = this.handleClick66.bind(this);
    this.handleClick100 = this.handleClick100.bind(this);
  }

  get rootURLsafe() {
    return this.props.point.rootURLsafe
  }

  get parentRootURLsafe() {
    return this.props.parentPoint.rootURLsafe
  }

  get linkType(){
    switch (this.props.linkType) {
      case EvidenceType.SUPPORT:
        return "supporting"
      case EvidenceType.COUNTER:
        return "counter"
      default:
        return null
    }
  }

  handleClick0() {
    console.log("0");
    if (this.props.data.currentUser){
      this.props.mutate({
        variables: {linkType: this.linkType, url: this.props.point.url, parentRootURLsafe: this.parentRootURLsafe, rootURLsafe: this.rootURLsafe, vote: 0}
      }).then( res => {
        console.log(res)
      });
    } else {
      $("#loginDialog").modal("show");
    }
  }

  handleClick33() {
    console.log("33");
    if (this.props.data.currentUser){
      this.props.mutate({
        variables: {linkType: this.linkType, url: this.props.point.url, parentRootURLsafe: this.parentRootURLsafe, rootURLsafe: this.rootURLsafe, vote: 33}
      }).then( res => {
        console.log(res)
      });
    } else {
      $("#loginDialog").modal("show");
    }
  }

  handleClick66() {
    console.log("66");
    if (this.props.data.currentUser){
      this.props.mutate({
        variables: {linkType: this.linkType, url: this.props.point.url, parentRootURLsafe: this.parentRootURLsafe, rootURLsafe: this.rootURLsafe, vote: 66}
      }).then( res => {
        console.log(res)
      });
    } else {
      $("#loginDialog").modal("show");
    }
  }

  handleClick100() {
    console.log("100");
    if (this.props.data.currentUser){

      this.props.mutate({
        variables: {linkType: this.linkType, url: this.props.point.url, parentRootURLsafe: this.parentRootURLsafe, rootURLsafe: this.rootURLsafe, vote: 100}
      }).then( res => {
        console.log(res)
      });
    } else {
      $("#loginDialog").modal("show");
    }
  }

  linkClassFor(vote){
	let myVoteClass = "myRelevanceVoteLow"
	if (vote > 50)
		myVoteClass = "myRelevanceVoteHigh"
    return (this.props.link.relevanceVote == vote) ? ("relVoteLink " +myVoteClass) : "relVoteLink"
  }
  
  // TODO: reflect the user's current vote;
  //   if it is 100% or 66%, add the class add class .myRelevanceVoteHigh
  //   if it is 33% or 0%, add the class add class .myRelevanceVoteLow
  render(){
    return <div className="relCtrlGroup" >
      <div className="relCtrlLabel">How Relevant is this claim {this.props.link.relevanceVote}?</div>
      <div className="relCtrlVoteOptions">
      <a className={this.linkClassFor(100)} onClick={this.handleClick100}>100<span className="perctSignSmall">%</span></a>
      <a className={this.linkClassFor(66)} onClick={this.handleClick66}>66<span className="perctSignSmall">%</span></a>
      <a className={this.linkClassFor(33)} onClick={this.handleClick33}><span className="numbersFixVertAlign">33</span><span className="perctSignSmall">%</span></a>
      <a className={this.linkClassFor(0)} onClick={this.handleClick0}>0<span className="perctSignSmall">%</span></a>
    </div>
      </div>
    }
}

const RelevanceVote = compose(
  graphql(RelevanceVoteQuery),
  graphql(CurrentUserQuery),
)(RelevanceComponent)


class PointCard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
    expandedIndex: {},
    relLinkClicked: false
  }
    this.handleCancelEdit = this.handleCancelEdit.bind(this);
    this.handleSeeEvidence = this.handleSeeEvidence.bind(this);
    this.handleHideEvidence = this.handleHideEvidence.bind(this);
    this.handleToggleEvidence = this.handleToggleEvidence.bind(this);
    this.handleToggleEvidenceFromCard = this.handleToggleEvidenceFromCard.bind(this);
    this.renderSubPointCard = this.renderSubPointCard.bind(this);
    this.handleRelClick = this.handleRelClick.bind(this);
    this.handleClickEdit = this.handleClickEdit.bind(this);
    this.handleClickMore = this.handleClickMore.bind(this);
	this.handleClickNoProp = this.handleClickNoProp.bind(this);
  }

  handleClickNoProp(e) {
	e.stopPropagation();	  
  }
  
  handleClickEdit(e) {
	e.stopPropagation();	  
    this.setState({editing: true})
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
    return this.props.data.point ? this.props.data.point : this.props.point
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

  handleRelClick(e) {
    //console.log("toggle relevance ui");
    if (this.state.relLinkClicked) {
      this.setState({ relLinkClicked: false })
    } else {
      this.setState({ relLinkClicked: true })
    }
  }

  relevanceCtrlUI() {
    if (this.props.parentPoint) {
      return <span>
        { this.state.relLinkClicked ?
            <div className="relevanceCtrlArea">
              <RelevanceVote point={this.point} parentPoint={this.props.parentPoint} link={this.props.link} linkType={this.evidenceType}/>
            </div> :
            <span className="noRelevanceCtrl"></span>
        }
      </span>
    } else {
      return null
    }
  }

  // TODO: rebuild arrow using css in order to control stroke width, instead of unicode &#x21B3;
  relevanceLinkUI() {
    if (this.props.parentPoint) {
    let classesRelevanceLink = `relevanceLink ${this.evidenceTypeClass()}`
    return <a className={classesRelevanceLink} onClick={this.handleRelClick}>
      <div className="relevanceLinkArea">
        <div className="dottedLine dottedLineRelevanceLink"></div>
        <span className="relevanceDisplay">{this.relevance}%</span>
        <div className="arrowCard">&#x21B3;</div>
        { this.state.buttonClicked ?
            <RelevanceVote point={this.point} parentPoint={this.props.parentPoint} linkType={this.evidenceType}/> :
            <span></span>
        }
      </div></a>
    } else {
      return null
    }
  }

  handleCancelEdit(e) {
    e.stopPropagation()
    this.setState({editing: false})
  }

  handleSeeEvidence(point=this.point) {
    const i = this.state.expandedIndex
    i[point.id] = true
    this.setState({expandedIndex: i})
    this.props.handleSeeEvidence && this.props.handleSeeEvidence(point);
  }

  handleHideEvidence(point=this.point) {
    const i = this.state.expandedIndex
    i[point.id] = false
    this.setState({expandedIndex: i})
    this.props.handleHideEvidence && this.props.handleHideEvidence(point);
  }

  // When user clicks on the pointTitle or "Add Evidence"
  handleToggleEvidence(point=this.point) {
    const i = this.state.expandedIndex
    console.log("pointCard : handleToggleEvidence : point.url : " + point.url)
    if (this.expanded()) {
      console.log("pointCard : handleToggleEvidence : EXPANDED ")
      i[point.id] = false
      this.setState({expandedIndex: i})
    } else {
      console.log("pointCard : handleToggleEvidence : NOT EXPANDED ")
      i[point.id] = true
      this.setState({expandedIndex: i})
    }
  }
  
  // When user clicks on the cardstack (but not on any particular link)
  // TODO: can/should these two toggle functions be consolidated?
  handleToggleEvidenceFromCard() {
    const i = this.state.expandedIndex
    console.log("pointCard : handleToggleEvidenceFromCard : point.url : " + this.point.url)
    if (this.expanded()) {
      console.log("pointCard : handleToggleEvidenceFromCard : EXPANDED ")
      i[this.point.id] = false
      this.setState({expandedIndex: i})
    } else {
      console.log("pointCard : handleToggleEvidenceFromCard : NOT EXPANDED ")
      i[this.point.id] = true
      this.setState({expandedIndex: i})
    }
  }
 
  expanded() {
    return this.state.expandedIndex[this.point.id]
  }

  renderSubPointCard(parentPoint, pointEdge, index){
    return newPointCard(pointEdge,
                        {index: index,
                         parentPoint: parentPoint,
                         expandedIndex: this.state.expandedIndex,
                         handleSeeEvidence: this.handleSeeEvidence,
                         handleHideEvidence:this.handleHideEvidence});
  }

  contentWidth() {
  // TODO old django pointBox.html also checks if point.imageURL.strip exists - is that necessary here? -JF
    if (this.point.imageURL) {
      return "span9"
    } else {
      return "span12 fullWidthContent"
    }
  }

  image() {
  // TODO old django pointBox.html also checks if point.imageURL.strip exists - is that necessary here? -JF
  if (this.point.imageURL)
    return  <div className="span3 pointCardImageContainer"><img className="pointCardImage" src={this.point.fullPointImage} alt="an image"></img></div>
  }

  evidence() {
    if (this.expanded() ) {
      // If this is the first level down, remove an indent bc the Relevance widget effectively creates one when it appears for the first time
      let classesEvidenceBlock = `evidenceBlock ${!this.props.parentPoint ? "removeOneIndent" : null} ${this.numSupportingPlusCounter() == 0 ? "evidenceBlockEmpty" : ""}`
      let classesEvidenceArrow = `evidenceBlock ${!this.props.parentPoint ? "removeOneIndent" : null}`
      console.log("pointCard : evidence() ")
      const singleColumnThreshold = 1224;
      return <div className={classesEvidenceBlock}>
        <div className="arrowPointToSupport">{this.numSupportingPlusCounter() > 0 ? "↓" : null}</div>
        <MediaQuery minDeviceWidth={singleColumnThreshold}>
          {this.supportingPoints()}
          {this.counterPoints()}
        </MediaQuery>
        <MediaQuery maxDeviceWidth={singleColumnThreshold}>
          {this.relevantPoints()}
        </MediaQuery>
      </div>
    }
  }

  supportingPoints(){
    if (this.expanded() && this.point.supportingPoints) {
      return <div className="evidenceBlockSupport">
        <div className="evidenceList">
          {this.point.supportingPoints.edges.length > 0 && <div className="supportHeading">Supporting Claims</div>}
          {this.point.supportingPoints.edges.map((edge, i) => this.renderSubPointCard(this.point, edge, i))}
      <AddEvidence point={this.point} type={EvidenceType.SUPPORT}/>
    </div>
      </div>
    }
  }

  counterPoints(){
    if (this.expanded() && this.point.counterPoints){
      return <div className="evidenceBlockCounter">
        <div className="evidenceList">
          {this.point.counterPoints.edges.length > 0 && <div className="counterHeading">Counter Claims</div>}
          {this.point.counterPoints.edges.map((edge, i) => this.renderSubPointCard(this.point, edge, i))}
          <AddEvidence point={this.point} type={EvidenceType.COUNTER}/>
        </div>
      </div>
    }
  }

  relevantPoints(){
    if (this.expanded() && this.point.relevantPoints){
      return <div className="evidenceBlockCounter">
        <div className="evidenceList">
          {this.point.relevantPoints.edges.length > 0 && <div className="relevantHeading">Relevant Claims</div>}
          {this.point.relevantPoints.edges.map((edge, i) => this.renderSubPointCard(this.point, edge, i))}
          <AddEvidence point={this.point} type={EvidenceType.SUPPORT}/>
          <AddEvidence point={this.point} type={EvidenceType.COUNTER}/>
        </div>
      </div>
    }
  }

  // TODO: this is declared as a local function in two different componants - should it be a global fuction or a const? -JF
  numSupportingPlusCounter(){
    return ( this.point.numSupporting + this.point.numCounter)
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

  sources(){
    if (this.point.sources){
      return <div className="row-fluid">
        <div className="pointText span12">
          <Sources point={this.point}/>
        </div>
      </div>
    }
  }

  handleClickMore(e) {
    e.stopPropagation();
	//console.log("pointCard : handleClickMore(e) ")
  }
  
  moreMenu() {
    return <span className="cardTopRowItem dropdown">
      <a onClick={this.handleClickMore} className="moreMenu dropdown-toggle"  data-toggle="dropdown">&#9776;</a>
      <ul id="" className="dropdown-menu" role="menu" aria-labelledby="dropdownMenu">

         <li><a onClick={this.handleClickEdit} className="" >Edit Claim</a></li>
         <li><a onClick={this.handleClickNoProp} target="_blank" href={this.point.url}>Open in a new tab</a></li>
		 <li><span className=""><span className="iconWithStat fa fa-level-up"></span>{this.point.supportedCount} upstream points</span></li>
       </ul>
    </span>
  }
/* 
         <li><span className="moreMenuHeading">More Actions</span></li>
         <li className="divider"></li> 
*/
/*
        Code to check if current user is the point Author
          {this.props.data.currentUser &&
          this.props.data.currentUser.url == this.point.authorURL &&
          <a onClick={this.handleClickEdit} className="editLink" >Edit</a>}
*/

 pointComponent() {
    const point = this.point;
    if (this.state.editing){
      return <EditPoint point={point} onCancel={this.handleCancelEdit}/>
    } else {
      return <Point point={point} onClick={this.handleToggleEvidence}/>
    }
  }

  // TODO: ref being used on the pointCard to grab it for focus assignment, though that's not fully implemented yet
  render(){
    const point = this.point;
    console.log("rendering " + point.url)
    let classesListedClaim = `listedClaim ${this.state.relLinkClicked ? "relGroupHilite" : "relNotClicked"} ${this.evidenceTypeClass()=="support" ? "linkedClaim" : "rootClaim"}`;
    let classesStackCardGroup = `stackCardGroup ${this.state.relLinkClicked ? "relExtraMarginBottom" : "relNotClicked"}`
    let classesStackCard1 = `stackCard ${this.numSupportingPlusCounter() < 3 ? "stackCardHidden" : ""} ${this.linksRatio() <= 0.75 ? "counter" : ""} ${this.expanded() ? "stackCardDealBottom stackCardDealFade" : ""}`
    let classesStackCard2 = `stackCard ${this.numSupportingPlusCounter() < 2 ? "stackCardHidden" : ""} ${this.linksRatio() <= 0.50 ? "counter" : ""} ${this.expanded() ? "stackCardDealInvertXform stackCardDealFade" : ""}`
    let classesStackCard3 = `stackCard ${this.numSupportingPlusCounter() < 1 ? "stackCardHidden" : ""} ${this.linksRatio() <= 0.25 ? "counter" : ""} ${this.expanded() ? "stackCardDealInvertXform stackCardDealFade" : ""}`
    let classesPointCard = `point-card stackCard ${this.expanded() ? "stackCardDealInvertXform" : ""} ${this.evidenceTypeClass()} row-fluid toggleChildVisOnHover`;
    //console.log("linksRatio " + this.linksRatio() )
    return <div className="listedClaimAndItsEvidence" ref={(input) => { this.cardToScrollTo = input; }}>

    <div className={classesListedClaim} tabIndex="-1" >
      { this.relevanceCtrlUI() }
      { this.relevanceLinkUI() }

	<div className={classesStackCardGroup} tabIndex="0" onClick={this.handleToggleEvidenceFromCard} ref={(input) => { this.cardToFocusOn = input;}}>
    <div className={classesStackCard1} tabIndex="-1">
    <div className={classesStackCard2} tabIndex="-1">
    <div className={classesStackCard3} tabIndex="-1">
	
      <div className={classesPointCard} tabIndex="-1">
      <div className={ this.contentWidth()  }>
        <div className="row-fluid">
        <div className="cardTopRow span12">
          <Byline point={point}/>
          <CommentCount point={point}/>
          <ShareIcon point={point}/>
          { this.moreMenu() }
        </div>
        </div>
        <div className="row-fluid">
        <div className="pointText span12">
          { this.pointComponent() }
        </div>
        </div>
        {this.sources()}
        <div className="row-fluid">
        <div className="cardBottomActionRow" >
          <span><EvidenceLink point={point} onSee={this.handleSeeEvidence} onHide={this.handleHideEvidence} onToggle={this.handleToggleEvidence} expanded={this.expanded()}/></span>
          <span><AgreeDisagree point={point} parentPoint={this.props.parentPoint}/></span>
        </div>
        </div>
      </div>
      {this.image()}
      </div>
	  
    </div>
    </div>
    </div>
    </div>

    </div>

      <div className="evidenceRow row-fluid">
      {this.evidence()}
      </div>

    </div>;
  }
}

export function newPointCard(pointEdge, {index, expandedIndex, handleSeeEvidence, handleHideEvidence, parentPoint}) {
  let point = pointEdge.node;
  let classes = `listedClaimGroup`;
  if (point) {
  return <div className={classes} key={point.url}>
      <ExpandedPointCard point={point}
    url={point.url}
    expandedIndex={expandedIndex}
    expanded={true}
    link={pointEdge.link}
    handleSeeEvidence={handleSeeEvidence}
    handleHideEvidence={handleHideEvidence}
    parentPoint={parentPoint}/>
      </div>;
  } else {
    return <div className="listedClaimGroup" key={index}></div>;
  }
}


export const GetPoint = gql`
${expandedPointFieldsFragment}
query Point($url: String) {
  point(url: $url) {
    ...pointFields,
    ...evidenceFields
 }
}`

export {PointCard};
export const ExpandedPointCard = graphql(GetPoint)(PointCard)

// TODO: explore a mutation-based point loading model
// export const ExpandPoint = gql`
// ${expandedPointFieldsFragment}
// mutation ExpandPoint($url: String!) {
//   expandPoint(url: $url) {
//     point {
//       id,
//       ...evidenceFields
//     }
//   }
// }`
// export const CollapsedPointCard = graphql(ExpandPoint)(PointCard)
