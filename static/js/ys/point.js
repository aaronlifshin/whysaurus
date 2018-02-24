import React from 'react';
import ReactDOM from 'react-dom';
import { graphql, compose } from 'react-apollo';
import gql from 'graphql-tag';
import { Form, Text } from 'react-form';
import MediaQuery from 'react-responsive';
import AnimateOnChange from 'react-animate-on-change';

// TODO: make work
//import Arrow from '@elsdoerfer/react-arrow';

import { CurrentUserQuery, EditPointQuery, AddEvidenceQuery, VoteQuery, RelevanceVoteQuery, GetPoint, GetCollapsedPoint } from './schema.js';
import {PointList} from './point_list.js'

// For Responsive 
const singleColumnThreshold = 960;

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

const EditTitleForm = ( props ) => {
  return (
      <Form onSubmit={props.onSubmit}>
      { formApi => (
          <form onSubmit={formApi.submitForm} id="form1" className="editPointTextForm">
          <Text onClick={props.onClick} field="title" id="editPointTextField"/>
          <button onClick={props.onClick} className="buttonUX2" type="submit">Save</button>
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
    this.handleClickNoProp = this.handleClickNoProp.bind(this);
  }

  // TODO: this simple function is also defined in the PointCard component - can/should it be declared in a single place somehow?
  handleClickNoProp(e) {
    e.stopPropagation();
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
      return <span><img id="spinnerImage" className="spinnerPointSubmitButtonPosition" src="/static/img/ajax-loader.gif"/>Saving...</span>
    } else {
      return <span>
        <EditTitleForm onClick={this.handleClickNoProp} onSubmit={this.handleClickSave}/>
      </span>
    }
  }

  render(){
    const score = this.point.pointValue
    return <div>
      {this.titleUI()}
      <button onClick={this.props.onCancel} type="cancel" className="cancelButton">Cancel</button>
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
    <span className="scoreAnimContainerMax score">
    <span className="scoreAnimContainerReset">
      <Hover onHover={<VoteStats point={this.point}/>}>
       <span className="ux2ScoreInLine number"><span className={score < 0 ? "negativeScore": "positiveScore"}><AnimateOnChange baseClassName="scorePreAnimate" animationClassName="Score--bounce" animate={score == prevScore}>{score >= 0 && "+"}{score}</AnimateOnChange></span></span>
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
        return <a className="cardBottomAction hideEvidence" onClick={this.handleClickHide}>Close</a>
      } else {
        return <a className="cardBottomAction seeEvidence" onClick={this.handleClickSee}>See Evidence</a>
      }
    } else {
      if (this.props.expanded) {
        return <a className="cardBottomAction hideEvidence" onClick={this.handleClickToggle}>Close</a>
      } else {
        return <a className="cardBottomAction" onClick={this.handleClickToggle}>Add Evidence</a>
          }
    }
  }

  render(){
  return <span className="evidenceContainer">{this.whichEvidenceButton()}</span>
  }
}

// TODO : depending on user tests, maybe add <div className="addEvidenceFormLabel">Add evidence this list</div>
const AddEvidenceForm = ( props ) => {
  let submitClasses = `buttonUX2 addEvidenceFormButton ${props.evidenceType=="counter" ? "buttonUX2Red" : ""}`
  return (
    <div className="addEvidenceFormGroup">
      <Form onSubmit={props.onSubmit}>
      { formApi => (
          <form onSubmit={formApi.submitForm} id="form1" className="addEvidenceForm">
          <Text field="title" id="title" className="addEvidenceFormTextField" placeholder='Make a claim, eg "Dogs can learn more tricks than cats."' />
          <button type="submit" className={submitClasses}>Add</button>
          <button type="cancel" className="cancelButton cancelButtonAddEvidence" onClick={props.onCancel}>Cancel</button>
          </form>
      )}
    </Form>
  </div>
  );
}

