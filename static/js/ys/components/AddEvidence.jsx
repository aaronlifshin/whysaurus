import React from 'react'
import PropTypes from 'prop-types'
import { graphql, compose } from 'react-apollo';

import * as schema from '../schema';
import AddEvidenceForm from './AddEvidenceForm'
import Spinner from './Spinner'


class AddEvidence extends React.Component {
  state = {addingSupport: false, addingCounter: false }

  get point() {
    return this.props.point;
  }

  get uiType(){
    return this.props.type
  }

  get adding() {
    return this.state.addingSupport || this.state.addingCounter
  }

  handleClickAddEvidenceSupport = (e) => {
    if (this.props.user){
      this.setState({addingSupport: true, addingCounter: false})
    } else {
      $("#loginDialog").modal("show");
    }
  }

  handleClickAddEvidenceCounter = (e) => {
    if (this.props.user){
      this.setState({addingSupport: false, addingCounter: true})
    } else {
      $("#loginDialog").modal("show");
    }
  }

  handleClickCancel = (e) => {
    e.stopPropagation();
    this.setState({addingSupport: false, addingCounter: false})
    console.log("AddEvidenceCard : handleCancel")
  }

  handleClickSave = (evidenceType, values, e, formApi) => {
    let parentURL = this.point.url
    values.parentURL = parentURL
    values.linkType = evidenceType
    this.setState({saving: true})
    this.props.save(parentURL, evidenceType, values).
      then( res => {
        this.setState({saving: false,
                       addingSupport: false,
                       addingCounter: false})
      })
  }

  addExistingClaim = (evidenceType, claim) => {
    let parentURL = this.point.url
    this.setState({saving: true})
    this.props.linkExisting(parentURL, evidenceType, claim.url).
      then( res => {
        this.setState({saving: false,
                       addingSupport: false,
                       addingCounter: false})
      })
  }

  handleClickSaveSupport = (values, e, formApi) => {
    this.handleClickSave("supporting", values, e, formApi)
  }

  handleClickSaveCounter = (values, e, formApi) => {
    this.handleClickSave("counter", values, e, formApi)
  }

  renderAddEvidenceForm = (evidenceType) => {
    console.log("AddEvidenceCard : renderAddEvidenceForm : " + evidenceType)
    let progressFeedbackClasses = `progressStateFeedback ${evidenceType=="counter" && "counter"}`
    return <span>
      { this.state.saving ? <div className={progressFeedbackClasses}><Spinner />Saving...</div> :
      <span>
        <AddEvidenceForm point={this.point}
                         evidenceType={evidenceType}
                         addExistingClaim={this.addExistingClaim}
                         onSubmit={evidenceType=="supporting" ? this.handleClickSaveSupport : this.handleClickSaveCounter}
                         onCancel={this.handleClickCancel}/>
      </span>}
    </span>
  }

  addText = (evidenceType) => {
    switch (evidenceType){
      case "supporting":
        return "Add Evidence For"
      case "counter":
        return "Add Evidence Against"
      default:
        return "Add Evidence"
    }
  }

  numSupportingPlusCounter = () => {
    return (this.point.numSupporting + this.point.numCounter)
  }

  renderAddEvidenceFormBasedOnState = () => {
    if (this.state.addingSupport) {
      return <span>
        {this.renderAddEvidenceForm("supporting")}
      </span>
    } else if (this.state.addingCounter) {
      return <span>
        {this.renderAddEvidenceForm("counter")}
      </span>
    }
    else return (null)
  }

  renderAddEvidenceButton = (evidenceType) => {
    let classesButton = `buttonUX2 ${evidenceType=="counter" ? "buttonUX2Red" : ""} addEvidenceButton`
    let nameButton = `${evidenceType=="counter" ? "addCounterEvidenceButton" : "addSupportingEvidenceButton" }`
    let buttonLabel = this.addText(evidenceType)
    let classesAnchor = ""
    let onClick = evidenceType == 'supporting' ? this.handleClickAddEvidenceSupport : this.handleClickAddEvidenceCounter
    return <a className={classesAnchor} onClick={onClick}>
      <button type="button" name={nameButton} tabIndex="0" className={classesButton}>{buttonLabel}</button>
    </a>
  }

