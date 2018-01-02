import React from 'react';
import ReactDOM from 'react-dom';
import { graphql, compose } from 'react-apollo';
import gql from 'graphql-tag';
import { Form, Text } from 'react-form';

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

export const expandedPointFieldsFragment = gql`
${pointFieldsFragment}
fragment evidenceFields on Point {
 supportingPoints { edges { node { title, upVotes, ...pointFields }, link { id, type, relevance, parentURLsafe, childURLsafe }} },
 counterPoints { edges { node { title, upVotes, ...pointFields }, link { id, type, relevance, parentURLsafe, childURLsafe }} }
}`

export const EvidenceType = Object.freeze({
    ROOT: Symbol("root"),
    SUPPORT:  Symbol("supporting"),
    COUNTER: Symbol("counter")
});

function Byline(props){
  return <span className="cardTopRowItem"><span>By </span><a className="byline" target="_blank" href={"/user/" + props.point.authorURL}>@{props.point.authorName}</a></span>
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
function MoreMenu(props) {
	return <span className="cardTopRowItem dropdown">
			<a className="moreMenu dropdown-toggle"  data-toggle="dropdown">&#9776;</a>
			 <ul id="stats" className="dropdown-menu" role="menu" aria-labelledby="dropdownMenu">
                <li>More Actions</li>
                <li className="divider"></li> 
				<li>
					<span className=""><span className="iconWithStat fa fa-level-up"></span>{props.point.supportedCount} Upstream Points</span>
				</li>
				 <li className="divider"></li> 
                <li>
					<a onClick={props.point.handleClickEdit} className="" >Edit</a>
				</li>
            </ul> 
		</span>	
}
/*
				Code to check if current user is the point Author
					{this.props.data.currentUser &&
					this.props.data.currentUser.url == this.point.authorURL &&
					<a onClick={this.handleClickEdit} className="editLink" >Edit</a>}					
*/


// thanks, https://stackoverflow.com/questions/29981236/how-do-you-hover-in-reactjs-onmouseleave-not-registered-during-fast-hover-ove
const Hover = ({ onHover, children }) => (
    <span className="hover">
      <span className="hover__no-hover">{children}</span>
      <span className="hover__hover">{onHover}</span>
    </span>
)

const VoteStats = ({point}) => (
    <div className="vote-stats">
      <p>Agreed: {point.upVotes} <br/> Disagreed: {point.downVotes}</p>
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
          <form onSubmit={formApi.submitForm} id="form1">
          <Text field="title" id="title" />
          <button type="submit">Save</button>
          </form>
      )}
    </Form>
  );
}

class PointComponent extends React.Component {
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
    console.log("edit");
    this.setState({editing: true})
  }

  handleClickSave(values, e, formApi) {
    console.log("saving edits")
    values.url = this.point.url
    this.setState({saving: true})
    this.props.mutate({
      variables: values
    })
    // this component will be replaced after save, so we don't need to update state
  }

  titleUI() {
    if (this.state.editing) {
      if (this.state.saving) {
        return <span>Saving...</span>
      } else {
        return <span>
            <EditTitleForm onSubmit={this.handleClickSave}/>
          </span>
      }
    } else {
      return <span className="pointTitle">
        <a href={this.point.url}>{this.point.title}</a>
        </span>
      /*return <span className="pointTitle">
        <a href={this.point.url}>{this.point.title}</a>
		{this.props.data.currentUser &&
        this.props.data.currentUser.url == this.point.authorURL &&
        <a onClick={this.handleClickEdit} className="editLink" >edit</a>}
        </span>	*/			
    }
  }

  render(){
    const score = this.point.pointValue
    return <div>
      {this.titleUI()}
	  <span className="scoreAnimContainerMax">
	  <span className="scoreAnimContainerReset">
      <Hover onHover={<VoteStats point={this.point}/>}>
      <span className="ux2ScoreInLine"><span className="positiveScore">{score > 0 && "+"}{score}</span></span>
      </Hover>
	  </span>
	  </span>
      </div>
  }
}

const Point = compose(
  graphql(EditPointQuery),
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
        <div key={i} className="source"><img className="iconSourcesSmall" src="/static/img/sourcesIconSmall_grey.png"/><a href={url}>{name}</a></div>
      )}
    </div>
  }
}

class EvidenceLink extends React.Component {
  constructor(props) {
    super(props)
    this.handleClickSee = this.handleClickSee.bind(this);
    this.handleClickHide = this.handleClickHide.bind(this);
  }

  get point() {
    return this.props.point;
  }

  hasEvidence() {
    return this.point.numSupporting > 0 || this.point.numCounter > 0;
  }
  
  handleClickSee(e) {
	console.log("see");
    this.props.onSee && this.props.onSee()
  }

  handleClickHide(e) {
    console.log("hide");
    this.props.onHide && this.props.onHide()
  }
  
