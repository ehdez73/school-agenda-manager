import React, { useState, useEffect } from 'react';
import './App.css';
import { t } from './i18n';
import CourseList from './components/CourseList';
import SubjectList from './components/SubjectList';
import TeacherList from './components/TeacherList';
import SubjectGroupList from './components/SubjectGroupList';
import ConfigForm from './components/ConfigForm';
import MarkdownTimetable from './components/MarkdownTimetable';
import LanguageSelector from './components/LanguageSelector';
import { setLocale as i18nSetLocale } from './i18n';

function App() {
  const [page, setPage] = useState(() => {
    try { return localStorage.getItem('currentPage') || 'home'; } catch { return 'home'; }
  });
  const [theme, setTheme] = useState('light');
  const [locale, setLocaleState] = useState(() => {
    try { return localStorage.getItem('locale') || (navigator.language && navigator.language.startsWith('es') ? 'es' : 'en'); } catch { return 'en'; }
  });

  useEffect(() => {
    // keep i18n module in sync so its t() uses the same current locale
    try { i18nSetLocale(locale); } catch { /* ignore */ }
  }, [locale]);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    try { localStorage.setItem('currentPage', page); } catch { /* ignore */ }
  }, [page]);

  return (
    <div className="app">
      <nav className="app__nav">
        <div className="nav__links">
          <span className="nav__brand" onClick={() => setPage('home')}>
            {t('nav.brand')}
          </span>
          <button className="nav__link" onClick={() => setPage('courses')}>
            {t('nav.courses')}
          </button>
          <button className="nav__link" onClick={() => setPage('subjects')}>
            {t('nav.subjects')}
          </button>
          <button className="nav__link" onClick={() => setPage('subject-groups')}>
            {t('nav.subject_groups')}
          </button>
          <button className="nav__link" onClick={() => setPage('teachers')}>
            {t('nav.teachers')}
          </button>
          <button className="nav__link" onClick={() => setPage('timetable-markdown')}>
            {t('nav.timetable')}
          </button>
          <button className="nav__link" onClick={() => setPage('config')}>
            {t('nav.config')}
          </button>
        </div>
        <div className="nav__theme-controls">
          <label className="nav__theme-label">{t('nav.theme_label')}</label>
          <select
            value={theme}
            onChange={e => setTheme(e.target.value)}
            className="nav__theme-select"
          >
            <option value="light">{t('nav.theme_light')}</option>
            <option value="dark">{t('nav.theme_dark')}</option>
          </select>
          <LanguageSelector value={locale} onChange={setLocaleState} />
        </div>
      </nav>

      <main className="app__content">
        {page === 'home' && (
          <div className="home">
            <h1 className="home__title">{t('home.title')}</h1>
            <p className="home__description">{t('home.description')}</p>
          </div>
        )}
        {page === 'courses' && <CourseList />}
        {page === 'subjects' && <SubjectList />}
        {page === 'teachers' && <TeacherList />}
        {page === 'subject-groups' && <SubjectGroupList />}
        {page === 'timetable-markdown' && <MarkdownTimetable />}
        {page === 'config' && <ConfigForm />}
      </main>
    </div>
  );
}

export default App;