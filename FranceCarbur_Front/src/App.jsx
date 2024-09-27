import './style.css'

function App() {

    const handleSubmit = (event) => {
        event.preventDefault()
        console.log(new FormData(event.target))
        //ajout du code pour envoyer un post au back python
    }

    return (
        <>
            <div className="container">
                <div className="form-box">
                    <div className="header-form">
                        <h4 className="text-primary text-center">
                            <i className="fa fa-user-circle" style={{fontSize: "110px"}}></i>
                        </h4>
                        <div className="image"></div>
                    </div>
                    <div className="body-form">
                        <form onSubmit={handleSubmit}>
                            <div className="input-group mb-3">
                                <div className="input-group-prepend">
                                    <span className="input-group-text"><i className="fa fa-user"></i></span>
                                </div>
                                <input type="text" className="form-control" name="id" placeholder="Identitfiant"/>
                            </div>
                            <div className="input-group mb-3">
                                <div className="input-group-prepend">
                                    <span className="input-group-text"><i className="fa fa-lock"></i></span>
                                </div>
                                <input type="password" className="form-control" name="mdp" placeholder="Mot de passe"/>
                            </div>
                            <div>
                                <button type="submit">Se connecter</button>
                                <button type="button">Mode invité</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </>
    )
}

export default App
