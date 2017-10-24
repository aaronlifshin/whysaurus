import React from 'react';
import {PointCard, More} from './point';
import renderer from 'react-test-renderer';

test('PointCard', () => {
  const point = {};
  const component = renderer.create(
      <PointCard point={point}></PointCard>
  );
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
})


