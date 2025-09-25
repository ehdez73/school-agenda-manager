// agenda-frontend/src/App.js
import React, { useState } from 'react';
import './App.css';
import CourseList from './components/CourseList';
import SubjectList from './components/SubjectList';
import TeacherList from './components/TeacherList';
import ConfigForm from './components/ConfigForm';

function App() {
  const [page, setPage] = useState('home');
  const [theme, setTheme] = useState('light');

  return (
    <div className={`App theme-${theme} app-root`}>
  <nav className="app-nav">
        <div>
          <span className="nav-title" onClick={() => setPage('home')}>Inicio</span>
          <button className="nav-btn" onClick={() => setPage('courses')}>Cursos</button>
          <button className="nav-btn" onClick={() => setPage('subjects')}>Asignaturas</button>
          <button className="nav-btn" onClick={() => setPage('teachers')}>Profesores</button>
          <button className="nav-btn" onClick={() => setPage('config')}>Configuración</button>
        </div>
        <div>
          <label className="nav-label">Tema:</label>
          <select value={theme} onChange={e => setTheme(e.target.value)} className="nav-select">
            <option value="light">Claro</option>
            <option value="dark">Oscuro</option>
          </select>
        </div>
      </nav>
  <div className="app-content">
        {page === 'home' && (
          <div className="home-content">
            <h1>Bienvenido a la gestión académica</h1>
            <p>Utiliza el menú superior para acceder a la administración de profesores, asignaturas y cursos.</p>
          </div>
        )}
  {page === 'courses' && <CourseList />}
  {page === 'subjects' && <SubjectList />}
  {page === 'teachers' && <TeacherList />}
  {page === 'config' && <ConfigForm />}
      </div>
    </div>
  );
}

export default App;