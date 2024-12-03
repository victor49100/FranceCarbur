// App.jsx
import {
  BrowserRouter as Router,
  Routes,
  Route,
} from 'react-router-dom';
import Accueil from './Accueil';
import Carte from './Carte'; // Import du nouveau composant

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Accueil />} />
        <Route path="/carte" element={<Carte />} /> {/* Nouvelle route pour la carte */}
      </Routes>
    </Router>
  );
};

export default App;
