import React from 'react'
import PropTypes from 'prop-types'
import { Form, Text, Field } from 'react-form'
import CharCount from './CharCount'
import * as validations from '../validations'

const TitleText = props => (
  <Field field={props.field}>
    {fieldApi => {
      // field is here to strip that property out of `rest`
      const { field, ...rest } = props
      const { value, error, warning, success, setValue, setTouched } = fieldApi
      let classesCharCounterDefault = "charCounter "
      let classesErrorArea = `titleTextErrorArea ${(error && error.title) ? "titleTextErrorAreaContent" : "" }`
      return (
        <div className="claimTitleField">
          <CharCount countedValue={value.title || ""} maxChars={validations.titleMaxCharacterCount} render={({charsLeft}) => (
            <span>
              <span className={classesErrorArea}>{error && error.title}</span>
              <Text field="title" {...rest}/>
              <span className={classesCharCounterDefault + (charsLeft && charsLeft < 0 ? ' overMaxChars' : '')}>{charsLeft}</span>              
            </span>
          )}/>
        </div>
      )
    }}
  </Field>
);

TitleText.propTypes = {
}

export default TitleText
