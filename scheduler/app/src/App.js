import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import GoogleLogin from 'react-google-login';
import axios from 'axios';


class App extends Component {

  render() {
    const responseGoogle = (response) => {
      axios.post('/login', response).then(data => {
        console.log(data);
        axios.get('/protected', {
          headers: { 'Authorization': `Bearer ${data.data.access_token}`}
        }).then(res => {
          console.log(res)
        })
      })
      
    }
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Welcome to React</h1>
        </header>
        <p className="App-intro">
          To get started, edit <code>src/App.js</code> and save to reload.
        </p>
        <GoogleLogin
          clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}
          buttonText="Login"
          hostedDomain="redturtle.it"
          onSuccess={responseGoogle}
          onFailure={responseGoogle}
        />,
      </div>
    );
  }
}

export default App;
