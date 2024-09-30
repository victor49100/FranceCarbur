// App.jsx
import {
    BrowserRouter as Router,
    Routes,
    Route
} from "react-router-dom";
import Accueil from './accueil/Accueil';
import Invite from './invite/Invite';


const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Accueil />} />
                <Route path="/invite" element={< Invite />} /> {}
            </Routes>
        </Router>
    );
}

export default App;
