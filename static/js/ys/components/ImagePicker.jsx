import React from 'react'
import PropTypes from 'prop-types'
import ReactFilestack from 'filestack-react'
import { Text, Field } from 'react-form'
import { client } from 'filestack-react';
import config from '../config'

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
    storeTo: {location: 's3', access: 'public'}
};


export default class ImagePicker extends React.Component {
  static propTypes = {
    onUploaded: PropTypes.func,
    onTransformed: PropTypes.func
  }

  render(){
    const {onUploaded, onTransformed, ...rest} = this.props
    return <Field {...rest}>
      { ({value, setValue}) =>
        <ReactFilestack
        mode="pick"
        apikey={config.filestack.key}
        options={filestackOptions}
        buttonText="Choose Image"
        buttonClass="buttonUX2 imagePickerButton"
        onSuccess={(response) => {
          const file = response.filesUploaded[0]
          if (file) {
            setValue(file.key)
            onUploaded && onUploaded(file)
            Promise.all([saveBigSummary(file),
                         saveMediumSummary(file),
                         saveFullPoint(file)]).
            then(onTransformed)
          } else {
            console.log("file upload seemed to fail, here's what I got:")
            console.log(response)
          }
        }}/>
    }
    </Field>
  }
}
