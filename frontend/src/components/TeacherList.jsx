import React, { useEffect, useState } from 'react';
import './TeacherList.css';

export default function TeacherList() {
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [sortBy, setSortBy] = useState('name');
  const [sortAsc, setSortAsc] = useState(true);
  const [search, setSearch] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('');
  const [form, setForm] = useState({ name: '', subjects: [], restrictions: '', preferences: '', weekly_hours: 1 });
  const [editingId, setEditingId] = useState(null);
  const [courseFilter, setCourseFilter] = useState('');

  useEffect(() => {
    fetchTeachers();
    fetchSubjects();
  }, []);

  function fetchSubjects() {
    fetch('http://localhost:5000/subjects')
      .then(res => res.json())
      .then(setSubjects);
  }

  function fetchTeachers() {
    fetch('http://localhost:5000/teachers')
      .then(res => res.json())
      .then(setTeachers);
  }


  function handleChange(e) {
  const { name, value, selectedOptions } = e.target;
    if (name === 'subjects') {
      const values = Array.from(selectedOptions, opt => Number(opt.value));
      setForm({ ...form, subjects: values });
    } else {
      setForm({ ...form, [name]: value });
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    const method = editingId ? 'PUT' : 'POST';
    const url = editingId
      ? `http://localhost:5000/teachers/${editingId}`
      : 'http://localhost:5000/teachers';
    // Map Spanish field to English for backend
    const payload = {
      name: form.name,
      subjects: form.subjects,
      restrictions: form.restrictions,
      preferences: form.preferences,
      weekly_hours: Number(form.weekly_hours) > 0 ? Number(form.weekly_hours) : 1
    };
    fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(() => {
        fetchTeachers();
        setForm({ name: '', subjects: [], restrictions: '', preferences: '', weekly_hours: 1 });
        setEditingId(null);
      });
  }

  function handleEdit(teacher) {
    setForm({
      name: teacher.name,
      subjects: teacher.subjects ? teacher.subjects.map(s => String(s.id)) : [],
      restrictions: teacher.restrictions || '',
      preferences: teacher.preferences || '',
      weekly_hours: teacher.weekly_hours ?? 1
    });
    setEditingId(teacher.id);
  }

  function handleDelete(id) {
    fetch(`http://localhost:5000/teachers/${id}`, { method: 'DELETE' })
      .then(() => fetchTeachers());
  }

  function handleSort(field) {
    if (sortBy === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortBy(field);
      setSortAsc(true);
    }
  }

  // Obtener lista de asignaturas únicas para el filtro
  const subjectOptions = Array.from(new Set(
    teachers.flatMap(t => t.subjects ? t.subjects.map(s => s.name) : [])
  ));

  // Obtener lista de cursos únicos para el filtro
  const courseOptions = Array.from(new Set(
    subjects.filter(s => s.course).map(s => s.course.name)
  ));

  const filteredTeachers = teachers.filter(teacher => {
  const matchesName = (teacher.name || '').toLowerCase().includes(search.toLowerCase());
    const matchesSubject = subjectFilter === '' || (teacher.subjects && teacher.subjects.map(s => s.name).includes(subjectFilter));
    const matchesCourse = courseFilter === '' || (teacher.subjects && teacher.subjects.some(s => s.course && s.course.name === courseFilter));
    return matchesName && matchesSubject && matchesCourse;
  });

  const sortedTeachers = [...filteredTeachers].sort((a, b) => {
    let aField, bField;
    if (sortBy === 'name') {
      aField = a.name || '';
      bField = b.name || '';
    } else if (sortBy === 'subjects') {
      aField = a.subjects ? a.subjects.map(s => s.name).join(', ') : '';
      bField = b.subjects ? b.subjects.map(s => s.name).join(', ') : '';
    }
    if (aField < bField) return sortAsc ? -1 : 1;
    if (aField > bField) return sortAsc ? 1 : -1;
    return 0;
  });

  return (
    <div>
      <h2>Profesores</h2>
      <form onSubmit={handleSubmit} className="teacher-form">
        <div className="teacher-form-row">
          <div className="teacher-form-col1">
            <label className="teacher-label">Nombre del profesor:</label>
            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Nombre del profesor"
              required
              className="teacher-input"
            />
            <label className="teacher-label teacher-label-margin">Horas lectivas/semana:</label>
            <input
              name="weekly_hours"
              type="number"
              min="0"
              value={form.weekly_hours}
              onChange={handleChange}
              placeholder="Horas lectivas por semana"
              className="teacher-input"
            />
          </div>
          <div className="teacher-form-col2">
            <label className="teacher-label">Asignaturas:</label>
            <select
              name="subjectsDropdown"
              value=""
              onChange={e => {
                const id = e.target.value;
                if (id && !form.subjects.includes(id)) {
                  setForm(f => ({ ...f, subjects: [...f.subjects, id] }));
                }
              }}
              className="teacher-select"
            >
              <option value="">Añadir asignatura...</option>
              {subjects
                .filter(s => !form.subjects.includes(String(s.id)))
                .sort((a, b) => a.name.localeCompare(b.name))
                .map(s => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
            </select>
            <div className="teacher-subject-list">
              {form.subjects.map(id => {
                const subj = subjects.find(s => String(s.id) === String(id));
                if (!subj) return null;
                return (
                  <span key={id} className="teacher-subject-chip">
                    {subj.name}
                    <button type="button" className="teacher-chip-btn" onClick={() => setForm(f => ({ ...f, subjects: f.subjects.filter(sid => String(sid) !== String(id)) }))}>×</button>
                  </span>
                );
              })}
            </div>
          </div>
        </div>
        {/* Restricciones y Preferencias: nueva fila debajo de las columnas, ancho 100% */}
        <div className="teacher-form-section">
          <label className="teacher-label teacher-label-margin">Restricciones:</label>
          <textarea
            name="restrictions"
            value={form.restrictions}
            onChange={handleChange}
            placeholder="Restricciones (ej: no disponible lunes)"
            rows={3}
            className="teacher-textarea"
          />
          <label className="teacher-label teacher-label-margin">Preferencias:</label>
          <textarea
            name="preferences"
            value={form.preferences}
            onChange={handleChange}
            placeholder="Preferencias (ej: prefiere mañana)"
            rows={3}
            className="teacher-textarea"
          />
        </div>
        <div className="teacher-form-actions">
          <button type="submit" className="teacher-btn">
            {editingId ? 'Actualizar' : 'Añadir'}
          </button>
          {editingId && (
            <button type="button" className="teacher-btn teacher-btn-cancel" onClick={() => { setForm({ name: '', subjects: [], restrictions: '', preferences: '', weekly_hours: 1 }); setEditingId(null); }}>
              Cancelar
            </button>
          )}
        </div>
      </form>
      <div className="teacher-search-bar">
        <input
          type="text"
          placeholder="Buscar por nombre..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="teacher-search-input"
        />
        <select
          value={subjectFilter}
          onChange={e => setSubjectFilter(e.target.value)}
          className="teacher-search-select"
        >
          <option value="">Todas las asignaturas</option>
          {subjectOptions.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select
          value={courseFilter}
          onChange={e => setCourseFilter(e.target.value)}
          className="teacher-search-select"
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
            <th className="teacher-table-th-sort" onClick={() => handleSort('name')}>
              Nombre {sortBy === 'name' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th className="teacher-table-th-sort" onClick={() => handleSort('subjects')}>
              Asignaturas {sortBy === 'subjects' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th>Horas/semana</th>
            <th>Restricciones</th>
            <th>Preferencias</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {sortedTeachers.map(teacher => (
            <tr key={teacher.id}>
              <td>{teacher.id}</td>
              <td>{teacher.name}</td>
              <td>{teacher.subjects ? teacher.subjects.map(s => `${s.name}`).join(', ') : ''}</td>
              <td>{teacher.weekly_hours ?? ''}</td>
              <td>{teacher.restrictions}</td>
              <td>{teacher.preferences}</td>
              <td>
                <button className="teacher-btn-edit" onClick={() => handleEdit(teacher)}>Editar</button>
                <button className="teacher-btn-delete" onClick={() => handleDelete(teacher.id)}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
