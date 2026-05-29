import React, { useEffect, useMemo, useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import './MarkdownTimetable.css';
import api from '../lib/api';
import { t } from '../i18n';
import SectionLayout from './SectionLayout';

const POLL_INTERVAL_MS = 2000;
const POLL_RETRY_MS = 3000;


function parseTimetableSections(markdownText) {
  if (!markdownText || !markdownText.trim()) return [];

  const lines = markdownText.replace(/\r\n/g, '\n').split('\n');
  const sections = [];
  let currentSection = null;
  let currentEntry = null;

  const commitEntry = () => {
    if (!currentSection || !currentEntry) return;
    currentSection.entries.push({
      id: `${sections.length}-${currentSection.entries.length}`,
      title: currentEntry.title,
      markdown: currentEntry.lines.join('\n').trim(),
    });
    currentEntry = null;
  };

  const commitSection = () => {
    if (!currentSection) return;
    commitEntry();
    if (currentSection.entries.length > 0) {
      sections.push(currentSection);
    }
    currentSection = null;
  };

  for (const line of lines) {
    const sectionMatch = line.match(/^##\s+(.+)$/);
    if (sectionMatch) {
      commitSection();
      currentSection = { title: sectionMatch[1].trim(), entries: [] };
      continue;
    }

    if (!currentSection) continue;

    const entryMatch = line.match(/^###\s+(.+)$/);
    if (entryMatch) {
      commitEntry();
      currentEntry = { title: entryMatch[1].trim(), lines: [] };
      continue;
    }

    if (currentEntry) {
      currentEntry.lines.push(line);
    }
  }

  commitSection();
  return sections;
}


function collectSubjectEntryColors(node, colors) {
  if (node === null || node === undefined || typeof node === 'boolean') return;
  if (Array.isArray(node)) {
    node.forEach(child => collectSubjectEntryColors(child, colors));
    return;
  }
  if (typeof node !== 'object') return;

  const className = node?.props?.className || '';
  const isSubjectEntry = typeof className === 'string' && className.split(' ').includes('tt-subject-entry');
  if (isSubjectEntry) {
    const bg = node?.props?.style?.backgroundColor;
    if (typeof bg === 'string' && bg.trim()) {
      colors.add(bg.trim().toLowerCase());
    }
  }

  collectSubjectEntryColors(node?.props?.children, colors);
}


function stripSubjectEntryInlineBg(node) {
  if (node === null || node === undefined || typeof node === 'boolean') return node;
  if (Array.isArray(node)) {
    return node.map(child => stripSubjectEntryInlineBg(child));
  }
  if (typeof node !== 'object') return node;

  const className = node?.props?.className || '';
  const isSubjectEntry = typeof className === 'string' && className.split(' ').includes('tt-subject-entry');
  const nextChildren = stripSubjectEntryInlineBg(node?.props?.children);
  if (!isSubjectEntry) {
    return React.cloneElement(node, undefined, nextChildren);
  }

  const nextStyle = { ...(node?.props?.style || {}) };
  delete nextStyle.backgroundColor;
  return React.cloneElement(node, { style: nextStyle }, nextChildren);
}


function MarkdownTimetable() {
  const [markdown, setMarkdown] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [details, setDetails] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [phase, setPhase] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const [downloading, setDownloading] = useState(false);
  const [selectedCourseIds, setSelectedCourseIds] = useState([]);
  const [selectedTeacherIds, setSelectedTeacherIds] = useState([]);
  const [courseQuery, setCourseQuery] = useState('');
  const [teacherQuery, setTeacherQuery] = useState('');
  const [showCourseSuggestions, setShowCourseSuggestions] = useState(false);
  const [showTeacherSuggestions, setShowTeacherSuggestions] = useState(false);
  const timetableRef = useRef();
  const courseSelectorRef = useRef(null);
  const teacherSelectorRef = useRef(null);
  const allCoursesCheckboxRef = useRef(null);
  const allTeachersCheckboxRef = useRef(null);
  const pollingRef = useRef(null);
  const elapsedRef = useRef(null);
  const startTimeRef = useRef(null);

  const clearTimers = () => {
    if (pollingRef.current) {
      clearTimeout(pollingRef.current);
      pollingRef.current = null;
    }
    if (elapsedRef.current) {
      clearInterval(elapsedRef.current);
      elapsedRef.current = null;
    }
  };

  const startElapsedTimer = (createdAtSeconds = null) => {
    if (elapsedRef.current) clearInterval(elapsedRef.current);
    const startedAtMs = createdAtSeconds ? createdAtSeconds * 1000 : Date.now();
    startTimeRef.current = startedAtMs;
    setElapsed(Math.max(0, Math.floor((Date.now() - startedAtMs) / 1000)));
    elapsedRef.current = setInterval(() => {
      if (!startTimeRef.current) return;
      setElapsed(Math.max(0, Math.floor((Date.now() - startTimeRef.current) / 1000)));
    }, 1000);
  };

  const stopGeneration = () => {
    clearTimers();
    startTimeRef.current = null;
    setGenerating(false);
    setPhase(null);
    setElapsed(0);
    setTaskId(null);
  };

  const fetchTimetable = async ({ silentNotFound = false } = {}) => {
    setLoading(true);
    if (!silentNotFound) {
      setError(null);
      setDetails(null);
    }
    try {
      const data = await api.get('/api/timetable', { responseType: 'text' });
      if (!data) {
        if (!silentNotFound) {
          setError(t('timetable.no_schedule'));
        }
        setMarkdown('');
        return;
      }
      setMarkdown(data);
    } catch (err) {
      if (silentNotFound && err?.status === 404) {
        setMarkdown('');
        return;
      }
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const applyStatus = (result) => {
    if (!result || !result.status) return result;

    if (result.task_id) {
      setTaskId(result.task_id);
    }

    if (result.phase) {
      setPhase(result.phase);
    }
    if (result.phase && result.phase_details) {
      setDetails(result.phase_details);
    }

    if (result.status === 'running') {
      setGenerating(true);
      startElapsedTimer(result.created_at || null);
      return result;
    }

    if (result.status === 'success') {
      stopGeneration();
      fetchTimetable();
      return result;
    }

    if (result.status === 'error') {
      stopGeneration();
      setError(result.error);
      setDetails(result.details || result.phase_details || null);
      return result;
    }

    if (result.status === 'cancelled' || result.status === 'idle') {
      stopGeneration();
      return result;
    }

    return result;
  };

  const pollTaskStatus = async () => {
    try {
      const result = await api.get('/api/timetable/status/current');
      if (!result || !result.status) {
        pollingRef.current = setTimeout(() => pollTaskStatus(), POLL_INTERVAL_MS);
        return;
      }

      applyStatus(result);
      if (result.status === 'running') {
        pollingRef.current = setTimeout(() => pollTaskStatus(), POLL_INTERVAL_MS);
      }
    } catch {
      pollingRef.current = setTimeout(() => pollTaskStatus(), POLL_RETRY_MS);
    }
  };

  useEffect(() => {
    return () => {
      clearTimers();
    };
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (courseSelectorRef.current && !courseSelectorRef.current.contains(event.target)) {
        setShowCourseSuggestions(false);
      }
      if (teacherSelectorRef.current && !teacherSelectorRef.current.contains(event.target)) {
        setShowTeacherSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      setError(null);
      setDetails(null);
      try {
        const status = await api.get('/api/timetable/status/current');
        applyStatus(status);
        if (status?.status === 'running') {
          await fetchTimetable({ silentNotFound: true });
          pollTaskStatus();
          return;
        }
      } catch {
        // No status available; continue with timetable fetch.
      }
      await fetchTimetable();
    };

    init();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    setDetails(null);
    setMarkdown('');
    startElapsedTimer();
    try {
      const result = await api.post('/api/timetable');
      applyStatus(result);
      pollTaskStatus();
    } catch (err) {
      stopGeneration();
      setError(err.message);
      setDetails(err.details || null);
    }
  };

  const handleClear = async () => {
    setGenerating(true);
    setError(null);
    setDetails(null);
    setMarkdown('');
    startElapsedTimer();
    try {
      await api.del('/api/timetable');
      const result = await api.post('/api/timetable');
      applyStatus(result);
      pollTaskStatus();
    } catch (err) {
      stopGeneration();
      setError(err.message);
      setDetails(err.details || null);
    }
  };

  const handleCancel = async () => {
    if (!taskId) return;
    try {
      await api.post(`/api/timetable/${taskId}/cancel`);
    } catch { /* ignore */ }
    stopGeneration();
  };

  const handleDownloadMarkdown = () => {
    if (!markdown.trim()) {
      setError(t('timetable.no_content_download'));
      return;
    }

    try {
      setDownloading(true);
      const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      const date = new Date().toISOString().split('T')[0];
      const filename = (t('timetable.md_filename') || `timetable-{date}`).replace('{date}', date) + '.md';
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError((t('timetable.md_error') || 'Error downloading markdown') + ': ' + err.message);
    } finally {
      setDownloading(false);
    }
  };

  const layoutState = loading ? 'loading' : error ? 'error' : 'ready';
  const parsedSections = useMemo(() => parseTimetableSections(markdown), [markdown]);
  const courseSection = parsedSections[0] || null;
  const teacherSection = parsedSections[1] || null;
  const canRenderSections = Boolean(courseSection && teacherSection);

  const syncSelectionWithSection = (entries, setSelectedIds) => {
    if (!entries || entries.length === 0) {
      setSelectedIds([]);
      return;
    }
    const validIds = new Set(entries.map(entry => entry.id));
    setSelectedIds((prev) => {
      const filtered = prev.filter(id => validIds.has(id));
      if (filtered.length > 0) return filtered;
      return entries.map(entry => entry.id);
    });
  };

  useEffect(() => {
    syncSelectionWithSection(courseSection?.entries || [], setSelectedCourseIds);
  }, [courseSection]);

  useEffect(() => {
    syncSelectionWithSection(teacherSection?.entries || [], setSelectedTeacherIds);
  }, [teacherSection]);

  const markdownComponents = {
    td: ({ children, ...props }) => {
      const colors = new Set();
      collectSubjectEntryColors(children, colors);
      const cellStyle = { ...(props.style || {}) };
      if (colors.size === 1) {
        const [onlyColor] = Array.from(colors);
        cellStyle.backgroundColor = onlyColor;
      }
      return <td {...props} style={cellStyle}>{stripSubjectEntryInlineBg(children)}</td>;
    },
  };

  const getSelectedEntries = (section, selectedIds) => {
    if (!section || section.entries.length === 0) return [];
    const selectedSet = new Set(selectedIds);
    return section.entries.filter(entry => selectedSet.has(entry.id));
  };

  const selectedCourseEntries = getSelectedEntries(courseSection, selectedCourseIds);
  const selectedTeacherEntries = getSelectedEntries(teacherSection, selectedTeacherIds);
  const allCourseIds = courseSection?.entries.map(entry => entry.id) || [];
  const allTeacherIds = teacherSection?.entries.map(entry => entry.id) || [];
  const areAllCoursesSelected = allCourseIds.length > 0 && allCourseIds.every(id => selectedCourseIds.includes(id));
  const areAllTeachersSelected = allTeacherIds.length > 0 && allTeacherIds.every(id => selectedTeacherIds.includes(id));
  const areSomeCoursesSelected = selectedCourseIds.length > 0 && !areAllCoursesSelected;
  const areSomeTeachersSelected = selectedTeacherIds.length > 0 && !areAllTeachersSelected;

  useEffect(() => {
    if (allCoursesCheckboxRef.current) {
      allCoursesCheckboxRef.current.indeterminate = areSomeCoursesSelected;
    }
  }, [areSomeCoursesSelected]);

  useEffect(() => {
    if (allTeachersCheckboxRef.current) {
      allTeachersCheckboxRef.current.indeterminate = areSomeTeachersSelected;
    }
  }, [areSomeTeachersSelected]);

  const filterEntriesByQuery = (entries, query) => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return entries;
    return entries.filter(entry => entry.title.toLowerCase().includes(normalized));
  };

  const filteredCourseEntries = filterEntriesByQuery(courseSection?.entries || [], courseQuery);
  const filteredTeacherEntries = filterEntriesByQuery(teacherSection?.entries || [], teacherQuery);

  const toggleEntrySelection = (entryId, selectedIds, setSelectedIds) => {
    const selectedSet = new Set(selectedIds);
    if (selectedSet.has(entryId)) {
      selectedSet.delete(entryId);
    } else {
      selectedSet.add(entryId);
    }
    setSelectedIds(Array.from(selectedSet));
  };

  const handleAllSelection = (checked, allIds, setSelectedIds) => {
    if (checked) {
      setSelectedIds(allIds);
      return;
    }
    setSelectedIds([]);
  };

  const handleAutocompleteEnter = (event, entries, selectedIds, setSelectedIds) => {
    if (event.key !== 'Enter') return;
    if (!entries.length) return;
    event.preventDefault();
    const firstMatch = entries[0];
    toggleEntrySelection(firstMatch.id, selectedIds, setSelectedIds);
  };

  return (
    <>
      <SectionLayout
        title={t('nav.timetable')}
        state={layoutState}
        errorMsg={error}
        actions={
          <>
            {generating ? (
              <button onClick={handleCancel} className="btn btn--warning btn--compact">
                {t('common.cancel')}
              </button>
            ) : markdown.trim() ? (
              <button onClick={handleClear} disabled={generating} className="btn btn--danger btn--compact">
                {t('timetable.recreate')}
              </button>
            ) : (
              <button onClick={handleGenerate} disabled={generating} className="btn btn--primary btn--compact">
                {t('timetable.generate')}
              </button>
            )}
            <button
              onClick={handleDownloadMarkdown}
              disabled={downloading || loading || !!error || !markdown.trim() || generating}
              className="btn btn--secondary btn--compact"
            >
              {downloading ? t('timetable.downloading_md') : (t('timetable.download_md') || 'Download Markdown')}
            </button>
          </>
        }
      >
        {generating && (
          <div className="state-loading" role="status" aria-live="polite">
            <span>{phase === 'phase2' ? t('timetable.diagnosing_causes') : t('timetable.generating_async')}{elapsed > 0 ? ` (${elapsed}s)` : ''}</span>
          </div>
        )}
        {!loading && !error && markdown.trim() && (
          <div className="timetable-container markdown-timetable" ref={timetableRef}>
            {canRenderSections ? (
              <>
                <section className="timetable-tabs-block">
                  <h3>{courseSection.title}</h3>
                  <div
                    className="timetable-selector"
                    role="group"
                    aria-label={courseSection.title}
                    ref={courseSelectorRef}
                  >
                    <div className="timetable-selector__controls">
                      <input
                        type="search"
                        className="timetable-selector__input"
                        value={courseQuery}
                        placeholder={t('common.search_placeholder') || 'Search by name...'}
                        onFocus={() => setShowCourseSuggestions(true)}
                        onChange={(event) => {
                          setCourseQuery(event.target.value);
                          setShowCourseSuggestions(true);
                        }}
                        onKeyDown={(event) => handleAutocompleteEnter(
                          event,
                          filteredCourseEntries,
                          selectedCourseIds,
                          setSelectedCourseIds,
                        )}
                        aria-label={`${courseSection.title} ${t('common.search_placeholder') || 'Search by name...'}`}
                      />
                    </div>
                    {showCourseSuggestions && (
                      <div
                        className="timetable-selector__dropdown"
                        role="listbox"
                        aria-label={courseSection.title}
                        onMouseDown={(event) => event.preventDefault()}
                      >
                        <label
                          className={`timetable-selector__option timetable-selector__option--all ${areAllCoursesSelected ? 'selected' : ''}`}
                        >
                          <input
                            ref={allCoursesCheckboxRef}
                            type="checkbox"
                            checked={areAllCoursesSelected}
                            onChange={(event) => handleAllSelection(
                              event.target.checked,
                              allCourseIds,
                              setSelectedCourseIds,
                            )}
                            aria-label={t('common.all_courses') || 'All courses'}
                          />
                          <span>{t('common.all_courses') || 'All courses'}</span>
                        </label>
                        {filteredCourseEntries.length > 0 ? (
                          filteredCourseEntries.map((entry) => {
                            const isSelected = selectedCourseIds.includes(entry.id);
                            return (
                              <label
                                key={entry.id}
                                className={`timetable-selector__option ${isSelected ? 'selected' : ''}`}
                              >
                                <input
                                  type="checkbox"
                                  checked={isSelected}
                                  onChange={() => toggleEntrySelection(
                                    entry.id,
                                    selectedCourseIds,
                                    setSelectedCourseIds,
                                  )}
                                  aria-label={entry.title}
                                />
                                <span>{entry.title}</span>
                              </label>
                            );
                          })
                        ) : (
                          <div className="timetable-selector__empty">No results</div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="timetable-panels-group">
                    {selectedCourseEntries.map((entry) => (
                      <div
                        key={entry.id}
                        id={`course-panel-${entry.id}`}
                        role="region"
                        aria-label={entry.title}
                        className="timetable-tab-panel"
                      >
                        <h4 className="timetable-panel-title">{entry.title}</h4>
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeRaw]}
                          components={markdownComponents}
                        >
                          {entry.markdown}
                        </ReactMarkdown>
                      </div>
                    ))}
                    {selectedCourseEntries.length === 0 && (
                      <div className="timetable-selector__empty">No timetables selected</div>
                    )}
                  </div>
                </section>

                <section className="timetable-tabs-block">
                  <h3>{teacherSection.title}</h3>
                  <div
                    className="timetable-selector"
                    role="group"
                    aria-label={teacherSection.title}
                    ref={teacherSelectorRef}
                  >
                    <div className="timetable-selector__controls">
                      <input
                        type="search"
                        className="timetable-selector__input"
                        value={teacherQuery}
                        placeholder={t('common.search_placeholder') || 'Search by name...'}
                        onFocus={() => setShowTeacherSuggestions(true)}
                        onChange={(event) => {
                          setTeacherQuery(event.target.value);
                          setShowTeacherSuggestions(true);
                        }}
                        onKeyDown={(event) => handleAutocompleteEnter(
                          event,
                          filteredTeacherEntries,
                          selectedTeacherIds,
                          setSelectedTeacherIds,
                        )}
                        aria-label={`${teacherSection.title} ${t('common.search_placeholder') || 'Search by name...'}`}
                      />
                    </div>
                    {showTeacherSuggestions && (
                      <div
                        className="timetable-selector__dropdown"
                        role="listbox"
                        aria-label={teacherSection.title}
                        onMouseDown={(event) => event.preventDefault()}
                      >
                        <label
                          className={`timetable-selector__option timetable-selector__option--all ${areAllTeachersSelected ? 'selected' : ''}`}
                        >
                          <input
                            ref={allTeachersCheckboxRef}
                            type="checkbox"
                            checked={areAllTeachersSelected}
                            onChange={(event) => handleAllSelection(
                              event.target.checked,
                              allTeacherIds,
                              setSelectedTeacherIds,
                            )}
                            aria-label={t('common.all_teachers') || 'All teachers'}
                          />
                          <span>{t('common.all_teachers') || 'All teachers'}</span>
                        </label>
                        {filteredTeacherEntries.length > 0 ? (
                          filteredTeacherEntries.map((entry) => {
                            const isSelected = selectedTeacherIds.includes(entry.id);
                            return (
                              <label
                                key={entry.id}
                                className={`timetable-selector__option ${isSelected ? 'selected' : ''}`}
                              >
                                <input
                                  type="checkbox"
                                  checked={isSelected}
                                  onChange={() => toggleEntrySelection(
                                    entry.id,
                                    selectedTeacherIds,
                                    setSelectedTeacherIds,
                                  )}
                                  aria-label={entry.title}
                                />
                                <span>{entry.title}</span>
                              </label>
                            );
                          })
                        ) : (
                          <div className="timetable-selector__empty">No results</div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="timetable-panels-group">
                    {selectedTeacherEntries.map((entry) => (
                      <div
                        key={entry.id}
                        id={`teacher-panel-${entry.id}`}
                        role="region"
                        aria-label={entry.title}
                        className="timetable-tab-panel"
                      >
                        <h4 className="timetable-panel-title">{entry.title}</h4>
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeRaw]}
                          components={markdownComponents}
                        >
                          {entry.markdown}
                        </ReactMarkdown>
                      </div>
                    ))}
                    {selectedTeacherEntries.length === 0 && (
                      <div className="timetable-selector__empty">No timetables selected</div>
                    )}
                  </div>
                </section>
              </>
            ) : (
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw]}
                components={markdownComponents}
              >
                {markdown}
              </ReactMarkdown>
            )}
          </div>
        )}
      </SectionLayout>
      {details && (
        <details className="diagnostic-details" open>
          <summary>{t('timetable.diagnostic_title')}</summary>
          <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
            {details}
          </ReactMarkdown>
        </details>
      )}
    </>
  );
}

export default MarkdownTimetable;
