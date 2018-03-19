import React from 'react'
import PropTypes from 'prop-types'
import { Form, Text } from 'react-form';
import { graphql } from 'react-apollo';

import * as validations from '../validations';
import * as schema from '../schema';
import TitleText from './TitleText'
import ClaimSearch from './ClaimSearch'

// use onmousedown here to try to get in before blur hides the UI (see note in TitleText onBlur below)
// TODO: think about ways to make the "suggestion UI hide" condition be "clicking on anything that is not the text input or suggestion ui itself"
const ExistingClaimPicker = ({claims, onSelectClaim}) => <ul className="ExistingClaimList">
      {claims && claims.map((claim) => <li onMouseDown={e => onSelectClaim(claim, e)} key={claim.id}>
                            {claim.title}
                            </li>)}
      </ul>

class AddEvidenceForm extends React.Component {

  constructor(props) {
    super(props)
    this.invalidEvidenceURLs = new Set([props.point.url, ...props.currentSupportingClaims.map(claim => claim.url)])
  }

  static propTypes = {
    point: PropTypes.object.isRequired,
    currentSupportingClaims: PropTypes.array.isRequired,
    addExistingClaim: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired,
    onCancel: PropTypes.func.isRequired
  }

  state = {titleTextFocused: false}

  selectExistingClaim = (claim) =>
    this.props.addExistingClaim(this.props.evidenceType, claim)

  filterEvidenceCandidates = (claims) =>
    claims.filter(claim => !this.invalidEvidenceURLs.has(claim.url))

  existingClaimPicker = (titleValue, searchResults, searching) => {
      if (titleValue && (titleValue != '')){
        if (searching) {
          return <div className="">Searching...</div>
        } else {
          return <ExistingClaimPicker claims={this.filterEvidenceCandidates(searchResults)} onSelectClaim={this.selectExistingClaim}/>
        }
      } else if (this.props.user) {
        return <ExistingClaimPicker claims={this.filterEvidenceCandidates(this.props.user.recentlyViewed)} onSelectClaim={this.selectExistingClaim}/>
      }
  }

  // if (this.state.titleTextFocused) {
  existingClaimPickerDropdown = (titleValue, searchResults, searching) => {
    if (this.state.titleTextFocused) {
      return <div className="existingClaimPickerDropdown">
        <div className="existingClaimPickerHeading">Existing Claims:</div>
        {this.existingClaimPicker(titleValue, searchResults, searching)}
      </div>
    }
  }

  // TODO: add multiple options for each type and randomize to give it some fun magic!
  generatePlaceholderText(evidenceType) {
    let placeholderSupport = `Make a claim, eg "Dogs can learn more tricks than cats."`
    let placeholderCounter= `Make a claim, eg "Cats are funnier than dogs."`
    if (this.props.evidenceType=="counter") {
        return placeholderCounter
    } else {
        return placeholderSupport
    }
  }

  render(){
    const {userLoading, user} = this.props
    let submitClasses = `buttonUX2 addEvidenceFormButton ${this.props.evidenceType=="counter" ? "buttonUX2Red" : ""}`
    return <Form onSubmit={this.props.onSubmit}
                 validate={values => ({title: validations.validateTitle(values.title)})}>
      { ({submitForm, values: {title}}) => (
        <ClaimSearch
          query={title}
          render={({results, searching}) =>
                  <form onSubmit={submitForm} className="addEvidenceForm">
                      <TitleText id="title" className="titleTextField"
                                   autoComplete='off'
                                   placeholder={this.generatePlaceholderText(this.props.evidenceType)}
                                   onFocus={() => {this.setState({titleTextFocused: true})}}
                                   // use the setTimeout here to allow the mousedown event in existingclaimpicker to fire consistently
                                   // right now this fires before the onClick in ExistingClaimPIcker and hides that UI before the click event can be fired
                                   // TODO: think about ways to make the "suggestion UI hide" condition be "clicking on anything that is not the text input or suggestion ui itself"
                                   onBlur={() => {setTimeout(() => this.setState({titleTextFocused: false}), 100)}}
                          />
                      {this.existingClaimPickerDropdown(title, results, searching)}
                      <button type="submit" className={submitClasses}>Add</button>
                      <button type="cancel" className="cancelButton cancelButtonAddEvidence" onClick={this.props.onCancel}>Cancel</button>
                    </form>
                  }/>
      )}
    </Form>
  }
}

export default graphql(schema.CurrentUserQuery, {
  props: ({ownProps, data: {loading, currentUser, refetch}}) => ({
    userLoading: loading,
    user: currentUser,
    refetchUser: refetch
  })
})(AddEvidenceForm)
