import React from 'react';
import ReactDOM from 'react-dom';
import { ApolloClient } from 'apollo-client';
import { gql } from 'graphql-tag';
import { ApolloProvider, graphql } from 'react-apollo';
import { HttpLink } from 'apollo-link-http';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { BrowserRouter, Switch, Route, Redirect } from 'react-router-dom'
import { Provider as AlertProvider } from 'react-alert'

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

const alertStyle = {
  backgroundColor: '#151515',
  color: 'white',
  padding: '10px',
  textTransform: 'uppercase',
  borderRadius: '3px',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  boxShadow: '0px 2px 2px 2px rgba(0, 0, 0, 0.03)',
  fontFamily: 'Arial',
  // width: '300px',
  boxSizing: 'border-box'
}

const buttonStyle = {
  marginLeft: '20px',
  border: 'none',
  backgroundColor: 'transparent',
  cursor: 'pointer',
  color: '#FFFFFF'
}

const AlertTemplate = ({ message, options, style, close }) => {
  return (
    <div style={{ ...alertStyle, ...style }}>
      <span style={{ flex: 2 }}>{message}</span>
      <button onClick={close} style={buttonStyle}>
        X
      </button>
    </div>
  )
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
  <AlertProvider template={AlertTemplate} {...alertOptions}>
    <BrowserRouter>
      <ApolloProvider client={client}>
        <ExpandedIndexProvider>
          <App/>
        </ExpandedIndexProvider>
      </ApolloProvider>
    </BrowserRouter>
  </AlertProvider>,
  document.getElementById('root')
);
