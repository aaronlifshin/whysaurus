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

  render(){
    let submitClasses = `buttonUX2 addEvidenceFormButton ${this.props.evidenceType=="counter" ? "buttonUX2Red" : ""}`
    let {point, evidenceType, addExistingClaim} = this.props
    return <Form onSubmit={this.props.onSubmit}
                 validate={values => ({title: validations.validateTitle(values.title)})}>
      { ({submitForm, values: {title}}) => (
        <form onSubmit={submitForm} className="addEvidenceForm">
          <TitleText id="title" className="titleTextField"
                     autoComplete='off'
                     placeholder={this.generatePlaceholderText(evidenceType)}
                     point={point}
                     evidenceType={evidenceType}
                     addExistingClaim={addExistingClaim}/>
          <button type="submit" className={submitClasses}>Add</button>
          <button type="cancel" className="cancelButton cancelButtonAddEvidence" onClick={this.props.onCancel}>Cancel</button>
        </form>
      )}
    </Form>
  }
}

export default AddEvidenceForm
