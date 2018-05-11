import React from 'react'
import { graphql, compose } from 'react-apollo';
import { Form, Text } from 'react-form';

import { CloseLinkX } from './common'
import * as validations from '../validations';
import * as schema from '../schema';

class EditSourceComponent extends React.Component {

  state = {saving: false}

  deleteSource = (id) => {
    this.setState({saving: true})
    this.props.delete(this.props.point.id, id)
  }

  render() {
    if (this.state.saving) {
      return "saving..."
    } else {
      const {id, url, name} = this.props.source
      return <div className="source">
        <span onClick={() => this.deleteSource(id)}>X</span>
        <a tabIndex="-1" target="_blank" href={url}>{name}</a>
        </div>
    }
  }
}

const EditSource = compose(
  graphql(schema.DeleteSource, {
    props: ({mutate}) => ({
      delete: (pointID, id) => mutate({
        variables: {pointID, id}
      })
    })
  }),
)(EditSourceComponent)

class EditSourcesComponent extends React.Component {

  state = {saving: false}

  onSubmit = ({name, url}) => {
    this.setState({saving: true})
    this.props.add(this.props.point.id, name, url).then(() => this.setState({saving: false}))
  }

  render(){
    const sources = this.props.point.sources
    let editSourcesLabel = `${sources ? "Edit Sources" : "Add Sources"}`
    return <div className="row-fluid claimEditArea pointCardPaddingH editSources ">
      <span className="claimEditAreaHeading">
      <span className="heading">{editSourcesLabel}</span>
      <span className="editAreaClose"><a onClick={this.props.onCancel}><CloseLinkX/></a></span>
      </span>
      {sources && sources.map((source, i) => <EditSource key={i} point={this.props.point} source={source}/>)}
      <Form onSubmit={this.onSubmit}
            validate={values => ({name: validations.validateSourceName(values.name),
                                  url: validations.validateSourceURL(values.url)})}>
      {formApi => <form onSubmit={formApi.submitForm}>
         <Text field="url" placeholder="URL"/>
         <Text field="name" placeholder="Title"/>
         {this.state.saving ? "saving..." : <button disabled={false} className="buttonUX2 createClaimFormButton" type="submit">Add Source</button>}

       </form>}
      </Form>
    </div>
  }
}

export default compose(
  graphql(schema.AddSource, {
    props: ({mutate}) => ({
      add: (pointID, name, url) => mutate({
        variables: {pointID, name, url}
      })
    })
  })
)(EditSourcesComponent)