class AddEvidenceCard extends React.Component {
  constructor(props) {
    super(props)
    this.state = {addingSupport: false, addingCounter: false }
    this.handleClickCancel = this.handleClickCancel.bind(this)
    this.handleClickAddEvidenceSupport = this.handleClickAddEvidenceSupport.bind(this)
    this.handleClickAddEvidenceCounter = this.handleClickAddEvidenceCounter.bind(this)
    
    // TODO: CONDENSE THESE TWO INTO SINGLE FUNCTIONS WITH A VARIABLE? - JF    
    this.handleClickSaveSupport = this.handleClickSaveSupport.bind(this)
    this.handleClickSaveCounter = this.handleClickSaveCounter.bind(this)

  }

  get point() {
    return this.props.point;
  }

  handleClickAddEvidenceSupport(e) {
    console.log("add evidence")
    if (this.props.data.currentUser){
      this.setState({addingSupport: true, addingCounter: false})
    } else {
      $("#loginDialog").modal("show");
    }
  }
  
  handleClickAddEvidenceCounter(e) {
    console.log("add evidence")
    if (this.props.data.currentUser){
      this.setState({adding: false, addingCounter: true})
    } else {
      $("#loginDialog").modal("show");
    }
  }  
 
  handleClickCancel(e){
    e.stopPropagation();
    this.setState({addingSupport: false, addingCounter: false})
    console.log("AddEvidenceCard : handleCancel")
  }

