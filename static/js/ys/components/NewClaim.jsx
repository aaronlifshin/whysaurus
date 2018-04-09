import React from 'react'
import * as validations from '../validations';
import { Form, Text } from 'react-form';
import TitleText from './TitleText'
import ReactFilestack from 'filestack-react';
import config from '../config'
import { client } from 'filestack-react';

const filestack = client.init(config.filestack.key)

function saveBigSummary(file) {
  const transformURL = filestack.transform(file.url, {resize: {width: 112, height: 112, fit: 'clip'}})
  const filename = "SummaryBig-" + file.key
  return filestack.storeURL(transformURL, {filename: filename, path: filename, access: 'public', location: 's3'})
}

function saveMediumSummary(file) {
  const transformURL = filestack.transform(file.url, {resize: {width: 54, height: 54, fit: 'clip'}})
  const filename = "SummaryMedium-" + file.key
  return filestack.storeURL(transformURL, {filename: filename, path: filename, access: 'public', location: 's3'})
}

function saveFullPoint(file) {
  const transformURL = filestack.transform(file.url, {resize: {width: 760, fit: 'clip'}})
  const filename = "FullPoint-" + file.key
  return filestack.storeURL(transformURL, {filename: filename, path: filename, access: 'public', location: 's3'})
}

// maxSize limited to 10mb for now
const filestackOptions = {
    accept: 'image/*',
    fromSources: ["imagesearch", "url", "local_file_system"],
    minFiles: 1,
    maxFiles: 1,
    maxSize:10485760,
    storeTo: {location: 's3', access: 'public'},
};

export default class NewClaim extends React.Component {
  constructor(props) {
    super(props)
  }

  state = {}

  render(){
    return <Form onSubmit={(values) => this.props.onSubmit({imageURL: this.state.imageURL, ...values})}
                 validate={values => ({title: validations.validateTitle(values.title)})}>
      { formApi => (
        <form onSubmit={formApi.submitForm} id="form1" className="addEvidenceForm">
          <TitleText id="title" className="titleTextField" placeholder='Make a claim, eg "Dogs can learn more tricks than cats."' />
          <ReactFilestack
            mode="pick"
            apikey={config.filestack.key}
            options={filestackOptions}
            buttonText="Upload Image"
            buttonClass="classname"
            onSuccess={(response) => {
              const file = response.filesUploaded[0]
              if (file) {
                console.log("saving and transforming:")
                console.log(file)
                this.setState({imageURL: file.key})

                Promise.all([saveBigSummary(file),
                             saveMediumSummary(file),
                             saveFullPoint(file)]).
                  then((result) => {
                    console.log("Saved transformed versions of image:")
                    console.log(result)
                  })
              } else {
                console.log("file upload seemed to fail, here's what I got:")
                console.log(response)
              }
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
