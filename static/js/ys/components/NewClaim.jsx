import React from 'react'
import * as validations from '../validations';
import { Form, Text } from 'react-form';
import TitleText from './TitleText'
import ReactFilestack from 'filestack-react';
import { config } from '../config'


export default class NewClaim extends React.Component {
  constructor(props) {
    super(props)
  }

  render(){
    return <Form onSubmit={this.props.onSubmit}
                 validate={values => ({title: validations.validateTitle(values.title)})}>
      { formApi => (
        <form onSubmit={formApi.submitForm} id="form1" className="addEvidenceForm">
          <TitleText id="title" className="titleTextField" placeholder='Make a claim, eg "Dogs can learn more tricks than cats."' />
          <ReactFilestack
            apikey={config.filestack.key}
            buttonText="Upload Image"
            buttonClass="classname"
            options={{storeTo: {location: 's3'}}}
            onSuccess={(response) => console.log(response)}
            />
          <button type="submit">Add</button>
          <button type="cancel" className="cancelButton cancelButtonAddEvidence" onClick={this.props.onCancel}>Cancel</button>
        </form>
      )}
    </Form>
  }
}
