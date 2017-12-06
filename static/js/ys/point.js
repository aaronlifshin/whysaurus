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
  upVotes,
  downVotes,
  numSupporting,
  numCounter,
  numComments,
  supportedCount,
  sources {url, name},
  rootURLsafe
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
  return <span><a className="byline" href={"/user/" + props.point.authorURL}>@{props.point.authorName}</a></span>
}

function CommentCount(props){
  return <span><i className="fa fa-comment-o"></i>{props.point.numComments}</span>
}

function ShareIcon(props){
  return <i className="fa fa-share-alt"></i>;
}

function SupportingCount(props){
  return <span><i className="fa fa-level-up"></i>{props.point.supportedCount}</span>
}


// thanks, https://stackoverflow.com/questions/29981236/how-do-you-hover-in-reactjs-onmouseleave-not-registered-during-fast-hover-ove
const Hover = ({ onHover, children }) => (
    <span className="hover">
      <span className="hover__no-hover">{children}</span>
      <span className="hover__hover">{onHover}</span>
    </span>
)

const VoteStats = ({point}) => (
    <div className="vote-stats">
      <p>Agreed: {point.upVotes}</p>
      <p>Disagreed: {point.downVotes}</p>
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
    this.props.mutate({
      variables: values
    })
      .then( res => {
        console.log(res)
      });
    this.setState({editing: false})
  }


  titleUI() {
    if (this.state.editing) {
      return <div>
        <EditTitleForm onSubmit={this.handleClickSave}/>
        </div>
      return <b>editing</b>
    } else {
      return <div>
        <a href={this.point.url}>{this.point.title}</a>
        <a onClick={this.handleClickEdit}>edit</a>
        </div>
    }
  }

  render(){
    const score = (this.point.upVotes || 0) - (this.point.downVotes || 0)
    return <span>
      {this.titleUI()}
      <Hover onHover={<VoteStats point={this.point}/>}>
      <b>{score > 0 && "+"}{score}</b>
      </Hover>
      </span>
  }
}

const Point = graphql(EditPointQuery)(PointComponent)

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
    return <ul>
      {this.point.sources && this.point.sources.map(({name, url}, i) =>
        <li key={i}><a href={url}>{name}</a></li>
      )}
    </ul>
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

  render(){
    if (this.hasEvidence()) {
      if (this.props.expanded) {
        return <a onClick={this.handleClickHide}>Hide Evidence</a>
      } else {
        return <a onClick={this.handleClickSee}>See Evidence</a>
      }
    } else {
      return <span>No Evidence</span>
    }
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
    this.props.mutate({ 
      variables: values
    })
      .then( res => {
        console.log(res)
      });
    this.setState({adding: false})
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
      return <div>
        <AddEvidenceForm onSubmit={this.handleClickSave}/>
      </div>
    } else {
      return <a onClick={this.handleClickAddEvidence}>{this.addText}</a>
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
mutation Vote($url: String!, $vote: Int!) {
  vote(url: $url, vote: $vote) {
    point {
      id
      upVotes
      downVotes
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
        variables: {url: this.props.point.url, vote: 1}
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
        variables: {url: this.props.point.url, vote: -1}
      }).then( res => {
        console.log(res)
      });
    } else {
      $("#loginDialog").modal("show");
    }
  }

  render(){
    return <span>
      <a onClick={this.handleClickAgree}>Agree</a>
      <a onClick={this.handleClickDisagree}>Disagree</a>
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

  handleClick0() {
    console.log("0");
    if (this.props.data.currentUser){
      this.props.mutate({
        variables: {linkType: this.props.linkType, url: this.props.point.url, parentRootURLsafe: this.parentRootURLsafe, rootURLsafe: this.rootURLsafe, vote: 0}
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
        variables: {linkType: this.props.linkType, url: this.props.point.url, parentRootURLsafe: this.parentRootURLsafe, rootURLsafe: this.rootURLsafe, vote: 33}
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
        variables: {linkType: this.props.linkType, url: this.props.point.url, parentRootURLsafe: this.parentRootURLsafe, rootURLsafe: this.rootURLsafe, vote: 66}
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
        variables: {linkType: this.props.linkType, url: this.props.point.url, parentRootURLsafe: this.parentRootURLsafe, rootURLsafe: this.rootURLsafe, vote: 100}
      }).then( res => {
        console.log(res)
      });
    } else {
      $("#loginDialog").modal("show");
    }
  }

  render(){
    return <span>
      <a onClick={this.handleClick0}>0</a>
      <a onClick={this.handleClick33}>33</a>
      <a onClick={this.handleClick66}>66</a>
      <a onClick={this.handleClick100}>100</a>
      </span>
    }
}

