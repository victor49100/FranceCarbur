import React, { useState, useEffect } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const Carte = () => {
  const [filters, setFilters] = useState({
    Gazole: true,
    SP95: true,
    SP98: true,
    E10: true,
    E85: true,
    GPLC: true,
  });

  useEffect(() => {
    const map = L.map('map').setView([46.603354, 1.888334], 6);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);
  }, []);

  const handleFilterChange = (fuelType) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      [fuelType]: !prevFilters[fuelType],
    }));
  };

  return (
    <div>
      <header className="filter-bar">
        {Object.keys(filters).map((fuelType) => (
          <label key={fuelType}>
            <input
              type="checkbox"
              checked={filters[fuelType]}
              onChange={() => handleFilterChange(fuelType)}
            />
            {fuelType}
          </label>
        ))}
      </header>
      <div id="map" style={{ height: '600px', width: '100%' }}></div>
    </div>
  );
};

export default Carte;
