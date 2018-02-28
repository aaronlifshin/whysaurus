import React from 'react'
import * as validations from '../validations';
import * as formUtils from '../form_utils.js';
import { Form, Text } from 'react-form';


export class NewClaim extends React.Component {
  constructor(props) {
    super(props)
  }

  render(){
    return <Form onSubmit={this.props.onSubmit}
                 validateError={values => ({title: validations.validateTitle(values.title)})}
                 dontValidateOnMount={true}>
      { formApi => (
        <form onSubmit={formApi.submitForm} id="form1" className="addEvidenceForm">
          <Text onChange={this.props.updateCharCount} field="title" id="title" className="addEvidenceFormTextField" placeholder='Make a claim, eg "Dogs can learn more tricks than cats."' />
          <p>{formApi.errors.title}</p>
          <p classes={props.charsLeft && props.charsLeft < 0 ? 'overMaxChars' : ''}>{props.charsLeft}</p>
          <button type="submit" className={submitClasses}>Add</button>
          <button type="cancel" className="cancelButton cancelButtonAddEvidence" onClick={props.onCancel}>Cancel</button>
        </form>
      )}
    </Form>
  }
}