  // TODO: CONDENSE THESE TWO INTO A SINGLE FUNCTION WITH A VARIABLE? - JF
  //    only differences are the values.linkType line and second data.point. line
  handleClickSaveSupport(values, e, formApi) {
    console.log("AddEvidenceCard : handleClickSave")
    let parentURL = this.point.url
    values.parentURL = parentURL
    values.linkType = "supporting"
    this.setState({saving: true})
    this.props.mutate({
      variables: values,
      update: (proxy, { data: { addEvidence: { newEdges } }}) => {
        const data = proxy.readQuery({ query: GetPoint, variables: {url: parentURL} })
        data.point.relevantPoints.edges = data.point.relevantPoints.edges.concat(newEdges.edges)

        data.point.supportingPoints.edges = data.point.supportingPoints.edges.concat(newEdges.edges)

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
  handleClickSaveCounter(values, e, formApi) {
    console.log("AddEvidenceCard : handleClickSave")
    let parentURL = this.point.url
    values.parentURL = parentURL
    values.linkType = "counter"
    this.setState({saving: true})
    this.props.mutate({
      variables: values,
      update: (proxy, { data: { addEvidence: { newEdges } }}) => {
        const data = proxy.readQuery({ query: GetPoint, variables: {url: parentURL} })
        data.point.relevantPoints.edges = data.point.relevantPoints.edges.concat(newEdges.edges)
        
        data.point.counterPoints.edges = data.point.counterPoints.edges.concat(newEdges.edges)

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
 
  renderAddEvidenceForm(evidenceType) {
    console.log("AddEvidenceCard : renderAddEvidenceForm : " + evidenceType)
    return <span>
        { this.state.saving ? <span className="addEvidenceFormSaving"><img id="spinnerImage" className="spinnerPointSubmitButtonPosition" src="/static/img/ajax-loader.gif"/>Saving...</span> : <AddEvidenceForm evidenceType={evidenceType} onSubmit={evidenceType=="support" ? this.handleClickSaveSupport : this.handleClickSaveCounter} onCancel={this.handleClickCancel}/> }
    </span>
  } 

  addText(evidenceType){   
    switch (evidenceType){
      case "support":
        return "Add Evidence For"
      case "counter":
        return "Add Evidence Against"
      default:
        return "Add Evidence"
    }
  }

  // TODO: this is declared as a local function in two different components - should it be a global fuction or a const? -JF
  numSupportingPlusCounter(){
    return ( this.point.numSupporting + this.point.numCounter)
  }

  renderAddEvidenceButton(evidenceType) {
    let classesButton = `buttonUX2 ${evidenceType=="counter" ? "buttonUX2Red" : ""} addEvidenceButton`
    let nameButton = `${evidenceType=="counter" ? "addCounterEvidenceButton" : "addSupportingEvidenceButton" }`
    let buttonLabel = this.addText(evidenceType)
    return <button type="button" name={nameButton} tabIndex="0" className={classesButton}>{buttonLabel}</button>
  }

/*
  render() {
    let classesButtonGrp = `addEvidenceButtonGrp ${this.linkType=="counter" ? "addEvidenceButtonGrpCounter" : "" }`
    // This logic is bananas. I'm sorry. I'll find ways to make it clearer as the implementation continues. - JF
    let classesLineWideScreen = `dottedLine dottedLineAddEvidenceButton ${this.linkType=="counter" ? "dottedLineAddCounter" : "dottedLineAddSupport" }  ${(this.numSupportingPlusCounter() < 1 || (this.linkType=="counter" && (this.point.numCounter < 1 || this.point.numSupporting < 1))) ? "hidden" : "" }`	
  	let classesLineNarrowScreen = `${(this.linkType=="supporting" && (this.numSupportingPlusCounter() > 0)) ? "dottedLine dottedLineAddEvidenceButton dottedLineAddSupport" : "hidden"}`	
    let classesArrowWideScreen = `${(this.linkType=="supporting" || (this.point.numCounter > 0 && this.point.numSupporting > 0)  ) ? "arrowAddEvidenceButton" : "hidden"}`
  	let classesArrowNarrowScreen = `${this.linkType=="supporting" ? "arrowAddEvidenceButton" : "hidden"}`    
    return <a onClick={this.handleClickAddEvidence}>
	         <div className={classesButtonGrp}>			   			   
            <MediaQuery minWidth={singleColumnThreshold}>
              <div className={classesLineWideScreen}></div>
              <div className={classesArrowWideScreen}>&#x21B3;</div>
            </MediaQuery>
            <MediaQuery maxWidth={singleColumnThreshold}>
              <div className={classesLineNarrowScreen}></div>
              <div className={classesArrowNarrowScreen}>&#x21B3;</div>
            </MediaQuery>			   		   
            { this.state.adding ? this.renderAddEvidenceForm() : this.renderAddEvidenceButton() }
	         </div>
	        </a> 
  }
 */ 
 
  get uiType(){
    return this.props.type
  }

  renderAddEvidenceFormBasedOnState() {
    if (this.state.addingSupport) {
      return <span>
        {this.renderAddEvidenceForm("support")}
      </span>     
    }
    else if (this.state.addingCounter) {
      return <span>
        {this.renderAddEvidenceForm("counter")}
      </span>      
    }
    else return (null)       
  }
  
  renderSupportButton() {
    return <a onClick={this.handleClickAddEvidenceSupport}>{this.renderAddEvidenceButton("support")}</a>    
  }
  renderCounterButton() {
    return <a onClick={this.handleClickAddEvidenceCounter}>{this.renderAddEvidenceButton("counter")}</a>       
  }  
  renderDualButtons() {
      return <span>
        {this.renderSupportButton()}
        {this.renderCounterButton()}     
      </span>       
  }
  
  renderEvidenceArrow(color) {
    let arrowGrpClass = `arrowEvidence`
    let arrowHeadClass = `arrowHeadUp ${color == "red" && "arrowHeadUpRed"}`
    let arrowStemClass = `arrowStemEvidence ${(this.numSupportingPlusCounter() == 0) && "arrowStemEvidenceShort" } ${color == "red" && "arrowStemRed"}`
    return <div className={arrowGrpClass}>
          <div className={arrowHeadClass}></div>
          <div className={arrowStemClass}></div>
        </div>    
  }
    
  render() {
    let topDivClass = `addEvidenceUI ${(this.numSupportingPlusCounter() > 0) && "verticalOffsetForLongEvidenceArrow" }   `
    switch (this.uiType) {  
    case "DUAL":
      return <div className={topDivClass}>
        { this.renderEvidenceArrow() }
        { (this.state.addingSupport || this.state.addingCounter) ? this.renderAddEvidenceFormBasedOnState() : this.renderDualButtons() }       
      </div>      
    case "SUPPORT":
      return <div className={topDivClass}>
        { this.renderEvidenceArrow() }
        { this.state.addingSupport ? this.renderAddEvidenceForm("support") : this.renderSupportButton() }  
      </div>      
    case "COUNTER":
      return <div className={topDivClass}> 
        { this.renderEvidenceArrow("red") }      
        { this.state.addingCounter ? this.renderAddEvidenceForm("counter") : this.renderCounterButton() }  
      </div>      
    default:
      console.log("AddEvidenceCard : render() : something's wrong!")
      return <div className={topDivClass}> 
      </div>    
    }
   
  }
}


const AddEvidence = compose(
  graphql(AddEvidenceQuery),
  graphql(CurrentUserQuery),
)(AddEvidenceCard)

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


class RelevanceComponent extends React.Component {
  constructor(props) {
    super(props);
    // This binding is necessary to make `this` work in the callback
    this.handleClick0 = this.handleClick0.bind(this);
    this.handleClick33 = this.handleClick33.bind(this);
    this.handleClick66 = this.handleClick66.bind(this);
    this.handleClick100 = this.handleClick100.bind(this);
    this.handleClickClose = this.handleClickClose.bind(this);
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

  handleClickClose() {
    //console.log("");
    this.props.onClose && this.props.onClose()
  }

  linkClassFor(vote){
    let defaultClasses = "relVoteLink number "
    let myVoteClass = "myRelevanceVote0"
    if (vote == 33)
      myVoteClass = "myRelevanceVote33"
    else if (vote == 66)
      myVoteClass = "myRelevanceVote66"
    else if (vote == 100)
      myVoteClass = "myRelevanceVote100"
    return (this.props.link.relevanceVote == vote) ? (defaultClasses + myVoteClass) : defaultClasses
  }

  get relevance() {
    return this.props.link && this.props.link.relevance
  }

  // TODO: add number of Votes so far to relevanceStats
  render(){
    return <div className="relCtrlGroup" >
          <span className="relCtrlClose"><a onClick={this.handleClickClose}>&#xd7;</a></span>
      <div className="relCtrlLabel pointTitle">How Relevant is this claim for you?</div>
        <div className="relCtrlVoteOptions">
          <a className={this.linkClassFor(100) + " relVoteLink100"} onClick={this.handleClick100}>100<span className="perctSignSmall">%</span></a>
          <a className={this.linkClassFor(66) + " relVoteLink66"} onClick={this.handleClick66}>66<span className="perctSignSmall">%</span></a>
          <a className={this.linkClassFor(33) + " relVoteLink33"} onClick={this.handleClick33}>33<span className="perctSignSmall">%</span></a>
          <a className={this.linkClassFor(0) + " relVoteLink0"} onClick={this.handleClick0}>0<span className="perctSignSmall">%</span></a>
            </div>
        <div className="relevanceExplanation">
                  <div className="relevanceStats">{this.relevance}% average on all votes so far</div>
          <div className="relevanceEquation">Relevance impacts argument scores dramatically. <a target="_blank" href="../WhatIsWhysaurus#nutsAndBolts">Learn more</a>.</div>
                </div>
      </div>
    }
}

// A Claim's Score * its Avg Relevance = its contribution to its parent's score

const RelevanceVote = compose(
  graphql(RelevanceVoteQuery),
  graphql(CurrentUserQuery),
)(RelevanceComponent)


class PointCard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      expanded: props.expanded,
      relLinkClicked: false
    }
    this.handleCancelEdit = this.handleCancelEdit.bind(this);
    this.handleSeeEvidence = this.handleSeeEvidence.bind(this);
    this.handleHideEvidence = this.handleHideEvidence.bind(this);
    this.handleToggleEvidence = this.handleToggleEvidence.bind(this);
    this.handleRelClick = this.handleRelClick.bind(this);
    this.handleClickEdit = this.handleClickEdit.bind(this);
    this.handleClickMore = this.handleClickMore.bind(this);
    this.handleClickNoProp = this.handleClickNoProp.bind(this);
  }

  // TODO: this simple function is also defined in the EditPointComponent component - can/should it be declared in a single place somehow?
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
              <RelevanceVote point={this.point} parentPoint={this.props.parentPoint} link={this.props.link} linkType={this.evidenceType} onClose={this.handleRelClick}/>
            </div> :
            <span className="noRelevanceCtrl"></span>
        }
      </span>
    } else {
      return null
    }
  }

  // TODO: rebuild arrow using css in order to control stroke width and cross-browser display, instead of unicode &#x21B3;
  // TODO: make animation only occur on the claim being manipulated (rather than on all relevance)
  //  code with animation:  <AnimateOnChange baseClassName="relevanceDisplay" animationClassName="Score--bounce" animate={this.relevance != -1}>{this.relevance}%</AnimateOnChange>
  relevanceLinkUI() {
    if (this.props.parentPoint) {
    let classesRelevanceLink = `relevanceLink ${this.evidenceTypeClass()}`
    return <a className={classesRelevanceLink} onClick={this.handleRelClick}>
      <div className="relevanceLinkArea">
        <div className="dottedLine dottedLineRelevanceLink"></div>
                <span className="relevanceDisplay number"><span className="positionRelDisplay">{this.relevance}<span className="perctSignSmallRelLink">%</span></span></span>
        <div className="dottedLine dottedLineElbow"></div>
      </div></a>
    } else {
      return null
    }
  }

  handleCancelEdit(e) {
    e.stopPropagation()
    this.setState({editing: false})
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

  // When user clicks on the pointTitle or "Add Evidence"
  handleToggleEvidence() {
    if (this.expanded()) {
      this.collapse()
    } else {
      this.expand()
    }
  }

  expanded() {
    return this.state.expanded;
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
      let classesEvidenceBlock = `evidenceBlock ${!this.props.parentPoint ? "removeOneIndent" : null}`
      //old idea:  <div className="arrowPointToSupport">{this.numSupportingPlusCounter() > 0 ? "↓" : null}</div>
      //console.log("pointCard : evidence() ")
      if (this.numSupportingPlusCounter() == 0) {
        return <div className={classesEvidenceBlock + " evidenceBlockEmpty"}>
          <AddEvidence point={this.point} type={"DUAL"}/>
        </div>
      } 
      else {
        return <div className={classesEvidenceBlock}>    
         <MediaQuery minWidth={singleColumnThreshold}> 
          {this.point.supportingPoints.edges.length > 0 && this.supportingPoints()}
          {this.point.counterPoints.edges.length > 0 && this.counterPoints()}                    
         </MediaQuery>
         <MediaQuery maxWidth={singleColumnThreshold}>
          {this.relevantPoints()}
         </MediaQuery>
        </div>
      }
    }
  }
  
  supportingPoints(){
    if (this.expanded() && this.point.supportingPoints) {
      return <div className="evidenceBlockSupport">
        <div className="evidenceList">
          <div className="supportHeading">Evidence For</div>
          <PointList edges={this.point.supportingPoints.edges} parentPoint={this.point}/>         
          {this.point.counterPoints.edges.length < 1 ? <AddEvidence point={this.point} type={"DUAL"}/> : <AddEvidence point={this.point} type={"SUPPORT"}/> }          
        </div>
      </div>
    }
  }

  counterPoints(){
    if (this.expanded() && this.point.counterPoints){
      return <div className="evidenceBlockCounter">
        <div className="evidenceList">
          <div className="counterHeading">Evidence Against</div>
          <PointList edges={this.point.counterPoints.edges} parentPoint={this.point}/>
          {this.point.supportingPoints.edges.length < 1 ? <AddEvidence point={this.point} type={"DUAL"}/> : <AddEvidence point={this.point} type={"COUNTER"}/> }          
        </div>
      </div>
    }
  }

  // TODO: if users ask about this, add <span className="sortBy">Sorted by Relevance</span>
  relevantPoints(){
    if (this.expanded() && this.point.relevantPoints){
      return <div className="evidenceBlockCounter">
        <div className="evidenceList">
          {this.point.relevantPoints.edges.length > 0 && <div className="supportHeading">Evidence</div>}
        <PointList edges={this.point.relevantPoints.edges} parentPoint={this.point}/>
        <AddEvidence point={this.point} type={"DUAL"}/>
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

  // TODO: add code to link to other "upstream" claims
  // <li><span className=""><span className="iconWithStat fa fa-level-up"></span>Linked to {this.point.supportedCount} other claims</span></li>
  moreMenu() {
    return <span className="cardTopRowItem dropdown">
      <a onClick={this.handleClickMore} className="moreMenu dropdown-toggle"  data-toggle="dropdown">&#9776;</a>
          <ul id="" className="dropdown-menu dropdown-menu-with-caret" role="menu" aria-labelledby="dropdownMenu">
                <div className="dropdown-caret">
        <div className="caret-outer"></div>
        <div className="caret-inner"></div>
      </div>
         <li><a onClick={this.handleClickEdit} className="" ><span className="iconWithStat fa fa-pencil"></span>Edit Claim</a></li>
         <li><a onClick={this.handleClickNoProp} target="_blank" href={this.point.url}><span className="iconWithStat fa fa-external-link"></span>Open in a new tab</a></li>
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

 pointTextComponent() {
    const point = this.point;
    if (this.state.editing){
      return <EditPoint point={point} onCancel={this.handleCancelEdit}/>
    } else {
      return <Point point={point} onClick={this.handleToggleEvidence}/>
    }
  }

  // TODO: ref being used on the pointCard to grab it for focus assignment, though that's not fully implemented yet
  render(){
    if (this.point){
      const point = this.point;
      console.log("rendering " + point.url)
      let classesListedClaim = `listedClaim ${this.state.relLinkClicked ? "relGroupHilite" : "relNotClicked"} ${this.evidenceTypeClass()=="support" ? "linkedClaim" : "rootClaim"}`;
      let classesStackCardGroup = `stackCardGroup ${this.state.relLinkClicked ? "relExtraMarginBottom" : "relNotClicked"}`
      let classesStackCard1 = `stackCard ${this.numSupportingPlusCounter() < 3 ? "stackCardHidden" : ""} ${this.linksRatio() <= 0.75 ? "counter" : ""} ${this.expanded() ? "stackCardDealBottom stackCardDealFade" : ""}`
      let classesStackCard2 = `stackCard ${this.numSupportingPlusCounter() < 2 ? "stackCardHidden" : ""} ${this.linksRatio() <= 0.50 ? "counter" : ""} ${this.expanded() ? "stackCardDealInvertXform stackCardDealFade" : ""}`
      let classesStackCard3 = `stackCard ${this.numSupportingPlusCounter() < 1 ? "stackCardHidden" : ""} ${this.linksRatio() <= 0.25 ? "counter" : ""} ${this.expanded() ? "stackCardDealInvertXform stackCardDealFade" : ""}`
      let classesPointCard = `point-card stackCard ${this.expanded() ? "stackCardDealInvertXform" : ""} ${this.evidenceTypeClass()} row-fluid toggleChildVisOnHover`;
      let classesRelevanceDot = `${this.props.parentPoint ? "cardBottomAction bottomActionDot" : "hidden" }`
      let classesRelevanceBottomLink = `${this.props.parentPoint ? "cardBottomAction relevanceVoteBottomAction" : "hidden" }`
      //console.log("linksRatio " + this.linksRatio() )
      return <div className="listedClaimGroup">
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
          { this.pointTextComponent() }
        </div>
        </div>
        {this.sources()}
        <div className="row-fluid">
        <div className="cardBottomActionRow" >
          <span><EvidenceLink point={point} onSee={this.handleSeeEvidence} onHide={this.handleHideEvidence} onToggle={this.handleToggleEvidence} expanded={this.expanded()}/></span>
          <span className="cardBottomAction bottomActionDot">·</span>
                  <span><AgreeDisagree point={point} parentPoint={this.props.parentPoint}/></span>
                  <span className={classesRelevanceDot}>·</span>
                  <a className={classesRelevanceBottomLink} onClick={this.handleRelClick}>Relevance</a>
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

    </div>
    </div>

      <div className="evidenceRow row-fluid">
      {this.evidence()}
      </div>

      </div>
        </div>;
    } else if (this.props.data && this.props.data.loading) {
      return <div>Loading...</div>
    } else {
      return <div>Something strange happened...</div>
    }
  }
}

export {PointCard};

export const ExpandedPointCard = graphql(GetPoint)(PointCard)