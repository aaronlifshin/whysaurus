import React from 'react';
import { CharCount } from '../ys/components/CharCount'
import renderer from 'react-test-renderer'
import { Form, Text } from 'react-form';

test('CharCount component renders', () => {
  const component = renderer.create(
    <Form>
      {({values}) => (
        <form>
          <CharCount maxChars={200}
                     countedValue={values.title}
                     render={({charsLeft}) => (
            <div>
              <Text />
              <span id="charsLeft">{charsLeft}</span>
            </div>
            )}/>
        </form>
      )}
    </Form>
  )

  let tree = component.toJSON()
  expect(tree).toMatchSnapshot()

     //TODO: add enzyme and do real dom testing
});
