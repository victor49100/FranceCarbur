
import './App.css'

function App() {

  return (      class App extends React.Component{
      render(){
          return(
              <div className="container">
                  <div className="form-box">
                      <div className="header-form">
                          <h4 className="text-primary text-center">
                              <i className="fa fa-user-circle" style={{fontSize:"110px"}}></i>
                          </h4>
                          <div className="image"></div>
                      </div>
                      <div className="body-form">
                          <form>
                              <div className="input-group mb-3">
                                  <div className="input-group-prepend">
                                      <span className="input-group-text"><i className="fa fa-user"></i></span>
                                  </div>
                                  <input type="text" className="form-control" placeholder="Identitfiant" />
                              </div>
                              <div className="input-group mb-3">
                                  <div className="input-group-prepend">
                                      <span className="input-group-text"><i className="fa fa-lock"></i></span>
                                  </div>
                                  <input type="password" className="form-control" placeholder="Mot de passe" />
                              </div>
                              <button type="button" className="btn btn-secondary btn-block">Se connecter</button>
                              <button type="button" className="btn btn-secondary btn-block">Connexion invité</button>
                              <div className="message">
                              </div>
                          </form>
                      </div>
                  </div>
              </div>
          )
      }
  }

    ReactDOM.render(<App />, document.getElementById('root'));

)
}

export default App
