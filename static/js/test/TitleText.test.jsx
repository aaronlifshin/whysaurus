import React from 'react';
import  TitleText from '../ys/components/TitleText'
import renderer from 'react-test-renderer'
import { Form } from 'react-form';

test('TitleText component renders', () => {
  const component = renderer.create(
    <Form>
      {formApi => (<TitleText></TitleText>)}
    </Form>
  )

  let tree = component.toJSON()
  expect(tree).toMatchSnapshot()
});
