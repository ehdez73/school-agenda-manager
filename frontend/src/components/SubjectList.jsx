import React, { useEffect, useState } from 'react';
import './SubjectList.css';

function SubjectList() {
  const [subjects, setSubjects] = useState([]);
  const [courses, setCourses] = useState([]);
  const [sortBy, setSortBy] = useState('name');
  const [sortAsc, setSortAsc] = useState(true);
  const [search, setSearch] = useState('');
  const [courseFilter, setCourseFilter] = useState('');
  const [form, setForm] = useState({ name: '', course_id: '', weekly_hours: 2 });
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    fetchSubjects();
    fetchCourses();
  }, []);
// (Remove duplicate function declaration and hooks)

  function fetchSubjects() {
    fetch('http://localhost:5000/subjects')
      .then(res => res.json())
      .then(setSubjects);
  }

  function fetchCourses() {
    fetch('http://localhost:5000/courses')
      .then(res => res.json())
      .then(setCourses);
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function handleSubmit(e) {
    e.preventDefault();
    const method = editingId ? 'PUT' : 'POST';
    const url = editingId
      ? `http://localhost:5000/subjects/${editingId}`
      : 'http://localhost:5000/subjects';
    // Map Spanish field to English for backend
    const payload = {
      id: form.id,
      name: form.name,
      weekly_hours: form.weekly_hours,
      course_id: form.course_id
    };
    fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(() => {
        fetchSubjects();
  setForm({ name: '', course_id: '', weekly_hours: 2 });
        setEditingId(null);
      });
  }

  function handleEdit(subject) {
  setForm({ name: subject.name, course_id: subject.course ? subject.course.id : '', id: subject.id, weekly_hours: subject.weekly_hours ?? 2 });
    setEditingId(subject.id);
  }

  function handleDelete(id) {
    fetch(`http://localhost:5000/subjects/${id}`, { method: 'DELETE' })
      .then(() => fetchSubjects());
  }

  function handleSort(field) {
    if (sortBy === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortBy(field);
      setSortAsc(true);
    }
  }

  // Obtener lista de cursos únicos para el filtro
  const courseOptions = Array.from(new Set(subjects.map(s => s.course ? s.course.name : 'Sin curso')));

  const filteredSubjects = subjects.filter(subject => {
    const matchesName = subject.name.toLowerCase().includes(search.toLowerCase());
    const matchesCourse = courseFilter === '' || (subject.course ? subject.course.name : 'Sin curso') === courseFilter;
    return matchesName && matchesCourse;
  });

  const sortedSubjects = [...filteredSubjects].sort((a, b) => {
    let aField, bField;
    if (sortBy === 'name') {
      aField = a.name || '';
      bField = b.name || '';
    } else if (sortBy === 'course') {
      aField = a.course ? a.course.name : '';
      bField = b.course ? b.course.name : '';
    }
    if (aField < bField) return sortAsc ? -1 : 1;
    if (aField > bField) return sortAsc ? 1 : -1;
    return 0;
  });

  return (
    <div>
      <h2>Asignaturas</h2>
  <form onSubmit={handleSubmit} className="subject-form">
  <label className="subject-label">
          ID alfanumérico
          <input
            name="id"
            value={form.id || ''}
            onChange={handleChange}
            placeholder="ID alfanumérico"
            required
            className="subject-input"
          />
        </label>
  <label className="subject-label">
          Nombre de la asignatura
          <input
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="Nombre de la asignatura"
            required
            className="subject-input"
          />
        </label>
  <label className="subject-label">
          Curso
          <select
            name="course_id"
            value={form.course_id}
            onChange={handleChange}
            required
            className="subject-select"
          >
            <option value="">Selecciona un curso</option>
            {courses.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </label>
  <label className="subject-label">
          Weekly hours
          <input
            name="weekly_hours"
            type="number"
            min={1}
            value={form.weekly_hours}
            onChange={handleChange}
            placeholder="Weekly hours"
            required
            className="subject-input subject-input-short"
          />
        </label>
        <button type="submit" className="subject-btn">
          {editingId ? 'Actualizar' : 'Añadir'}
        </button>
        {editingId && (
          <button type="button" className="subject-btn subject-btn-cancel" onClick={() => { setForm({ id: '', name: '', course_id: '' }); setEditingId(null); }}>
            Cancelar
          </button>
        )}
      </form>
  <div className="subject-search-bar">
        <input
          type="text"
          placeholder="Buscar por nombre..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="subject-search-input"
        />
        <select
          value={courseFilter}
          onChange={e => setCourseFilter(e.target.value)}
          className="subject-search-select"
        >
          <option value="">Todos los cursos</option>
          {courseOptions.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>
      <table className="modern-table">
        <thead>
          <tr>
            <th>ID</th>
            <th className="subject-table-th-sort" onClick={() => handleSort('name')}>
              Nombre {sortBy === 'name' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th className="subject-table-th-sort" onClick={() => handleSort('course')}>
              Curso {sortBy === 'course' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th>Horas/semana</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {sortedSubjects.map(subject => (
            <tr key={subject.id}>
              <td>{subject.id}</td>
              <td>{subject.name}</td>
              <td>{subject.course ? subject.course.name : 'Sin curso'}</td>
              <td>{subject.weekly_hours}</td>
              <td>
                <button className="subject-btn-edit" onClick={() => handleEdit(subject)}>Editar</button>
                <button className="subject-btn-delete" onClick={() => handleDelete(subject.id)}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default SubjectList;
