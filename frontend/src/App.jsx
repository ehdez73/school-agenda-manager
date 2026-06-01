import { useState, useEffect } from 'react';
import './App.css';
import { t } from './i18n';
import CourseList from './components/CourseList';
import SubjectList from './components/SubjectList';
import TeacherList from './components/TeacherList';
import ConfigForm from './components/ConfigForm';
import MarkdownTimetable from './components/MarkdownTimetable';
import LanguageSelector from './components/LanguageSelector';
import HelpSection from './components/HelpSection';
import { setLocale as i18nSetLocale } from './i18n';

function App() {
  const [page, setPage] = useState(() => {
    try { return localStorage.getItem('currentPage') || 'home'; } catch { return 'home'; }
  });
  const [locale, setLocaleState] = useState(() => {
    try { return localStorage.getItem('locale') || (navigator.language && navigator.language.startsWith('es') ? 'es' : 'en'); } catch { return 'en'; }
  });

  useEffect(() => {
    // keep i18n module in sync so its t() uses the same current locale
    try { i18nSetLocale(locale); } catch { /* ignore */ }
  }, [locale]);

  useEffect(() => {
    if ('scrollRestoration' in window.history) {
      const previous = window.history.scrollRestoration;
      window.history.scrollRestoration = 'manual';
      return () => {
        window.history.scrollRestoration = previous;
      };
    }
    return undefined;
  }, []);

  useEffect(() => {
    try { localStorage.setItem('currentPage', page); } catch { /* ignore */ }
  }, [page]);

  useEffect(() => {
    // Deep links with hashes are intended for Help guide headings.
    if (window.location.hash && page !== 'help') {
      setPage('help');
    }
  }, []);

  useEffect(() => {
    if (page === 'help' || !window.location.hash) return;

    const nextUrl = `${window.location.pathname}${window.location.search}`;
    window.history.replaceState(null, '', nextUrl);
  }, [page]);

  useEffect(() => {
    const onHashChange = () => {
      if (window.location.hash && page !== 'help') {
        setPage('help');
      }
    };

    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, [page]);

  return (
    <div className="app">
      <a
        href="https://github.com/ehdez73/school-agenda-manager"
        className="github-ribbon"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Fork me on GitHub"
      >
        <img
          width="149"
          height="149"
          src="https://github.blog/wp-content/uploads/2008/12/forkme_right_red_aa0000.png"
          alt="Fork me on GitHub"
        />
      </a>
      <nav className="app__nav">
        <div className="nav__links">
          <span className="nav__brand" onClick={() => setPage('home')}>
            {t('nav.brand')}
          </span>
          <button className={'nav__link' + (page === 'courses' ? ' nav__link--active' : '')} onClick={() => setPage('courses')}>
            {t('nav.courses')}
          </button>
          <button className={'nav__link' + (page === 'subjects' ? ' nav__link--active' : '')} onClick={() => setPage('subjects')}>
            {t('nav.subjects')}
          </button>
          <button className={'nav__link' + (page === 'teachers' ? ' nav__link--active' : '')} onClick={() => setPage('teachers')}>
            {t('nav.teachers')}
          </button>
          <button className={'nav__link' + (page === 'timetable-markdown' ? ' nav__link--active' : '')} onClick={() => setPage('timetable-markdown')}>
            {t('nav.timetable')}
          </button>
          <button className={'nav__link' + (page === 'config' ? ' nav__link--active' : '')} onClick={() => setPage('config')}>
            {t('nav.config')}
          </button>
          <button className={'nav__link' + (page === 'help' ? ' nav__link--active' : '')} onClick={() => setPage('help')}>
            {t('nav.help')}
          </button>
        </div>
        <LanguageSelector value={locale} onChange={setLocaleState} />
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
        {page === 'timetable-markdown' && <MarkdownTimetable />}
        {page === 'config' && <ConfigForm />}
        {page === 'help' && <HelpSection locale={locale} />}
      </main>

      <footer className="app__footer">
        <span>Made with <span className="footer__heart">&hearts;</span> by ehdez73</span>
      </footer>
    </div>
  );
}

export default App;