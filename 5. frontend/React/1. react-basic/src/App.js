import React, {Component} from 'react';

// import Home from "./pages/Home";
// import About from "./pages/About";
// import Counter from "./pages/Counter";
// import Input from "./pages/Input";
// import Login from "./pages/Login";
// import UserList from "./pages/UserList";


function App() {
  return (
    <div className="App">
      <Home />
    </div>
  );
};

export default App;


class Home extends Component {
  render() {
      return <h1>Home init</h1>
  }
}


