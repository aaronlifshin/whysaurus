import React from 'react'
import PropTypes from 'prop-types'
import { Form, Text } from 'react-form';
import { graphql } from 'react-apollo';

import * as validations from '../validations';
import * as schema from '../schema';
import TitleText from './TitleText'
import ClaimSearch from './ClaimSearch'

class AddEvidenceForm extends React.Component {

  static propTypes = {
    point: PropTypes.object.isRequired,
    evidenceType: PropTypes.string.isRequired,
    addExistingClaim: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired,
    onCancel: PropTypes.func.isRequired
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
  
  // TO DO: there is bug around validationFailures - its returning 0 when it shouldn't be
  //   for now, adding the condition (title.length > validations.titleMaxCharacterCount) to make the button disable when it should
  //   but really we should fix the bug
  //   see PR here: https://github.com/aaronlifshin/whysaurus/pull/82#pullrequestreview-111369929
  render(){
    let submitClasses = `buttonUX2 createClaimFormButton ${this.props.evidenceType=="counter" ? "buttonUX2Red" : ""}`
    let {point, evidenceType, addExistingClaim} = this.props
    return <Form onSubmit={this.props.onSubmit}
                 validate={values => ({title: validations.validateTitle(values.title)})}>
      { ({submitForm, values: {title}, validationFailures}) => (
        <form onSubmit={submitForm} className="addEvidenceForm">
          <div className="claimCreationFormFieldBlock">
            <TitleText id="title" className="titleTextField"
                     autoComplete='off'
                     placeholder={this.generatePlaceholderText(evidenceType)}
                     suggestExistingClaims={true}
                     point={point}
                     evidenceType={evidenceType}
                     addExistingClaim={addExistingClaim}
                     onSubmit={submitForm}/>
          </div>
          <div className="claimCreationFormButtonBlock">
            <button type="submit" className={submitClasses} disabled={(!title || (title == "")) ||  (title.length > validations.titleMaxCharacterCount) || (validationFailures > 0)}>Add</button>
            <button type="cancel" className="cancelButton cancelButtonAddEvidence" onClick={this.props.onCancel}>Cancel</button>
          </div>
        </form>
      )}
    </Form>
  }
}

export default AddEvidenceForm