const RelevanceVote = compose(
  graphql(RelevanceVoteQuery),
  graphql(CurrentUserQuery),
)(RelevanceComponent)


function More(){
  return <span>More</span>
}

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
    return this.props.link && this.props.link.type
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
      return <Hover onHover={<RelevanceVote point={this.point} parentPoint={this.props.parentPoint} linkType={this.evidenceType}/>}>
               <b>rel: {this.relevance}</b>
             </Hover>
        
      return <RelevanceVote point={this.point} parentPoint={this.props.parentPoint} linkType={this.evidenceType}/>
    }
  }

  supportingPoints(){
    if (this.expanded() && this.point.supportingPoints) {
      return <div className="support">
        {this.point.supportingPoints.edges.map((edge, i) => this.renderSubPointCard(this.point, edge, i))}
        <AddEvidence point={this.point} type={EvidenceType.SUPPORT}/>
      </div>
    }
  }

  counterPoints(){
    if (this.expanded() && this.point.counterPoints){
      return <div className="counter">
        {this.point.counterPoints.edges.map((edge, i) => this.renderSubPointCard(this.point, edge, i))}
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

  render(){
    const point = this.point;
    console.log("rendering " + point.url)
    let classes = `point-card row-fluid ${this.evidenceTypeClass()}`;
    return <div>
    { this.relevanceUI() }
      <div className={classes}>
        <div className="span9">
          <div className="row-fluid">
            <div className="span12">
              <Byline point={point}/>
              <CommentCount point={point}/>t
              <ShareIcon point={point}/>
              <SupportingCount point={point}/>
            </div>
          </div>
          <div className="row-fluid">
            <div className="pointText span12">
              <Point point={point}/>
            </div>
          </div>
          {this.sources()}
          <div className="row-fluid">
            <div className="span12">
              <EvidenceLink point={point} onSee={this.handleSeeEvidence} onHide={this.handleHideEvidence} expanded={this.expanded()}/>
              <AgreeDisagree point={point}/>
              <More point={point}/>
            </div>
          </div>
        </div>
        <div className="span3"><img src={point.imageURL} alt="an image"></img></div>
      </div>
      <div className="row-fluid">
        {this.supportingPoints()}
        {this.counterPoints()}
      </div>
    </div>;
  }
}

export function newPointCard(pointEdge, {index, expandedIndex, handleSeeEvidence, handleHideEvidence, parentPoint}) {
  let point = pointEdge.node;
  if (point) {
    return <div className="pointCardGroup" key={point.url}>
      <ExpandedPointCard point={point}
    url={point.url}
    expandedIndex={expandedIndex}
    expanded={true}
    link={pointEdge.link}
    handleSeeEvidence={handleSeeEvidence}
    handleHideEvidence={handleHideEvidence}
    parentPoint={parentPoint}/>
      </div>;
    // TODO: figure out how to render regular point cards pre-expansion.
    //       currently failing to expand on the first click for unknown reasons.
    // if (!expandedIndex[point.url]) {
    //   console.log("point card for " + point.url);
    //   console.log(expandedIndex)
    //   return <div className="span5" key={point.url}>
    //     <PointCard point={point}
    //       expandedIndex={expandedIndex}
    //       expanded={false}
    //       evidenceType={pointEdge.evidenceType}
    //       handleSeeEvidence={handleSeeEvidence}
    //       handleHideEvidence={handleHideEvidence}/>
    //     </div>
    // } else {
    //   console.log("expanded point card for " + point.url);
    //   console.log(expandedIndex)
    //   return <div className="span5" key={point.url}>
    //     <ExpandedPointCard point={point}
    //         url={point.url}
    //         expandedIndex={expandedIndex}
    //         expanded={true}
    //         evidenceType={pointEdge.evidenceType}
    //         handleSeeEvidence={handleSeeEvidence}
    //         handleHideEvidence={handleHideEvidence}/>
    //     </div>;
    // }
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

