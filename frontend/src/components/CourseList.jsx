import React, { useEffect, useState } from 'react';

export default function CourseList() {
  const [courses, setCourses] = useState([]);
  const [sortAsc, setSortAsc] = useState(true);
  const [search, setSearch] = useState('');
  const [form, setForm] = useState({ name: '', num_lines: 1 });
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    fetchCourses();
  }, []);

  function fetchCourses() {
    fetch('http://localhost:5000/courses')
      .then(res => res.json())
      .then(setCourses);
  }

  function handleSort() {
    setSortAsc(!sortAsc);
  }

  function handleChange(e) {
    const { name, value } = e.target;
    // Map num_lineas (UI) to num_lines (state)
    if (name === 'num_lineas') {
      setForm({ ...form, num_lines: value });
    } else {
      setForm({ ...form, [name]: value });
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    const method = editingId ? 'PUT' : 'POST';
    const url = editingId
      ? `http://localhost:5000/courses/${form.name}`
      : 'http://localhost:5000/courses';
    // Map Spanish field to English for backend
    const payload = {
      name: form.name,
      num_lines: form.num_lines
    };
    fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(() => {
        fetchCourses();
        setForm({ name: '' });
        setEditingId(null);
      });
  }

  function handleEdit(course) {
  setForm({ name: course.name, num_lines: course.num_lines });
    setEditingId(course.name);
  }

  function handleDelete(id) {
    fetch(`http://localhost:5000/courses/${id}`, { method: 'DELETE' })
      .then(() => fetchCourses());
  }

  const filteredCourses = courses.filter(course =>
    course.name.toLowerCase().includes(search.toLowerCase())
  );

  const sortedCourses = [...filteredCourses].sort((a, b) => {
  if (a.name < b.name) return sortAsc ? -1 : 1;
  if (a.name > b.name) return sortAsc ? 1 : -1;
  return 0;
  });

  return (
    <div>
      <h2>Cursos</h2>
      <form onSubmit={handleSubmit} style={{ marginBottom: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <label style={{ display: 'flex', flexDirection: 'column', fontWeight: 500 }}>
          Nombre del curso
          <input
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="Nombre del curso"
            required
            style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid #ccc', marginTop: 2 }}
          />
        </label>
        <label style={{ display: 'flex', flexDirection: 'column', fontWeight: 500 }}>
          Nº líneas
          <input
            name="num_lines"
            type="number"
            min={1}
            value={form.num_lines}
            onChange={handleChange}
            placeholder="Nº líneas"
            required
            style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid #ccc', width: 100, marginTop: 2 }}
          />
        </label>
        <button type="submit" style={{ padding: '6px 16px', borderRadius: 6, background: '#2563eb', color: '#fff', border: 'none' }}>
          {editingId ? 'Actualizar' : 'Añadir'}
        </button>
        {editingId && (
          <button type="button" style={{ padding: '6px 16px', borderRadius: 6, background: '#64748b', color: '#fff', border: 'none' }} onClick={() => { setForm({ name: '', num_lines: 1 }); setEditingId(null); }}>
            Cancelar
          </button>
        )}
      </form>
      <input
        type="text"
        placeholder="Buscar por nombre..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        style={{ marginBottom: '1rem', padding: '6px 12px', borderRadius: 6, border: '1px solid #ccc' }}
      />
      <table className="modern-table">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Nº líneas</th>
            <th>Grupos</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {sortedCourses.map(course => {
            const grupos = Array.from({ length: course.num_lines }, (_, i) => `${course.name}${String.fromCharCode(65 + i)}`);
            return (
              <tr key={course.name}>
                <td>{course.name}</td>
                <td>{course.num_lines}</td>
                <td>{grupos.join(', ')}</td>
                <td>
                  <button style={{ marginRight: 8, padding: '4px 10px', borderRadius: 4, border: 'none', background: '#fbbf24', color: '#222' }} onClick={() => handleEdit(course)}>Editar</button>
                  <button style={{ padding: '4px 10px', borderRadius: 4, border: 'none', background: '#ef4444', color: '#fff' }} onClick={() => handleDelete(course.name)}>Eliminar</button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
