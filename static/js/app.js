import React from 'react';
import ReactDOM from 'react-dom';
import { ApolloClient } from 'apollo-client';
import { gql } from 'graphql-tag';
import { ApolloProvider, graphql } from 'react-apollo';
import { HttpLink } from 'apollo-link-http';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { BrowserRouter, Switch, Route, Redirect } from 'react-router-dom'
import { Provider as AlertProvider } from 'react-alert'
import AlertTemplate from 'react-alert-template-basic'

import {PointListWithPoint} from './ys/components/PointList';
import History from './ys/components/History';
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

const alertOptions = {
  position: 'bottom center',
  timeout: 5000,
  offset: '30px',
  transition: 'scale'
}

class HistoryPage extends React.Component {

  render(){
      return <div className="row pointPageContainer infiniteWidth">
        <div id="content" className="fullPageText">
          <History url={this.props.match.params.url}/>
        </div>
       </div>
  }
}


class App extends React.Component {
  render() {
    return (
        <Switch>
        <Route exact path={homeURL} component={HomePage} />
        <Route exact path="/claim/:url" component={PointPage} />
        <Route exact path="/history/:url" component={HistoryPage} />
        </Switch>
    )
  }
}

ReactDOM.render(
  <BrowserRouter>
    <ApolloProvider client={client}>
      <ExpandedIndexProvider>
        <AlertProvider template={AlertTemplate} {...alertOptions}>
          <App/>
        </AlertProvider>
      </ExpandedIndexProvider>
    </ApolloProvider>
  </BrowserRouter>,
  document.getElementById('root')
);