  whichEvidenceButton() {
	if (this.hasEvidence()) {
      if (this.props.expanded) {
        return <a className="pointcardBottomRowAction hideEvidence" onClick={this.handleClickHide}>Hide Evidence</a>
      } else {
        return <a className="pointcardBottomRowAction seeEvidence" onClick={this.handleClickSee}>See Evidence</a>
      }
    } else {
      return <span className="pointcardBottomRowAction"><span className="shownStatTillHidden">No </span><span className="hiddenStatTillRevealed">Add </span>Evidence</span>
    }  
  }

  render(){
	return <span className="seeEvidenceContainer">{this.whichEvidenceButton()}</span>
  }
}

const AddEvidenceForm = ( props ) => {
  return (
      <Form onSubmit={props.onSubmit}>
      { formApi => (
          <form onSubmit={formApi.submitForm} id="form1">
          <label htmlFor="title">Title</label>
          <Text field="title" id="title" />
          <button type="submit">Add</button>
          </form>
      )}
    </Form>
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
    values.parentURL = this.point.url
    values.linkType = this.linkType
    this.setState({saving: true})
    this.props.mutate({ 
      variables: values
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

  // TODO: Should this function be renamed to be specific/descriptive, like addEvidenceLabel? -JF
  get addText(){
    switch (this.evidenceType){
      case EvidenceType.ROOT:
        return "Add Point"
      case EvidenceType.SUPPORT:
        return "Add Support"
      case EvidenceType.COUNTER:
        return "Add Counterpoint";
      default:
        return "Add Evidence"
    }
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
      return <div className="addEvidenceButton"><a  onClick={this.handleClickAddEvidence}>{this.addText}</a></div>
    }
  }
}

export const AddEvidenceQuery = gql`
${expandedPointFieldsFragment}
mutation AddEvidence($title: String!, $linkType: String, $parentURL: String, $imageURL: String, $imageAuthor: String, $imageDescription: String, $sourceURLs: [String], $sourceNames: [String]) {
  addEvidence(pointData: {title: $title, content: $title, summaryText: $title, imageURL: $imageURL, imageAuthor: $imageAuthor, imageDescription: $imageDescription, sourceURLs: $sourceURLs, sourceNames: $sourceNames, linkType: $linkType, parentURL: $parentURL}) {
    point {
    ...pointFields,
    ...evidenceFields
    }
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

  handleClickAgree() {
    console.log("agree");
    if (this.props.data.currentUser){
      this.props.mutate({
        variables: {url: this.props.point.url,
                    vote: 1,
                    parentURL: this.props.parentPoint && this.props.parentPoint.url}
      }).then( res => {
        console.log(res)
      });	  	  
    } else {
      $("#loginDialog").modal("show");
    }
  }

  handleClickDisagree() {
    console.log("disagree");
    if (this.props.data.currentUser){
      this.props.mutate({
        variables: {url: this.props.point.url,
                    vote: -1,
                    parentURL: this.props.parentPoint && this.props.parentPoint.url}
      }).then( res => {
        console.log(res)
      });
    } else {
      $("#loginDialog").modal("show");
    }
  }

  agreeClass(){
    return "pointcardBottomRowAction agree" + (this.props.point.currentUserVote == 1 ? " current-vote" : "")
  }

  disagreeClass(){
    return "pointcardBottomRowAction disagree" + (this.props.point.currentUserVote == -1 ? " current-vote" : "")
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

  render(){
    return <span className="relVoteGroup" >
	  vote on relevance: 
      <a className="relVoteLink" onClick={this.handleClick0}>0%</a>
      <a className="relVoteLink" onClick={this.handleClick33}>33%</a>
      <a className="relVoteLink" onClick={this.handleClick66}>66%</a>
      <a className="relVoteLink" onClick={this.handleClick100}>100%</a>
      </span>
    }
}

const RelevanceVote = compose(
  graphql(RelevanceVoteQuery),
  graphql(CurrentUserQuery),
)(RelevanceComponent)


class PointCard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {expandedIndex: {}}
    this.handleSeeEvidence = this.handleSeeEvidence.bind(this);
    this.handleHideEvidence = this.handleHideEvidence.bind(this);
    this.renderSubPointCard = this.renderSubPointCard.bind(this);
  }

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

  get relevance() {
    return this.props.link && this.props.link.relevance
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

  expanded() {
    return this.state.expandedIndex[this.point.id]
  }

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
  
  // Alt approach to animation, currently unused - JF
  animClass() {
	console.log(' animClass() ');
	if (this.expanded()) 
		return "animateSiblingsDown";
	else 
		return "noAnim";
  }
    

  renderSubPointCard(parentPoint, pointEdge, index){
    return newPointCard(pointEdge,
                        {index: index,
                         parentPoint: parentPoint,
                         expandedIndex: this.state.expandedIndex,
                         handleSeeEvidence: this.handleSeeEvidence,
                         handleHideEvidence:this.handleHideEvidence});
  }

  relevanceUI() {
    if (this.props.parentPoint) {
      return <div className="relevanceDisplay"><Hover onHover={<RelevanceVote point={this.point} parentPoint={this.props.parentPoint} linkType={this.evidenceType}/>}>
               <span >{this.relevance}%</span>
             </Hover></div>
        
      return <RelevanceVote point={this.point} parentPoint={this.props.parentPoint} linkType={this.evidenceType}/>
    }
  }
  
  contentWidth() {
	// TODO old django pointBox.html also checks if point.imageURL.strip exists - is that necessary here? -JF
	if (this.point.imageURL)
	  return "span9"
	else	
	  return "span12 fullWidthContent"
  }
  
  image() {
	// TODO old django pointBox.html also checks if point.imageURL.strip exists - is that necessary here? -JF
	if (this.point.imageURL)
		return  <div className="span3 pointCardImageContainer"><img className="pointCardImage" src={this.point.fullPointImage} alt="an image"></img></div>
  }
  
  evidence() {
    if (this.expanded() ) {
      return <div className="evidenceBlock">
	    {this.supportingPoints()}
        {this.counterPoints()}
	  </div>		
	}
  }
		
  supportingPoints(){
    if (this.expanded() && this.point.supportingPoints) {
      return <div className="evidenceBlockSupport">
        <div className="evidenceList">
          {this.point.supportingPoints.edges.length > 0 && <div className="supportHeading">Supporting Claims</div>}	  
          {this.point.supportingPoints.edges.map((edge, i) => this.renderSubPointCard(this.point, edge, i))}
        </div>
        <AddEvidence point={this.point} type={EvidenceType.SUPPORT}/>
      </div>
    }
  }
  
  counterPoints(){
    if (this.expanded() && this.point.counterPoints){
      return <div className="evidenceBlockCounter">
        <div className="evidenceList">
	  {this.point.counterPoints.edges.length > 0 && <div className="counterHeading">Counter Claims</div>}	  		
          {this.point.counterPoints.edges.map((edge, i) => this.renderSubPointCard(this.point, edge, i))}
        </div>
        <AddEvidence point={this.point} type={EvidenceType.COUNTER}/>
      </div>
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

  moreMenu() {
	return <span className="cardTopRowItem dropdown">
			<a className="moreMenu dropdown-toggle"  data-toggle="dropdown">&#9776;</a>
			 <ul id="stats" className="dropdown-menu" role="menu" aria-labelledby="dropdownMenu">
                <li>More Actions</li>
                <li className="divider"></li> 
				<li>
					<span className=""><span className="iconWithStat fa fa-level-up"></span>{this.point.supportedCount} upstream points</span>
				</li>
				 <li className="divider"></li> 
                <li>
					<a onClick={this.point.handleClickEdit} className="" >Edit</a>
				</li>
            </ul> 
		</span>
  }
/*
				Code to check if current user is the point Author
					{this.props.data.currentUser &&
					this.props.data.currentUser.url == this.point.authorURL &&
					<a onClick={this.handleClickEdit} className="editLink" >Edit</a>}					
*/
   
   
  render(){
    const point = this.point;
    console.log("rendering " + point.url)
	
	// Alt approach to animation, currently unused - JF
    //let classes = `point-card row-fluid ${this.evidenceTypeClass()} ${this.animClass()} toggleChildVisOnHover`;

	let classes = `point-card row-fluid toggleChildVisOnHover`;
	
	// TODO: I moved the Edit button inside the more Menu and now it's  no longer working. I tried building the MoreMenu as a local and as a global fuction ( this.moreMenu() } v <MoreMenu point={point}/> ) ). Lets pick which to use and trash the other code -JF
	// TODO: There's empty div that's wrapping everything here which isn't doing anything, but seems to be required for the return statement to work. Can/should we remove it? -JF
    return <div>
    { this.relevanceUI() }
      <div className={classes}>
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
              <Point point={point}/>
            </div>
          </div>
          {this.sources()}
          <div className="row-fluid">
            <div className="" >
              <span><EvidenceLink point={point} onSee={this.handleSeeEvidence} onHide={this.handleHideEvidence} expanded={this.expanded()}/></span>
              <span><AgreeDisagree point={point} parentPoint={this.props.parentPoint}/></span>
            </div>
          </div>
        </div>
		{this.image()}
      </div>
      <div className="row-fluid">
	    {this.evidence()} 
      </div>
    </div>;
  }
}

export function newPointCard(pointEdge, {index, expandedIndex, handleSeeEvidence, handleHideEvidence, parentPoint}) {
  let point = pointEdge.node;
  
  //Alt approach to animation, abandoned for now -JF
  //let classes = `pointCardGroup ${(expandedIndex===true) ? "animPink" : "noAnim"}`;
  
  let classes = `pointCardGroup`;  
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
    return <div className="pointCardGroup" key={index}></div>;
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

