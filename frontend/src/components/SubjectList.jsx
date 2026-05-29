import React, { useEffect, useState } from 'react';
import api from '../lib/api';
import { t } from '../i18n';
import ConfirmDeleteModal from './ConfirmDeleteModal';
import FormModal from './FormModal';
import SubjectForm from './SubjectForm';
import './SubjectList.css';
import SectionLayout from './SectionLayout';

function SubjectList() {
  const [subjects, setSubjects] = useState([]);
  const [courses, setCourses] = useState([]);
  const [daysPerWeek, setDaysPerWeek] = useState(5);
  const [sortBy, setSortBy] = useState('name');
  const [sortAsc, setSortAsc] = useState(true);
  const [search, setSearch] = useState('');
  const [courseFilter, setCourseFilter] = useState('');
  const [form, setForm] = useState({ name: '', course_id: '', color: '#dbeafe', weekly_hours: 2, max_hours_per_day: 2, consecutive_hours: true, linked_subject_id: '', included_lines: null });
  const [showForm, setShowForm] = useState(false);
  const [formError, setFormError] = useState('');
  const [lockedHours, setLockedHours] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteId, setDeleteId] = useState(null);

  useEffect(() => {
    fetchSubjects();
    fetchCourses();
    fetchConfig();
  }, []);

  function fetchConfig() {
    api.get('/config').then(cfg => {
      if (cfg && typeof cfg.days_per_week === 'number') setDaysPerWeek(cfg.days_per_week);
    }).catch(() => {});
  }


  function fetchSubjects() {
    api.get('/subjects').then(setSubjects).catch(() => setSubjects([]));
  }

  function fetchCourses() {
    api.get('/courses').then(setCourses).catch(() => setCourses([]));
  }


  function handleSubmit(e) {
    e.preventDefault();
    const payload = {
      id: form.id,
      name: form.name,
      color: form.color || '#dbeafe',
      weekly_hours: form.weekly_hours,
      max_hours_per_day: form.max_hours_per_day,
      consecutive_hours: form.consecutive_hours ?? true,
      teach_every_day: !!form.teach_every_day,
      course_id: form.course_id,
      linked_subject_id: form.linked_subject_id || null,
      included_lines: form.included_lines,
    };
    setFormError('');
    const action = editingId ? api.put(`/subjects/${editingId}`, payload) : api.post('/subjects', payload);
    action.then(() => {
      fetchSubjects();
  setForm({ id: '', name: '', course_id: '', color: '#dbeafe', weekly_hours: 2, max_hours_per_day: 2, consecutive_hours: true, linked_subject_id: '', included_lines: null });
      setEditingId(null);
      setShowForm(false);
      setLockedHours(false);
      setSelectedEntity(null);
    }).catch(err => setFormError(err.message));
  }

  function handleEdit(subject) {
    setForm({ 
      name: subject.name, 
      course_id: subject.course ? subject.course.id : '', 
      id: subject.id, 
      color: subject.color || '#dbeafe',
      weekly_hours: subject.weekly_hours ?? 2,
      max_hours_per_day: subject.max_hours_per_day ?? 2,
      consecutive_hours: subject.consecutive_hours ?? true,
      teach_every_day: subject.teach_every_day ?? false,
      linked_subject_id: subject.linked_subject_id || '',
      included_lines: subject.included_lines ?? null,
    });
    const isLocked = subject.subject_groups && subject.subject_groups.length > 0;
    setLockedHours(Boolean(isLocked));
    setEditingId(subject.id);
    setShowForm(false);
    setSelectedEntity(subject);
  }

  function handleDelete(id) {
    setDeleteId(id);
    setShowDeleteModal(true);
  }

  function confirmDelete() {
    api.del(`/subjects/${deleteId}`).then(() => {
      fetchSubjects();
      setShowDeleteModal(false);
      setDeleteId(null);
      setSelectedEntity(null);
      setEditingId(null);
      setForm({ id: '', name: '', course_id: '', color: '#dbeafe', weekly_hours: 2, max_hours_per_day: 2, consecutive_hours: true, linked_subject_id: '', included_lines: null });
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

  const courseOptions = Array.from(new Set(subjects.map(s => s.course ? s.course.name : t('subjects.no_course')))).sort((a, b) => a.localeCompare(b));

  const filteredSubjects = subjects.filter(subject => {
    const matchesName = subject.name.toLowerCase().includes(search.toLowerCase());
    const matchesCourse = courseFilter === '' || (subject.course ? subject.course.name : t('subjects.no_course')) === courseFilter;
    return matchesName && matchesCourse;
  });

  const sortedSubjects = [...filteredSubjects].sort((a, b) => {
    let aField, bField;
    if (sortBy === 'id') {
      aField = a.id || '';
      bField = b.id || '';
    } else if (sortBy === 'name') {
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
    <>
      <ConfirmDeleteModal
        open={showDeleteModal}
        entity={t('subjects.title')}
        id={deleteId}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
      {showForm && (
        <FormModal open={showForm} onClose={() => { setForm({ id: '', name: '', course_id: '', color: '#dbeafe', weekly_hours: 2, max_hours_per_day: 1, consecutive_hours: true, linked_subject_id: '', included_lines: null }); setEditingId(null); setShowForm(false); }}>
          <SubjectForm
            form={form}
            setForm={setForm}
            courses={courses}
            subjects={subjects}
            lockedHours={lockedHours}
            editingId={editingId}
            daysPerWeek={daysPerWeek}
            formError={formError}
            onSubmit={handleSubmit}
              onCancel={() => { setForm({ id: '', name: '', course_id: '', color: '#dbeafe', weekly_hours: 2, max_hours_per_day: 1, consecutive_hours: true, linked_subject_id: '', included_lines: null }); setEditingId(null); setShowForm(false); }}
          />
        </FormModal>
      )}
      {selectedEntity && (
        <FormModal open={!!selectedEntity} onClose={() => { setSelectedEntity(null); setEditingId(null); setForm({ id: '', name: '', course_id: '', color: '#dbeafe', weekly_hours: 2, max_hours_per_day: 2, consecutive_hours: true, linked_subject_id: '', included_lines: null }); setLockedHours(false); }}>
          <SubjectForm
            form={form}
            setForm={setForm}
            courses={courses}
            subjects={subjects}
            lockedHours={lockedHours}
            editingId={editingId}
            daysPerWeek={daysPerWeek}
            formError={formError}
            onSubmit={handleSubmit}
            onCancel={() => { setSelectedEntity(null); setEditingId(null); setForm({ id: '', name: '', course_id: '', color: '#dbeafe', weekly_hours: 2, max_hours_per_day: 2, consecutive_hours: true, linked_subject_id: '', included_lines: null }); setLockedHours(false); }}
            onDelete={() => handleDelete(selectedEntity.id)}
            subject={selectedEntity}
          />
        </FormModal>
      )}
      <SectionLayout
        title={t('subjects.title')}
        actions={
          !showForm && !selectedEntity && (
            <button
              className="btn btn--primary btn--compact"
              onClick={() => { setForm({ id: '', name: '', course_id: '', color: '#dbeafe', weekly_hours: 2, max_hours_per_day: 1, consecutive_hours: true, linked_subject_id: '', included_lines: null }); setShowForm(true); }}
            >
              {t('subjects.add_subject')}
            </button>
          )
        }
      >
        {formError && (
          <div role="alert" className="state-error mb-md">
            {formError}
          </div>
        )}
        <div className="search-bar">
          <input
            type="text"
            placeholder={t('common.search_placeholder')}
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input search-input"
          />
          <select
            value={courseFilter}
            onChange={e => setCourseFilter(e.target.value)}
            className="select search-select"
          >
            <option value="">{t('common.all_courses')}</option>
            {courseOptions.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
          </select>
        </div>
      <table className="modern-table">
        <thead>
          <tr>
            <th className="subject-table-th-sort" onClick={() => handleSort('id')}>
              {t('common.id') || 'ID'} {sortBy === 'id' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th className="subject-table-th-sort" onClick={() => handleSort('name')}>
              {t('common.name') || 'Name'} {sortBy === 'name' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th className="subject-table-th-sort" onClick={() => handleSort('course')}>
              {t('subjects.course') || 'Course'} {sortBy === 'course' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th>{t('subjects.linked') || 'Vinculada'}</th>
            <th>{t('subjects.teacher')}</th>
            <th className="subject-table-th-sort" onClick={() => handleSort('weekly_hours')}>
              {t('subjects.weekly_hours')} {sortBy === 'weekly_hours' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th className="subject-table-th-sort" onClick={() => handleSort('max_hours_per_day')}>
              {t('subjects.max_hours_per_day')} {sortBy === 'max_hours_per_day' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedSubjects.map(subject => (
            <tr key={subject.id} onClick={() => handleEdit(subject)} style={{ cursor: 'pointer' }}>
              <td>{subject.id}</td>
              <td>
                <span className="subject-color-chip" style={{ backgroundColor: subject.color || '#dbeafe' }} aria-hidden="true" />
                <span className="subject-name">{subject.name}</span>
                {subject.subject_groups?.map(g => (
                  <span key={g.id} className="group-badge">{g.name}</span>
                ))}
              </td>
              <td>{subject.course ? subject.course.name : t('subjects.no_course')}</td>
              <td>
                {subject.linked_subject_id ? (
                  (() => {
                    const linked = subjects.find(s => s.id === subject.linked_subject_id);
                    return linked ? linked.full_name || linked.name : subject.linked_subject_id;
                  })()
                ) : '—'}
              </td>
              <td className="text-center">
                {subject.teachers && subject.teachers.length > 0
                  ? <span className="text-success font-bold">✓</span>
                  : <span className="text-danger">✗</span>}
              </td>
              <td>{subject.weekly_hours}</td>
              <td>{subject.max_hours_per_day || 2}</td>
            </tr>
          ))}
        </tbody>
      </table>
      </SectionLayout>
    </>
  );
}

export default SubjectList;
