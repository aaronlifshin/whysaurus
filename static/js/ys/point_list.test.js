import React from 'react';
import {PointListWithPoints, getPoints, PostListWithPoints, edgeRows, evidenceEdges, evidenceRows} from './point_list';
import renderer from 'react-test-renderer';
import { MockedProvider } from 'react-apollo/test-utils';
import { List, Map } from 'immutable'


let foo = {title: "Foo"}
let bar = {title: "Bar"}
let cats = {title: "Cats"}
let fooBarCats = [{node: {title: "Foo Bar Cats",
			  supportingPoints: {edges: [{node: foo}]},
			  counterPoints: {edges: [{node: bar}, {node: cats}]}}}]

test('evidenceEdges', () => {
  expect(List([...evidenceEdges([])])).toBe(List([]));
  expect(List([...evidenceEdges([{node: {title: "Foo"}}])])).
    toEqual(List([List([]), List([])]));
  expect(List([...evidenceEdges(fooBarCats)])).
    toEqual(List([List([{node: foo}]),
		  List([{node: bar}, {node: cats}])
		 ]));
});

test('evidenceRows', () => {
  expect(evidenceRows(fooBarCats)).
    toEqual(List([[{node: foo}, {node: bar}],
		  [undefined, {node: cats}]
		 ]));
});

test('edgeRows', () => {
  expect(List([...edgeRows([])])).toBe(List([]))
  expect(List([...edgeRows([{node: {title: "Bacon"}}])])).
    toEqual(List([List([Map({node: {title: "Bacon"}, depth: 0})])]))
  expect(List([...edgeRows(fooBarCats)])).
    toEqual(List([List([Map(fooBarCats[0]).set('depth', 0)]),
  		  List([Map({node: foo, depth: 1}), Map({node: bar, depth: 1})]),
  		  List([Map({depth: 1}), Map({node: cats, depth: 1})])
  		 ]))
});


// test('PointCard', () => {
//   const point = {};

//   const variables = { cache: false };
//   const query = getPoints;
//   const mockedData = {
//     points: {
//       edges: [
// 	{
// 	  node: {title: "Foo"}
// 	}
//       ]
//     }
//   };
//   const component = renderer.create(
//       <MockedProvider mocks={[
//         { request: { query, variables }, result: { data: mockedData } }
//       ]}>
//       <PostListWithPoints></PostListWithPoints>
//       </MockedProvider>
//   );
//   let tree = component.toJSON();
//   expect(tree).toMatchSnapshot();
//   console.log(tree)
// })


