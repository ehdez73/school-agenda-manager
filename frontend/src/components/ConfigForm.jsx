import React, { useEffect, useState } from 'react';
import './ConfigForm.css';

export default function ConfigForm() {
  const [classesPerDay, setClassesPerDay] = useState(5);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch('http://localhost:5000/config')
      .then(res => res.json())
      .then(data => {
        setClassesPerDay(data.classes_per_day);
        setLoading(false);
      });
  }, []);

  function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    fetch('http://localhost:5000/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ classes_per_day: Number(classesPerDay) })
    })
      .then(res => res.json())
      .then(data => {
        setClassesPerDay(data.classes_per_day);
        setMessage('Configuración guardada');
        setLoading(false);
        setTimeout(() => setMessage(''), 2000);
      });
  }

  return (
    <div className="config-form-container">
      <h2 className="config-form-title">Configuración</h2>
      <form onSubmit={handleSubmit}>
        <label className="config-form-label">
          Nº clases por día:
          <input
            type="number"
            min={1}
            value={classesPerDay}
            onChange={e => setClassesPerDay(e.target.value)}
            required
            className="config-form-input"
          />
        </label>
        <button type="submit" className="config-form-btn" disabled={loading}>
          Guardar
        </button>
        {message && <div className="config-form-message">{message}</div>}
      </form>
    </div>
  );
}
