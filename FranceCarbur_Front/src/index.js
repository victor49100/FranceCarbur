import React from 'react';
import ReactDOM from 'react-dom';
import App from './App'; // Assurez-vous que App.jsx existe dans le même dossier
import './style.css'; // Si vous avez un fichier de styles global

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root') // Assurez-vous que le fichier public/index.html contient un div avec id="root"
);
