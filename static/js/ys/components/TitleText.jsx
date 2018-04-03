import React from 'react'
import { graphql } from 'react-apollo';
import { Form, Text, TextArea, Field } from 'react-form'
import PropTypes from 'prop-types'

import * as validations from '../validations'
import * as schema from '../schema';

import CharCount from './CharCount'
import ClaimSuggestor from './ClaimSuggestor'

// use onmousedown here to try to get in before blur hides the UI (see note in TitleText onBlur below)
// TODO: think about ways to make the "suggestion UI hide" condition be "clicking on anything that is not the text input or suggestion ui itself"
const ExistingClaimPicker = ({claims, onSelectClaim}) => <ul className="ExistingClaimList">
      {claims && claims.map((claim) => <li onMouseDown={e => onSelectClaim(claim, e)} key={claim.id}>
                            {claim.title}
                            </li>)}
</ul>

class TitleText extends React.Component {
  static propTypes = {
    point: PropTypes.object,
    evidenceType: PropTypes.string,
    addExistingClaim: PropTypes.func
  }

  constructor(props) {
    super(props)
    this.state = {titleTextFocused: false}
  }

  selectExistingClaim = (claim) =>
    this.props.addExistingClaim(this.props.evidenceType, claim)

  feedbackArea = (error, suggestions, searching) => {
    let errorClasses = `titleTextErrorArea ${error && "titleTextErrorAreaContent"}`
    return <div className="existingClaimPickerDropdown">
      <span className={errorClasses}>{error}</span>
      <div className="existingClaimPickerHeading">Existing Claims:</div>
      <ExistingClaimPicker claims={suggestions} onSelectClaim={this.selectExistingClaim}/>
    </div>
  }

  render(){
    // `field` is here to strip out the field prop since we set it manually
    const { field, point, evidenceType, addExistingClaim, ...restOfProps } = this.props
    // add focused prop here to make Field.shouldComponentUpdate return true when focus changes
    return <Field field="title" focused={this.state.titleTextFocused}>
      {fieldApi => {
        const { value, error, warning, success, setValue, setTouched } = fieldApi
        let title = value
        let classesCharCounterDefault = "charCounter "
        return (
          <div className="claimTitleField">
            <ClaimSuggestor
              query={title}
              point={point}
              evidenceType={evidenceType}
              render={({suggestions, searching}) => (
                <CharCount countedValue={title || ""} maxChars={validations.titleMaxCharacterCount} render={({charsLeft}) => (
                  <span>
                    <Text field="title" {...restOfProps}
                          onFocus={() => {this.setState({titleTextFocused: true})
                      }}
                          // use the setTimeout here to allow the mousedown event in existingclaimpicker to fire consistently
                          // right now this fires before the onClick in ExistingClaimPIcker and hides that UI before the click event can be fired
                          // TODO: think about ways to make the "suggestion UI hide" condition be "clicking on anything that is not the text input or suggestion ui itself"
                      onBlur={() => {setTimeout(() => this.setState({titleTextFocused: false}), 100)}}
                      />
                      {this.state.titleTextFocused && this.feedbackArea(error, suggestions, searching)}
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

export default TitleText