  renderSupportButton = () => this.renderAddEvidenceButton("supporting")

  renderCounterButton = () => this.renderAddEvidenceButton("counter")

  renderDualButtons = () => <span>
    {this.renderAddEvidenceButton("supporting")}
    {this.renderAddEvidenceButton("counter")}
  </span>


  renderEvidenceArrow = () => {
    let isCounter = (this.state.addingCounter || this.uiType == "COUNTER")
    let arrowGrpClass = `arrowEvidence ${(this.numSupportingPlusCounter() > 0) && "verticalOffsetForLongEvidenceArrow"}`
    let arrowHeadClass = `arrowHeadUp ${isCounter && "counter"}`
    let arrowStemClass = `arrowStemEvidence ${(this.numSupportingPlusCounter() == 0) && "arrowStemEvidenceShort" } ${isCounter && "counter"}`
    return <div className={arrowGrpClass}>
      <div className={arrowHeadClass}></div>
      <div className={arrowStemClass}></div>
    </div>
  }

  render() {
    let topDivClass = `addEvidenceUI`
    let controlsAreaClass = `addEvidenceControlsArea ${(this.numSupportingPlusCounter() == 0) && "addEvidenceControlsAreaNoEvidence"}`
    switch (this.uiType) {
    case "DUAL":
      return <div className={topDivClass}>
        { this.renderEvidenceArrow() }
        <span className={controlsAreaClass}>
          { (this.adding) ? this.renderAddEvidenceFormBasedOnState() : this.renderDualButtons() }
        </span>
      </div>
    case "SUPPORT":
      return <div className={topDivClass}>
        { this.renderEvidenceArrow() }
        <span className={controlsAreaClass}>
          { this.state.addingSupport ? this.renderAddEvidenceForm("supporting") : this.renderSupportButton() }
        </span>
      </div>
    case "COUNTER":
      return <div className={topDivClass}>
        { this.renderEvidenceArrow() }
        <span className={controlsAreaClass}>
          { this.state.addingCounter ? this.renderAddEvidenceForm("counter") : this.renderCounterButton() }
        </span>
      </div>
    default:
      console.log("AddEvidenceCard : render() : something's wrong!")
      return <div className={topDivClass}>
      </div>
    }
  }
}

function updateGetPointWithEdges(proxy, url, evidenceType, edges) {
  const data = proxy.readQuery({ query: schema.GetPoint, variables: {url: url} })
  data.point.relevantPoints.edges = data.point.relevantPoints.edges.concat(edges.edges)
  let points = data.point[evidenceType == "supporting" ? "supportingPoints" : "counterPoints"]
  points.edges = points.edges.concat(edges.edges)
  proxy.writeQuery({ query: schema.GetPoint,
                     variables: {url: url},
                     data: data })
}

export default compose(
  graphql(schema.AddEvidenceQuery, {
    props: ({mutate}) => ({
      save: (parentURL, evidenceType, values) => mutate({
        variables: values,
        update: (proxy, { data: { addEvidence: { newEdges } }}) =>
          updateGetPointWithEdges(proxy, parentURL, evidenceType, newEdges)
      })
    })
  }),
  graphql(schema.LinkPoint, {
    props: ({mutate}) => ({
      linkExisting: (parentURL, evidenceType, url) => mutate({
        variables: {parentURL: parentURL, linkType: evidenceType, url: url},
        update: (proxy, { data: { linkPoint: { newEdges } }}) =>
          updateGetPointWithEdges(proxy, parentURL, evidenceType, newEdges)
      })
    })
  }),
  graphql(schema.CurrentUserQuery, {
    props: ({ownProps, data: {loading, currentUser, refetch}}) => ({
      userLoading: loading,
      user: currentUser,
      refetchUser: refetch
    })
  })
)(AddEvidence)
