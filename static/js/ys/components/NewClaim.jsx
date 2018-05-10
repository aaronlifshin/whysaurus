import React from 'react'
import * as validations from '../validations';
import { Form, Text } from 'react-form';
import TitleText from './TitleText'
import ReactFilestack from 'filestack-react';
import config from '../config'
import ImagePicker from './ImagePicker';

export default class NewClaim extends React.Component {
  state = {}

  render(){
    return <Form onSubmit={(values) => this.props.onSubmit({imageURL: this.state.imageURL, ...values})}
                 validate={values => ({title: validations.validateTitle(values.title)})}>
      { formApi => (
        <form onSubmit={formApi.submitForm} id="form1" className="addEvidenceForm">
          <TitleText id="title" className="titleTextField" placeholder='Make a claim, eg "Dogs can learn more tricks than cats."' />
          <ImagePicker
            onUploaded={(file) => {
              this.setState({imageURL: file.key})
            }}
            onTransformed={(result) => {
              console.log("Saved transformed versions of image:")
              console.log(result)
            }}
            />
            {this.state.imageURL && <img src={config.cdn.baseURL + this.state.imageURL}/>}
          <button type="submit">Add</button>
          <button type="cancel" className="cancelButton cancelButtonAddEvidence" onClick={this.props.onCancel}>Cancel</button>
        </form>
      )}
    </Form>
  }
}
