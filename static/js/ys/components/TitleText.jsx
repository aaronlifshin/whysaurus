import React from 'react'
import { graphql } from 'react-apollo';
import { Form, Text, TextArea, Field } from 'react-form'
import PropTypes from 'prop-types'

import * as validations from '../validations'
import * as schema from '../schema';

import CharCount from './CharCount'
import ClaimSearch from './ClaimSearch'

// use onmousedown here to try to get in before blur hides the UI (see note in TitleText onBlur below)
// TODO: think about ways to make the "suggestion UI hide" condition be "clicking on anything that is not the text input or suggestion ui itself"
const ExistingClaimPicker = ({claims, onSelectClaim}) => <ul className="ExistingClaimList">
      {claims && claims.map((claim) => <li onMouseDown={e => onSelectClaim(claim, e)} key={claim.id}>
                            {claim.title}
                            </li>)}
</ul>

class TitleText extends React.Component {

  constructor(props) {
    super(props)
    this.invalidEvidenceURLs = new Set([props.point.url, ...this.evidence().map(claim => claim.url)])
  }

  static propTypes = {
    point: PropTypes.object,
    evidenceType: PropTypes.string,
    currentEvidence: PropTypes.array,
    addExistingClaim: PropTypes.func
  }

  state = {titleTextFocused: false}

  selectExistingClaim = (claim) =>
    this.props.addExistingClaim(this.props.evidenceType, claim)

  evidence = () => {
    let connections = this.props.point[this.props.evidenceType == "supporting" ? "supportingPoints" : "counterPoints"]
    return connections ? connections.edges.map(edge => edge.node) : []
  }

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

  existingClaimPickerDropdown = (titleValue, searchResults, searching) => {
    if (this.state.titleTextFocused) {
      return <div className="existingClaimPickerDropdown">
        <div className="existingClaimPickerHeading">Existing Claims:</div>
        {this.existingClaimPicker(titleValue, searchResults, searching)}
      </div>
    }
  }

  render(){
    const { field, ...restOfProps } = this.props
    return <Field field={field}>
      {fieldApi => {
        const { value: { title }, error, warning, success, setValue, setTouched } = fieldApi
        let classesCharCounterDefault = "charCounter "
        let classesErrorArea = `titleTextErrorArea ${(error && error.title) ? "titleTextErrorAreaContent" : "" }`
        return (
          <div className="claimTitleField">
            <ClaimSearch
              query={title}
              render={({results, searching}) => (
                <CharCount countedValue={title || ""} maxChars={validations.titleMaxCharacterCount} render={({charsLeft}) => (
                  <span>
                    <span className={classesErrorArea}>{error && error.title}</span>
                    <Text field="title" {...restOfProps}
                          onFocus={() => {this.setState({titleTextFocused: true})}}
                          // use the setTimeout here to allow the mousedown event in existingclaimpicker to fire consistently
                          // right now this fires before the onClick in ExistingClaimPIcker and hides that UI before the click event can be fired
                          // TODO: think about ways to make the "suggestion UI hide" condition be "clicking on anything that is not the text input or suggestion ui itself"
                          onBlur={() => {setTimeout(() => this.setState({titleTextFocused: false}), 100)}}
                      />
                    {this.existingClaimPickerDropdown(title, results, searching)}
                    <span className={classesCharCounterDefault + (charsLeft && charsLeft < 0 ? ' overMaxChars' : '')}>{charsLeft}</span>
                  </span>
                )}/>
              )}/>
          </div>
        )
      }}
    </Field>
  }
}

export default graphql(schema.CurrentUserQuery, {
  props: ({ownProps, data: {loading, currentUser, refetch}}) => ({
    userLoading: loading,
    user: currentUser,
    refetchUser: refetch
  })
})(TitleText)
