import React from 'react'
import PropTypes from 'prop-types'
import { graphql, compose } from 'react-apollo';

import * as schema from '../schema';
import AddEvidenceForm from './AddEvidenceForm'

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
    this.props.mutate({
      variables: values,
      update: (proxy, { data: { addEvidence: { newEdges } }}) => {
        const data = proxy.readQuery({ query: schema.GetPoint, variables: {url: parentURL} })
        data.point.relevantPoints.edges = data.point.relevantPoints.edges.concat(newEdges.edges)
        let points = data.point[evidenceType == "supporting" ? "supportingPoints" : "counterPoints"]
        points.edges = points.edges.concat(newEdges.edges)
        proxy.writeQuery({ query: schema.GetPoint,
                           variables: {url: parentURL},
                           data: data })
      }
    }).then( res => {
      this.setState({saving: false,
                     addingSupport: false,
                     addingCounter: false})
      console.log(res)
    })
  }

  handleClickSaveSupport = (values, e, formApi) => {
    this.handleClickSave("supporting", values, e, formApi)
  }

  handleClickSaveCounter = (values, e, formApi) => {
    this.handleClickSave("counter", values, e, formApi)
  }

  addExistingClaim = (claim) => {
    console.log("ADDING EXISTING CLAIM")
    console.log(claim)
    console.log("TODO: UNIMPLEMENTED")
  }

  renderAddEvidenceForm = (evidenceType) => {
    console.log("AddEvidenceCard : renderAddEvidenceForm : " + evidenceType)
    let groupClass = `${(this.numSupportingPlusCounter() > 0) && "verticalOffsetForLongEvidenceArrow"}`
    return <span className={groupClass}>
      { this.state.saving ? <span className="addEvidenceFormSaving"><img id="spinnerImage" className="spinnerPointSubmitButtonPosition" src="/static/img/ajax-loader.gif"/>Saving...</span> :
        <AddEvidenceForm evidenceType={evidenceType} onSubmit={evidenceType=="supporting" ? this.handleClickSaveSupport : this.handleClickSaveCounter} onCancel={this.handleClickCancel} addExistingClaim={this.addExistingClaim}/> }
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
    let aClass = `${(this.numSupportingPlusCounter() > 0) && "verticalOffsetForLongEvidenceArrow"}`
    let onClick = evidenceType == 'supporting' ? this.handleClickAddEvidenceSupport : this.handleClickAddEvidenceCounter
    return <a className={aClass} onClick={onClick}>
      <button type="button" name={nameButton} tabIndex="0" className={classesButton}>{buttonLabel}</button>
    </a>
  }

  renderSupportButton = () => this.renderAddEvidenceButton("supporting")

  renderCounterButton = () => this.renderAddEvidenceButton("counter")

  renderDualButtons = () => <span>
    {this.renderSupportButton()}
    {this.renderCounterButton()}
  </span>

  renderEvidenceArrow = (color) => {
    let arrowGrpClass = `arrowEvidence ${(this.numSupportingPlusCounter() > 0) && "verticalOffsetForLongEvidenceArrow"}`
    let arrowHeadClass = `arrowHeadUp ${color == "red" && "arrowHeadUpRed"}`
    let arrowStemClass = `arrowStemEvidence ${(this.numSupportingPlusCounter() == 0) && "arrowStemEvidenceShort" } ${color == "red" && "arrowStemRed"}`
    return <div className={arrowGrpClass}>
      <div className={arrowHeadClass}></div>
      <div className={arrowStemClass}></div>
    </div>
  }

  render() {
    let topDivClass = `addEvidenceUI`
    switch (this.uiType) {
    case "DUAL":
      return <div className={topDivClass}>
        { this.renderEvidenceArrow() }
        { (this.adding) ? this.renderAddEvidenceFormBasedOnState() : this.renderDualButtons() }
      </div>
    case "SUPPORT":
      return <div className={topDivClass}>
        { this.renderEvidenceArrow() }
        { this.state.addingSupport ? this.renderAddEvidenceForm("supporting") : this.renderSupportButton() }
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


export default compose(
  graphql(schema.AddEvidenceQuery),
  graphql(schema.CurrentUserQuery, {
    props: ({ownProps, data: {loading, currentUser, refetch}}) => ({
      userLoading: loading,
      user: currentUser,
      refetchUser: refetch
    })
  })
)(AddEvidence)
