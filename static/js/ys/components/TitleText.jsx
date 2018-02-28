import React from 'react'
import * as validations from '../validations';
import * as formUtils from '../form_utils.js';
import { Form, Text, Field } from 'react-form';

const TitleFieldComponent = props => {
  console.log("title field")
  console.log(Form)
  console.log(Text)
  console.log(Field)
  // Use the form field and your custom input together to create your very own input!
  return <Field field={props.field}>
    { fieldApi => {

      // Remember to pull off everything you dont want ending up on the <input>
      // thats why we pull off onChange, onBlur, and field
      // Note, the ...rest is important because it allows you to pass any
      // additional fields to the internal <input>.
      const { updateCharCount, charsLeft, onChange, field, ...rest } = props

      const { value, error, warning, success, setValue, setTouched } = fieldApi

      return (
        <div className="titleField">
          <Text onChange={updateCharCount} field="title" {...rest}/>
          <p classes={charsLeft && charsLeft < 0 ? 'overMaxChars' : ''}>{charsLeft}</p>
             <p>{error}</p>
</div>
      )
    }}
    {fieldApi => {
      return <div>Foo</div>
    }}
  </Field>
};
export const TitleText = formUtils.withCharCount(TitleFieldComponent, validations.titleMaxCharacterCount)
