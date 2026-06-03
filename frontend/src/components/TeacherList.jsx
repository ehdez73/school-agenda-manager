import { useEffect, useState } from 'react';
import api from '../lib/api';
import { t } from '../i18n';
import ConfirmDeleteModal from './ConfirmDeleteModal';
import FormModal from './FormModal';
import Select from './Select';
import TeacherForm from './TeacherForm';
import SectionLayout from './SectionLayout';
import './TeacherList.css';

const emptyTeacherForm = () => ({ name: '', subjects: [], teacher_subject_lines: {}, max_hours_week: 1, coordination_hours: 0, preferences: {}, tutor_groups: [] });

export default function TeacherList() {
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [sortBy, setSortBy] = useState('name');
  const [sortAsc, setSortAsc] = useState(true);
   const [courses, setCourses] = useState([]);
  const [search, setSearch] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('');
  const [form, setForm] = useState(emptyTeacherForm());
  const [classesPerDay, setClassesPerDay] = useState(5);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [courseFilter, setCourseFilter] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteId, setDeleteId] = useState(null);

  useEffect(() => {
    fetchTeachers();
    fetchSubjects();
    fetchCourses();
    api.get('/config').then(cfg => setClassesPerDay(cfg?.classes_per_day || 5)).catch(() => setClassesPerDay(5));
  }, []);

  function fetchSubjects() {
    api.get('/subjects').then(setSubjects).catch(() => setSubjects([]));
  }

  function fetchCourses() {
    api.get('/courses').then(setCourses).catch(() => setCourses([]));
  }

  function fetchTeachers() {
    api.get('/teachers').then(setTeachers).catch(() => setTeachers([]));
  }

  function handleSubmit(e) {
    e.preventDefault();
    const preferences_obj = form.preferences || {};
    const tsLines = form.teacher_subject_lines || {};
    const cleanedLines = {};
    for (const sid of form.subjects) {
      const val = tsLines[sid];
      if (val === undefined) continue;
      const subject = subjects.find(s => String(s.id) === String(sid));
      if (!subject) continue;
      const numLines = subject.course?.num_lines || 1;
      if (val === null || val.length === numLines) continue; // all lines = no restriction
      cleanedLines[sid] = val;
    }
    const payload = {
      name: form.name,
      subjects: form.subjects,
      teacher_subject_lines: Object.keys(cleanedLines).length > 0 ? cleanedLines : {},
      tutor_groups: form.tutor_groups || [],
      max_hours_week: Number(form.max_hours_week) > 0 ? Number(form.max_hours_week) : 1,
      coordination_hours: Number(form.coordination_hours) >= 0 ? Number(form.coordination_hours) : 0,
      preferences: preferences_obj
    };
    const action = editingId
      ? api.put(`/teachers/${editingId}`, payload)
      : api.post('/teachers', payload);

    action.then(() => {
      fetchTeachers();
      setForm(emptyTeacherForm());
      setEditingId(null);
      setShowForm(false);
      setSelectedEntity(null);
    }).catch(() => { });
  }

  function handleEdit(teacher) {
    setForm({
      id: teacher.id,
      name: teacher.name,
      subjects: teacher.subjects ? teacher.subjects.map(s => String(s.id)) : [],
      teacher_subject_lines: teacher.teacher_subject_lines || {},
      tutor_groups: teacher.tutor_groups ? teacher.tutor_groups.map(group => String(group)) : (teacher.tutor_group ? [String(teacher.tutor_group)] : []),
      max_hours_week: teacher.max_hours_week ?? 1,
      coordination_hours: teacher.coordination_hours ?? 0,
      preferences: teacher.preferences || {}
    });
    setEditingId(teacher.id);
    setShowForm(false);
    setSelectedEntity(teacher);
  }

  function handleDelete(id) {
    setDeleteId(id);
    setShowDeleteModal(true);
  }

  function confirmDelete() {
    api.del(`/teachers/${deleteId}`).then(() => {
      fetchTeachers();
      setShowDeleteModal(false);
      setDeleteId(null);
      setSelectedEntity(null);
      setEditingId(null);
      setForm(emptyTeacherForm());
    }).catch(() => { });
  }

  function cancelDelete() {
    setShowDeleteModal(false);
    setDeleteId(null);
  }

  function handleSort(field) {
    if (sortBy === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortBy(field);
      setSortAsc(true);
    }
  }

  const subjectOptions = Array.from(new Set(
    teachers.flatMap(t => t.subjects ? t.subjects.map(s => s.name) : [])
  )).sort((a, b) => a.localeCompare(b));

  const courseOptions = Array.from(new Set(
    subjects.filter(s => s.course).map(s => s.course.name)
  )).sort((a, b) => a.localeCompare(b));

  // Build a list of concrete groups (course + letter), e.g. '1ºA', '1ºB'
  const groupsList = courses.flatMap(course => {
    const num = Number(course.num_lines) || 1;
    return Array.from({ length: num }, (_, i) => {
      const name = `${course.name}${String.fromCharCode(65 + i)}`;
      return { id: name, name };
    });
  }).map(g => {
    const tutorIds = teachers
      .filter(t => (t.tutor_groups && t.tutor_groups.some(group => String(group) === String(g.id))) || String(t.tutor_group || '') === String(g.id))
      .map(t => t.id);
    return { ...g, tutor_ids: tutorIds };
  });

  const filteredTeachers = teachers.filter(teacher => {
    const matchesName = (teacher.name || '').toLowerCase().includes(search.toLowerCase());
    const matchesSubject = subjectFilter === '' || (teacher.subjects && teacher.subjects.map(s => s.name).includes(subjectFilter));
    const matchesCourse = courseFilter === '' || (teacher.subjects && teacher.subjects.some(s => s.course_id === courseFilter));
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
    <>
      <ConfirmDeleteModal
        open={showDeleteModal}
        entity={t('teachers.title')}
        id={deleteId}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
      {showForm && (
        <FormModal open={showForm} onClose={() => { setForm(emptyTeacherForm()); setEditingId(null); setShowForm(false); }}>
          <TeacherForm
            form={form}
            setForm={setForm}
            subjects={subjects}
            groups={groupsList}
            classesPerDay={classesPerDay}
            onSubmit={handleSubmit}
            onCancel={() => { setForm(emptyTeacherForm()); setEditingId(null); setShowForm(false); }}
          />
        </FormModal>
      )}
      {selectedEntity && (
        <FormModal open={!!selectedEntity} onClose={() => { setSelectedEntity(null); setEditingId(null); setForm(emptyTeacherForm()); }}>
          <TeacherForm
            form={form}
            setForm={setForm}
            subjects={subjects}
            groups={groupsList}
            classesPerDay={classesPerDay}
            onSubmit={handleSubmit}
            onCancel={() => { setSelectedEntity(null); setEditingId(null); setForm(emptyTeacherForm()); }}
            onDelete={() => handleDelete(selectedEntity.id)}
          />
        </FormModal>
      )}
      <SectionLayout
        title={t('teachers.title')}
        actions={
          !showForm && !selectedEntity && (
            <button
              className="btn btn--primary btn--compact"
              onClick={() => { setForm(emptyTeacherForm()); setShowForm(true); }}
            >
              {t('teachers.add_teacher')}
            </button>
          )
        }
      >
      <div className="search-bar">
        <input
          type="text"
          placeholder={t('common.search_placeholder')}
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="input search-input"
        />
        <Select
          value={subjectFilter}
          onChange={e => setSubjectFilter(e.target.value)}
          options={[
            { value: '', label: t('common.all_subjects') },
            ...subjectOptions.map(s => ({ value: s, label: s })),
          ]}
          className="search-select"
        />
        <Select
          value={courseFilter}
          onChange={e => setCourseFilter(e.target.value)}
          options={[
            { value: '', label: t('common.all_courses') },
            ...courseOptions.map(c => ({ value: c, label: c })),
          ]}
          className="search-select"
        />
      </div>
      <table className="modern-table">
        <thead>
          <tr>
            <th className="teacher-table-th-sort" onClick={() => handleSort('name')}>
              {t('common.name') || 'Name'} {sortBy === 'name' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th className="teacher-table-th-sort" onClick={() => handleSort('subjects')}>
              {t('teachers_table.subjects') || 'Subjects'} {sortBy === 'subjects' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th>{t('teachers.tutor_group') || 'Tutor'}</th>
            <th>{t('teachers.hours_week')}</th>
          </tr>
        </thead>
        <tbody>
          {sortedTeachers.map(teacher => (
            <tr key={teacher.id} onClick={() => handleEdit(teacher)} style={{ cursor: 'pointer' }}>
              <td>{teacher.name}</td>
              <td>{teacher.subjects ? teacher.subjects.map(s => `${s.full_name}`).join(', ') : ''}</td>
              <td>{teacher.tutor_groups ? teacher.tutor_groups.join(', ') : (teacher.tutor_group ?? '')}</td>
              <td>
                {(() => {
                  const max = teacher.max_hours_week ?? 0;
                  const lective = teacher.assigned_hours ?? 0;
                  const coord = teacher.coordination_hours ?? 0;
                  const support = teacher.support_hours ?? 0;
                  const total = lective + coord + support;
                  const totalMatch = total === max;
                  const parts = [];
                  if (lective > 0) parts.push(`${lective}h`);
                  if (coord > 0) parts.push(`${coord}h ${t('timetable.coordination_label_short')}`);
                  if (support > 0) parts.push(`${support}h ${t('timetable.support_label_short')}`);
                  const frac = totalMatch
                    ? `${total}h/${max}h`
                    : `<span style="color:red">${total}h/${max}h</span>`;
                  return <span dangerouslySetInnerHTML={{ __html: `${frac} ${parts.length ? ' (' + parts.join(', ') + ')' : ''}` }} />;
                })()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </SectionLayout>
    </>
  );
}
