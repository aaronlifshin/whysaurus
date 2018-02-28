import React from 'react';
import { TitleText } from '../ys/components/TitleText'
import renderer from 'react-test-renderer'


test('TitleText component renders', () => {
  const component = renderer.create(
    <TitleText></TitleText>,
  )

  let tree = component.toJSON()
  expect(tree).toMatchSnapshot()
});
