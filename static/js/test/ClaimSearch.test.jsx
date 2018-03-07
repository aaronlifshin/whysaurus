import React from 'react';
import ClaimSearch from '../ys/components/ClaimSearch'
import renderer from 'react-test-renderer'

test('ClaimSearch component renders', () => {
  const component = renderer.create(
    <ClaimSearch query="hams"
                 render={({results, searching}) => {
                   if (searching){
                     return <div>Searching...</div>
                   } else {
                     return JSON.stringify(result)
                   }
      }}/>
  )

  let tree = component.toJSON()
  expect(tree).toMatchSnapshot()
  //TODO: figure out how to mock data from the apollo client here
  //TODO: add enzyme and do real dom testing
});
