import React from 'react';
import { NewClaim } from '../ys/components/NewClaim'
import renderer from 'react-test-renderer'


test('New Claim component renders', () => {
  const component = renderer.create(
    <NewClaim></NewClaim>,
  )

  let tree = component.toJSON()
  expect(tree).toMatchSnapshot()
});
