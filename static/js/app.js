import React from 'react';
import ReactDOM from 'react-dom';
import { ApolloClient } from 'apollo-client';
import { gql } from 'graphql-tag';
import { ApolloProvider, graphql } from 'react-apollo';
import { HttpLink } from 'apollo-link-http';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { BrowserRouter, Switch, Route, Redirect } from 'react-router-dom'

import {PointListWithPoint} from './ys/components/PointList';
import {HomePage} from './ys/home';
import {ExpandedIndexProvider} from './ys/components/ExpandedIndex'

const client = new ApolloClient({
  link: new HttpLink({ uri: '/graphql', credentials: 'same-origin' }),
  cache: new InMemoryCache()
});

const homeURL = "/"

class PointPage extends React.Component {

  state = {goHome: false}

  render(){
    if (this.state.goHome){
      return <Redirect to={homeURL}/>
    } else {
      return <div className="row pointPageContainer infiniteWidth">
        <div id="infiniteOrFiniteWidth" className="">
          <PointListWithPoint url={this.props.match.params.url} onDelete={() => {this.setState({goHome: true})}}/>
        </div>
      </div>
    }
  }
}


class App extends React.Component {
  render() {
    return (
        <Switch>
        <Route exact path={homeURL} component={HomePage} />
        <Route exact path="/claim/:url" component={PointPage} />
        </Switch>
    )
  }
}

ReactDOM.render(
  <BrowserRouter>
    <ApolloProvider client={client}>
      <ExpandedIndexProvider>
        <App/>
      </ExpandedIndexProvider>
    </ApolloProvider>
  </BrowserRouter>,
  document.getElementById('root')
);
