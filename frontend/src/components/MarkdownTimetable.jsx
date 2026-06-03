import React, { useEffect, useMemo, useState, useRef, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import './MarkdownTimetable.css';
import api from '../lib/api';
import { t } from '../i18n';
import SectionLayout from './SectionLayout';
import ConfirmDeleteModal from './ConfirmDeleteModal';
import FormModal from './FormModal';
import Select from './Select';

const POLL_INTERVAL_MS = 4000;
const POLL_RETRY_MS = 3000;
const COURSE_SELECTION_STORAGE_KEY = 'timetable.selectedCourseIds';
const TEACHER_SELECTION_STORAGE_KEY = 'timetable.selectedTeacherIds';


function readSelectionFromSessionStorage(storageKey) {
  try {
    const rawValue = sessionStorage.getItem(storageKey);
    if (rawValue === null) return null;
    const parsedValue = JSON.parse(rawValue);
    return Array.isArray(parsedValue) ? parsedValue.map(value => String(value)) : null;
  } catch {
    return null;
  }
}


function writeSelectionToSessionStorage(storageKey, selectedIds) {
  try {
    if (selectedIds === null) {
      sessionStorage.removeItem(storageKey);
      return;
    }
    sessionStorage.setItem(storageKey, JSON.stringify(selectedIds));
  } catch {
    // Ignore storage failures in private mode or restricted environments.
  }
}


function clearSelectionFromSessionStorage(storageKey) {
  try {
    sessionStorage.removeItem(storageKey);
  } catch {
    // Ignore storage failures in private mode or restricted environments.
  }
}


function stripHtmlTags(text) {
  return text
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<[^>]+>/g, '');
}


function filterFixedRows(markdown) {
  if (!markdown) return markdown;
  return markdown.split('\n')
    .filter(line => !(line.includes('tt-fixed-slot') && line.trimStart().startsWith('|')))
    .join('\n');
}


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


function areSameSelection(currentIds, nextIds) {
  return currentIds.length === nextIds.length && currentIds.every((id, index) => id === nextIds[index]);
}


function syncSelectionWithSection(entries, currentSelectedIds, setSelectedIds) {
  if (!entries || entries.length === 0) return;
  const nextIdsWhenEmpty = entries.map(entry => entry.id);
  if (currentSelectedIds === null) {
    setSelectedIds(nextIdsWhenEmpty);
    return;
  }
  const validIds = new Set(nextIdsWhenEmpty);
  const nextSelectedIds = currentSelectedIds.filter(id => validIds.has(id));
  if (!areSameSelection(currentSelectedIds, nextSelectedIds)) {
    setSelectedIds(nextSelectedIds);
  }
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


function MarkdownTimetable({ preselectTeacher, preselectCourseGroups, preselectTeachers, onConsumePreselect, onConsumeCoursePreselect, onConsumeTeacherPreselect, onViewTeacher }) {
  const [markdown, setMarkdown] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [details, setDetails] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [phase, setPhase] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const [generatingMessage, setGeneratingMessage] = useState('');
  const [infeasibleMessage, setInfeasibleMessage] = useState('');
  const [downloading, setDownloading] = useState(false);
  const [selectedCourseIdsState, setSelectedCourseIds] = useState(() => readSelectionFromSessionStorage(COURSE_SELECTION_STORAGE_KEY));
  const [selectedTeacherIdsState, setSelectedTeacherIds] = useState(() => readSelectionFromSessionStorage(TEACHER_SELECTION_STORAGE_KEY));
  const [showRecreateModal, setShowRecreateModal] = useState(false);
  const [showCourseFixedLines, setShowCourseFixedLines] = useState(true);
  const [showTeacherFixedLines, setShowTeacherFixedLines] = useState(true);
  const [courseQuery, setCourseQuery] = useState('');
  const [teacherQuery, setTeacherQuery] = useState('');
  const [showCourseSuggestions, setShowCourseSuggestions] = useState(false);
  const [showTeacherSuggestions, setShowTeacherSuggestions] = useState(false);
  const [supportModal, setSupportModal] = useState({
    open: false,
    teacherName: null,
    teacherId: null,
    day: null,
    hour: null,
    supportId: null,
  });
  const [availableSubjects, setAvailableSubjects] = useState([]);
  const [existingSupport, setExistingSupport] = useState(null);
  const [selectedSubjectIndex, setSelectedSubjectIndex] = useState(0);
  const [hourLabel, setHourLabel] = useState(null);
  const [savingSupport, setSavingSupport] = useState(false);
  const timetableRef = useRef();
  const courseSelectorRef = useRef(null);
  const teacherSelectorRef = useRef(null);
  const allCoursesCheckboxRef = useRef(null);
  const allTeachersCheckboxRef = useRef(null);
  const pollingRef = useRef(null);
  const elapsedRef = useRef(null);
  const startTimeRef = useRef(null);

  const clearTimers = useCallback(() => {
    if (pollingRef.current) {
      clearTimeout(pollingRef.current);
      pollingRef.current = null;
    }
    if (elapsedRef.current) {
      clearInterval(elapsedRef.current);
      elapsedRef.current = null;
    }
  }, []);

  const startElapsedTimer = useCallback((createdAtSeconds = null) => {
    if (elapsedRef.current) clearInterval(elapsedRef.current);
    const startedAtMs = createdAtSeconds ? createdAtSeconds * 1000 : Date.now();
    startTimeRef.current = startedAtMs;
    setElapsed(Math.max(0, Math.floor((Date.now() - startedAtMs) / 1000)));
    elapsedRef.current = setInterval(() => {
      if (!startTimeRef.current) return;
      setElapsed(Math.max(0, Math.floor((Date.now() - startTimeRef.current) / 1000)));
    }, 1000);
  }, []);

  const pickRandomGeneratingMessage = useCallback(() => {
    const messages = t('timetable.generating_async');
    if (Array.isArray(messages) && messages.length > 0) {
      return messages[Math.floor(Math.random() * messages.length)];
    }
    return messages;
  }, []);

  const pickRandomInfeasibleMessage = useCallback(() => {
    const messages = t('timetable.infeasible_detected');
    if (Array.isArray(messages) && messages.length > 0) {
      return messages[Math.floor(Math.random() * messages.length)];
    }
    return messages;
  }, []);

  const stopGeneration = useCallback(() => {
    clearTimers();
    startTimeRef.current = null;
    setGenerating(false);
    setPhase(null);
    setElapsed(0);
    setTaskId(null);
    setGeneratingMessage('');
    setInfeasibleMessage('');
  }, [clearTimers]);

  const resetPersistedSelections = () => {
    clearSelectionFromSessionStorage(COURSE_SELECTION_STORAGE_KEY);
    clearSelectionFromSessionStorage(TEACHER_SELECTION_STORAGE_KEY);
    setSelectedCourseIds(null);
    setSelectedTeacherIds(null);
    setCourseQuery('');
    setTeacherQuery('');
    setShowCourseSuggestions(false);
    setShowTeacherSuggestions(false);
  };

  const refreshTimetableSilent = async () => {
    try {
      const data = await api.get('/timetable', { responseType: 'text', cacheBust: true });
      if (data) setMarkdown(data);
    } catch {
      // silent — don't disrupt the current view
    }
  };

  const fetchTimetable = useCallback(async ({ silentNotFound = false } = {}) => {
    setLoading(true);
    if (!silentNotFound) {
      setError(null);
      setDetails(null);
    }
    try {
      const data = await api.get('/timetable', { responseType: 'text' });
      if (!data) {
        if (!silentNotFound) {
          setError(t('timetable.no_schedule'));
        }
        setMarkdown('');
        return false;
      }
      setMarkdown(data);
      return true;
    } catch (err) {
      if (silentNotFound && err?.status === 404) {
        setMarkdown('');
        return false;
      }
      if (!silentNotFound) {
        setError(err.message);
      }
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const applyStatus = useCallback((result) => {
    if (!result || !result.status) return result;

    if (result.task_id) {
      setTaskId(result.task_id);
    }

    if (result.phase) {
      setPhase(result.phase);
      if (result.phase === 'infeasible') {
        setInfeasibleMessage(pickRandomInfeasibleMessage());
      }
    }
    if (result.phase && result.phase_details) {
      setDetails(result.phase_details);
    }

    if (result.status === 'running') {
      setGenerating(true);
      setGeneratingMessage(pickRandomGeneratingMessage());
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
  }, [fetchTimetable, pickRandomInfeasibleMessage, pickRandomGeneratingMessage, startElapsedTimer, stopGeneration]);

  const pollTaskStatus = useCallback(async () => {
    try {
      const result = await api.get('/timetable/status/current');
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
  }, [applyStatus]);

  useEffect(() => {
    return () => {
      clearTimers();
    };
  }, [clearTimers]);

  useEffect(() => {
    writeSelectionToSessionStorage(COURSE_SELECTION_STORAGE_KEY, selectedCourseIdsState);
  }, [selectedCourseIdsState]);

  useEffect(() => {
    writeSelectionToSessionStorage(TEACHER_SELECTION_STORAGE_KEY, selectedTeacherIdsState);
  }, [selectedTeacherIdsState]);

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
        const status = await api.get('/timetable/status/current');
        applyStatus(status);
        if (status?.status === 'running') {
          await fetchTimetable({ silentNotFound: true });
          pollTaskStatus();
          return;
        }
        if (status?.status === 'error') {
          setLoading(false);
          return;
        }
      } catch {
        // No status available; continue with timetable fetch.
      }
      const hasTimetable = await fetchTimetable();
      if (!hasTimetable) {
        try {
          const errResult = await api.get('/timetable/error');
          if (errResult?.message) {
            setError(errResult.message);
            setDetails(errResult.details || null);
          }
        } catch {
          // No persisted error; keep the default "no schedule" message.
        }
      }
    };

    init();
  }, [applyStatus, pollTaskStatus, fetchTimetable]);

  const handleGenerate = async () => {
    resetPersistedSelections();
    setGenerating(true);
    setGeneratingMessage(pickRandomGeneratingMessage());
    setError(null);
    setDetails(null);
    setMarkdown('');
    startElapsedTimer();
    try {
      const result = await api.post('/timetable');
      applyStatus(result);
      pollTaskStatus();
    } catch (err) {
      stopGeneration();
      setError(err.message);
      setDetails(err.details || null);
    }
  };

  const handleRecreateClick = () => {
    setShowRecreateModal(true);
  };

  const cancelRecreate = () => {
    setShowRecreateModal(false);
  };

  const confirmRecreate = async () => {
    setShowRecreateModal(false);
    resetPersistedSelections();
    setGenerating(true);
    setGeneratingMessage(pickRandomGeneratingMessage());
    setError(null);
    setDetails(null);
    setMarkdown('');
    startElapsedTimer();
    try {
      await api.del('/timetable');
      const result = await api.post('/timetable');
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
      await api.post(`/timetable/${taskId}/cancel`);
    } catch { /* ignore */ }
    stopGeneration();
  };

  const buildFilteredMarkdown = () => {
    const parts = [];
    if (courseSection && selectedCourseEntries.length > 0) {
      parts.push(`## ${courseSection.title}`);
      selectedCourseEntries.forEach(entry => {
        const md = showCourseFixedLines ? entry.markdown : filterFixedRows(entry.markdown);
        parts.push(`\n### ${entry.title}\n${md}`);
      });
    }
    if (teacherSection && selectedTeacherEntries.length > 0) {
      parts.push(`\n## ${teacherSection.title}`);
      selectedTeacherEntries.forEach(entry => {
        const md = showTeacherFixedLines ? entry.markdown : filterFixedRows(entry.markdown);
        parts.push(`\n### ${entry.title}\n${md}`);
      });
    }
    return parts.join('\n');
  };

  const handleDownloadMarkdown = () => {
    const content = stripHtmlTags(buildFilteredMarkdown());
    if (!content.trim()) {
      setError(t('timetable.no_content_download'));
      return;
    }

    try {
      setDownloading(true);
      const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
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

  function consolidateCellBg(cellHtml) {
    const colorRe = /background-color:\s*(#[0-9a-fA-F]{6})/g;
    const colors = [];
    let m;
    while ((m = colorRe.exec(cellHtml)) !== null) {
      colors.push(m[1].toLowerCase());
    }
    if (colors.length === 0) return { html: cellHtml, bgColor: null };
    const unique = [...new Set(colors)];
    if (unique.length === 1) {
      let cleaned = cellHtml.replace(/background-color:\s*#[0-9a-fA-F]{6};?\s*/gi, '');
      cleaned = cleaned.replace(/\s*style="\s*"/g, '');
      return { html: cleaned, bgColor: unique[0] };
    }
    return { html: cellHtml, bgColor: null };
  }

  const pipeTableToHtml = (md) => {
    const lines = md.split('\n');
    const result = [];
    let inTable = false;
    let tableRows = [];

    const flushTable = () => {
      if (!inTable) return;
      if (tableRows.length > 1) {
        result.push('<table>');
        tableRows.forEach((row, i) => {
          const cells = row.split('|').slice(1, -1).map(c => c.trim());
          const tag = i === 1 ? 'th' : 'td';
          if (i === 1) return;
          const processedCells = cells.map(c => {
            const { html, bgColor } = consolidateCellBg(c);
            const styleAttr = bgColor ? ` style="background-color: ${bgColor};"` : '';
            return `<${tag}${styleAttr}>${html}</${tag}>`;
          });
          result.push(`<tr>${processedCells.join('')}</tr>`);
        });
        result.push('</table>');
      }
      inTable = false;
      tableRows = [];
    };

    for (const line of lines) {
      const trimmed = line.trim();
      const isPipeRow = trimmed.startsWith('|') && trimmed.endsWith('|');
      const isSeparator = isPipeRow && /^[\s|:-]+$/.test(trimmed);

      if (isPipeRow && !isSeparator) {
        if (!inTable) {
          inTable = true;
          tableRows = [];
        }
        tableRows.push(line);
        continue;
      }
      flushTable();
      if (isSeparator) continue;
      const h2 = line.match(/^## (.+)/);
      if (h2) { result.push(`<h2>${h2[1]}</h2>`); continue; }
      const h3 = line.match(/^### (.+)/);
      if (h3) { result.push(`<h3>${h3[1]}</h3>`); continue; }
      if (trimmed) {
        result.push(`<p>${trimmed}</p>`);
      }
    }
    flushTable();
    return result.join('\n');
  };

  const handlePrint = () => {
    const content = buildFilteredMarkdown();
    if (!content.trim()) {
      setError(t('timetable.no_content_print'));
      return;
    }

    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      setError(t('timetable.no_content_print'));
      return;
    }
    printWindow.document.write(`<!DOCTYPE html><html><head><title>${t('timetable.print_md')}</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; line-height: 1.5; }
  table { border-collapse: collapse; margin: 12px 0; width: 100%; table-layout: fixed; }
  th, td { border: 1px solid #999; padding: 4px 6px; text-align: left; vertical-align: top; word-wrap: break-word; font-size: 9px; }
  th { background: #f5f5f5; font-weight: 600; }
  .tt-subject-entry { display: inline-block; padding: 1px 3px; border-radius: 2px; margin: 1px 0; font-size: 9px; }
  .tt-fixed-slot { display: inline-block; padding: 2px 4px; font-weight: 700; font-style: italic; color: #666; border-radius: 3px; font-size: 9px; }
  h2 { font-size: 16px; margin-top: 18px; }
  h3 { font-size: 14px; margin-top: 14px; }
  @page { size: landscape; margin: 1cm; }
  @media print { body { padding: 0; } }
</style></head><body>
`);
    const html = pipeTableToHtml(content);
    printWindow.document.write(html);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => printWindow.print(), 300);
  };

  const layoutState = loading ? 'loading' : error ? 'error' : 'ready';
  const parsedSections = useMemo(() => parseTimetableSections(markdown), [markdown]);
  const courseSection = parsedSections[0] || null;
  const teacherSection = parsedSections[1] || null;
  const canRenderSections = Boolean(courseSection && teacherSection);

  useEffect(() => {
    syncSelectionWithSection(courseSection?.entries || [], selectedCourseIdsState, setSelectedCourseIds);
  }, [courseSection, selectedCourseIdsState]);

  useEffect(() => {
    syncSelectionWithSection(teacherSection?.entries || [], selectedTeacherIdsState, setSelectedTeacherIds);
  }, [teacherSection, selectedTeacherIdsState]);

  useEffect(() => {
    if (!preselectTeacher || !teacherSection || teacherSection.entries.length === 0) return;
    const match = teacherSection.entries.find(entry =>
      entry.title.toLowerCase().startsWith(preselectTeacher.toLowerCase()) ||
      entry.title.toLowerCase().replace(/ — .*/, '').trim() === preselectTeacher.toLowerCase()
    );
    if (match) {
      setSelectedTeacherIds([match.id]);
      setTimeout(() => {
        const el = document.getElementById(`teacher-panel-${match.id}`);
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
    onConsumePreselect();
  }, [preselectTeacher, teacherSection, onConsumePreselect]);

  useEffect(() => {
    if (!preselectCourseGroups || !courseSection || courseSection.entries.length === 0 || preselectCourseGroups.length === 0) return;
    const matchedIds = courseSection.entries
      .filter(entry => {
        const courseLine = entry.title.replace(/^.*?:\s*/, '').replace(/ —.*/, '').trim();
        return preselectCourseGroups.some(group => courseLine === group);
      })
      .map(entry => entry.id);
    if (matchedIds.length > 0) {
      setSelectedCourseIds(matchedIds);
    }
    if (onConsumeCoursePreselect) onConsumeCoursePreselect();
  }, [preselectCourseGroups, courseSection, onConsumeCoursePreselect]);

  useEffect(() => {
    if (!preselectTeachers || !teacherSection || teacherSection.entries.length === 0 || preselectTeachers.length === 0) return;
    const matchedIds = teacherSection.entries
      .filter(entry => {
        const teacherName = entry.title.replace(/ — .*/, '').trim();
        return preselectTeachers.some(name => teacherName.toLowerCase() === name.toLowerCase());
      })
      .map(entry => entry.id);
    if (matchedIds.length > 0) {
      setSelectedTeacherIds(matchedIds);
    }
    if (onConsumeTeacherPreselect) onConsumeTeacherPreselect();
  }, [preselectTeachers, teacherSection, onConsumeTeacherPreselect]);

function hasConflictChild(node) {
  if (node === null || node === undefined || typeof node === 'boolean') return false;
  if (Array.isArray(node)) return node.some(child => hasConflictChild(child));
  if (typeof node !== 'object') return false;
  const className = node?.props?.className || '';
  if (typeof className === 'string') {
    const classes = className.split(' ');
    if (classes.includes('tt-support-conflict') || classes.includes('tt-subject-conflict')) return true;
  }
  return hasConflictChild(node?.props?.children);
}

  const markdownComponents = {
    td: ({ children, ...props }) => {
      const colors = new Set();
      collectSubjectEntryColors(children, colors);
      const cellStyle = { ...(props.style || {}) };
      if (hasConflictChild(children)) {
        cellStyle.backgroundColor = '#eb5252';
      } else if (colors.size === 1) {
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

  const selectedCourseIds = selectedCourseIdsState ?? [];
  const selectedTeacherIds = selectedTeacherIdsState ?? [];
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

  const handleSidebarScroll = (entryId, type) => {
    const el = document.getElementById(`${type}-panel-${entryId}`);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const sortAvailableSubjects = (subjects) => {
    return [...subjects].sort((left, right) => {
      const subjectComparison = (left.subject_name || '').localeCompare(right.subject_name || '', undefined, {
        numeric: true,
        sensitivity: 'base',
      });
      if (subjectComparison !== 0) return subjectComparison;

      return (left.course_line || '').localeCompare(right.course_line || '', undefined, {
        numeric: true,
        sensitivity: 'base',
      });
    });
  };

  const getSupportSubjectKey = (subject) => `${subject.subject_id}:${subject.course_id}:${subject.line}`;

  const openSupportModal = async (teacherName, day, hour, supportId) => {
    setSavingSupport(false);
    try {
      const data = await api.get(`/timetable/gaps?teacher_name=${encodeURIComponent(teacherName)}&day=${day}&hour=${hour}`);
      const existingSupportData = data.existing_support || null;
      let subjects = sortAvailableSubjects(data.available_subjects || []);

      if (existingSupportData) {
        const currentKey = getSupportSubjectKey(existingSupportData);
        if (!subjects.some(subject => getSupportSubjectKey(subject) === currentKey)) {
          subjects = sortAvailableSubjects([...subjects, existingSupportData]);
        }
      }

      setAvailableSubjects(subjects);
      setExistingSupport(existingSupportData);
      setHourLabel(data.hour_label || null);
      setSelectedSubjectIndex(() => {
        if (!existingSupportData) return 0;
        const currentKey = getSupportSubjectKey(existingSupportData);
        const selectedIndex = subjects.findIndex(subject => getSupportSubjectKey(subject) === currentKey);
        return selectedIndex >= 0 ? selectedIndex : 0;
      });
      setSupportModal({
        open: true,
        teacherName,
        teacherId: data.teacher_id,
        day,
        hour,
        supportId,
      });
    } catch {
      setAvailableSubjects([]);
      setExistingSupport(null);
      setHourLabel(null);
      setSelectedSubjectIndex(0);
      setSupportModal({ open: true, teacherName, teacherId: null, day, hour, supportId });
    }
  };

  const handleTimetableClick = (e) => {
    const gap = e.target.closest('.tt-gap');
    if (gap) {
      const teacherName = gap.dataset.teacher;
      const day = parseInt(gap.dataset.day, 10);
      const hour = parseInt(gap.dataset.hour, 10);
      openSupportModal(teacherName, day, hour, null);
      return;
    }
    const supportEntry = e.target.closest('.tt-support-entry');
    if (supportEntry) {
      const supportId = parseInt(supportEntry.dataset.supportId, 10);
      const teacherName = supportEntry.dataset.teacher;
      const day = parseInt(supportEntry.dataset.day, 10);
      const hour = parseInt(supportEntry.dataset.hour, 10);
      openSupportModal(teacherName, day, hour, supportId);
      return;
    }
  };

  const handleAssignSupport = async () => {
    if (availableSubjects.length === 0) return;
    const subj = availableSubjects[selectedSubjectIndex];
    if (!subj || !supportModal.teacherId) return;
    setSavingSupport(true);
    try {
      if (supportModal.supportId) {
        await api.del(`/support/${supportModal.supportId}`);
      }
      await api.post('/support', {
        teacher_id: supportModal.teacherId,
        day: supportModal.day,
        hour: supportModal.hour,
        subject_id: subj.subject_id,
        course_id: subj.course_id,
        line: subj.line,
      });
      setSupportModal(prev => ({ ...prev, open: false }));
      await refreshTimetableSilent();
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingSupport(false);
    }
  };

  const handleRemoveSupport = async () => {
    if (!existingSupport?.id) return;
    setSavingSupport(true);
    try {
      await api.del(`/support/${existingSupport.id}`);
      setSupportModal(prev => ({ ...prev, open: false }));
      await refreshTimetableSilent();
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingSupport(false);
    }
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
              <button onClick={handleRecreateClick} disabled={generating} className="btn btn--danger btn--compact">
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
              aria-label={t('timetable.download_md') || 'Download Markdown'}
              title={t('timetable.download_md') || 'Download Markdown'}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </button>
            <button
              onClick={handlePrint}
              disabled={loading || !!error || !markdown.trim() || generating}
              className="btn btn--secondary btn--compact"
              aria-label={t('timetable.print_md') || 'Print'}
              title={t('timetable.print_md') || 'Print'}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="6 9 6 2 18 2 18 9"/>
                <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
                <rect x="6" y="14" width="12" height="8"/>
              </svg>
            </button>
          </>
        }
      >
        {generating && (
          <div className="state-loading" role="status" aria-live="polite">
            <span>{phase === 'infeasible' ? infeasibleMessage : phase === 'phase2' || phase === 'phase3' ? t('timetable.diagnosing_causes') : generatingMessage}{elapsed > 0 ? ` (${elapsed}s)` : ''}</span>
          </div>
        )}
        {!loading && !error && markdown.trim() && (
          <div className="timetable-with-sidebar">
            {canRenderSections && (
              <aside className="timetable-sidebar">
                <div className="timetable-sidebar__group">
                  <h4
                    className="timetable-sidebar__heading"
                    onClick={() => document.getElementById('course-section-title')?.scrollIntoView({ behavior: 'smooth', block: 'start' })}
                  >
                    {courseSection.title}
                  </h4>
                  {selectedCourseEntries.length > 0 && (
                    <ul className="timetable-sidebar__list">
                      {selectedCourseEntries.map(entry => (
                        <li key={entry.id}>
                          <span
                            className="timetable-sidebar__item"
                            onClick={() => handleSidebarScroll(entry.id, 'course')}
                            onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSidebarScroll(entry.id, 'course'); } }}
                            tabIndex={0}
                            role="button"
                          >
                            {entry.title.replace(/ — .*/, '')}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
                <div className="timetable-sidebar__group">
                  <h4
                    className="timetable-sidebar__heading"
                    onClick={() => document.getElementById('teacher-section-title')?.scrollIntoView({ behavior: 'smooth', block: 'start' })}
                  >
                    {teacherSection.title}
                  </h4>
                    {selectedTeacherEntries.length > 0 && (
                    <ul className="timetable-sidebar__list">
                      {selectedTeacherEntries.map(entry => (
                        <li key={entry.id} className="timetable-sidebar__teacher-item">
                          <span
                            className="timetable-sidebar__item"
                            onClick={() => handleSidebarScroll(entry.id, 'teacher')}
                            onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSidebarScroll(entry.id, 'teacher'); } }}
                            tabIndex={0}
                            role="button"
                          >
                            {entry.title.replace(/ — .*/, '')}
                          </span>
                          {onViewTeacher && (
                            <button
                              className="timetable-sidebar__edit-btn"
                              onClick={(e) => { e.stopPropagation(); onViewTeacher(entry.title.replace(/ — .*/, '')); }}
                              title={t('timetable.edit_teacher')}
                              aria-label={t('timetable.edit_teacher')}
                            >
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                              </svg>
                            </button>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </aside>
            )}
            <div className="timetable-container markdown-timetable" ref={timetableRef} onClick={handleTimetableClick}>
              {canRenderSections ? (
                <div className="timetable-content">
                <section className="timetable-tabs-block">
                  <h3 id="course-section-title">{courseSection.title}</h3>
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
                      <label className="timetable-fixed-toggle">
                        <input
                          type="checkbox"
                          checked={showCourseFixedLines}
                          onChange={(e) => setShowCourseFixedLines(e.target.checked)}
                        />
                        <span className="timetable-fixed-toggle__slider"></span>
                        <span className="timetable-fixed-toggle__label">{t('timetable.show_course_fixed')}</span>
                      </label>
                    </div>
                    {showCourseSuggestions && (
                      <div
                        className="timetable-selector__dropdown"
                        role="listbox"
                        aria-label={courseSection.title}
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
                          <div className="timetable-selector__empty">{t('common.no_results')}</div>
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
                          {showCourseFixedLines ? entry.markdown : filterFixedRows(entry.markdown)}
                        </ReactMarkdown>
                      </div>
                    ))}
                    {selectedCourseEntries.length === 0 && (
                          <div className="timetable-selector__empty">{t('timetable.no_timetables_selected')}</div>
                    )}
                  </div>
                </section>

                <section className="timetable-tabs-block">
                  <h3 id="teacher-section-title">{teacherSection.title}</h3>
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
                      <label className="timetable-fixed-toggle">
                        <input
                          type="checkbox"
                          checked={showTeacherFixedLines}
                          onChange={(e) => setShowTeacherFixedLines(e.target.checked)}
                        />
                        <span className="timetable-fixed-toggle__slider"></span>
                        <span className="timetable-fixed-toggle__label">{t('timetable.show_teacher_fixed')}</span>
                      </label>
                    </div>
                    {showTeacherSuggestions && (
                      <div
                        className="timetable-selector__dropdown"
                        role="listbox"
                        aria-label={teacherSection.title}
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
                                {onViewTeacher && (
                                  <button
                                    className="timetable-selector__edit-btn"
                                    onClick={(e) => { e.stopPropagation(); e.preventDefault(); onViewTeacher(entry.title.replace(/ — .*/, '')); }}
                                    title={t('timetable.edit_teacher')}
                                    aria-label={t('timetable.edit_teacher')}
                                  >
                                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                                    </svg>
                                  </button>
                                )}
                              </label>
                            );
                          })
                        ) : (
                          <div className="timetable-selector__empty">{t('common.no_results')}</div>
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
                        <h4 className="timetable-panel-title">
                        {onViewTeacher ? (
                          <span
                            className="timetable-panel-title__link"
                            onClick={(e) => { e.stopPropagation(); onViewTeacher(entry.title.replace(/ — .*/, '')); }}
                            title={t('timetable.edit_teacher')}
                          >
                            {entry.title}
                          </span>
                        ) : (
                          entry.title
                        )}
                      </h4>
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeRaw]}
                          components={markdownComponents}
                        >
                          {showTeacherFixedLines ? entry.markdown : filterFixedRows(entry.markdown)}
                        </ReactMarkdown>
                      </div>
                    ))}
                    {selectedTeacherEntries.length === 0 && (
                          <div className="timetable-selector__empty">{t('timetable.no_timetables_selected')}</div>
                    )}
                  </div>
                </section>
              </div>
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
      <ConfirmDeleteModal
        open={showRecreateModal}
        entity={t('nav.timetable')}
        text={t('timetable.confirm_recreate')}
        confirmText={t('timetable.recreate')}
        onConfirm={confirmRecreate}
        onCancel={cancelRecreate}
      />
      <FormModal
        open={supportModal.open}
        onClose={() => setSupportModal(prev => ({ ...prev, open: false }))}
        className="form-modal--support"
      >
        <h3>{t('timetable.support_modal_title')}</h3>
        <p>
          <strong>{supportModal.teacherName}</strong>
          {' — '}
          {supportModal.day != null && t(`day.${supportModal.day}`)}
          {' - '}
          {hourLabel || t('hours.label', { n: (supportModal.hour != null ? supportModal.hour + 1 : '') })}
        </p>
        {existingSupport ? (
          <p className="form-group">
            <span className="form-group__label">{t('timetable.support_modal_current')}</span>
            <strong>{existingSupport.course_line}: {existingSupport.subject_name}</strong>
          </p>
        ) : null}
        {availableSubjects.length > 0 ? (
          <div className="form-group">
            <label className="form-group__label">{t('timetable.support_modal_select')}</label>
            <Select
              value={String(selectedSubjectIndex)}
              onChange={(e) => setSelectedSubjectIndex(parseInt(e.target.value, 10))}
              options={availableSubjects.map((s, i) => ({
                value: String(i),
                label: `${s.subject_name} — ${s.course_line}`
              }))}
            />
          </div>
        ) : (
          <p>{t('timetable.support_modal_no_subjects')}</p>
        )}
        <div className="form-actions">
          <button
            className="btn btn--secondary"
            onClick={() => setSupportModal(prev => ({ ...prev, open: false }))}
          >
            {t('timetable.support_modal_cancel')}
          </button>
          {existingSupport ? (
            <button
              className="btn btn--danger"
              onClick={handleRemoveSupport}
              disabled={savingSupport}
            >
              {savingSupport ? t('timetable.support_modal_saving') : t('timetable.support_modal_remove')}
            </button>
          ) : null}
          {availableSubjects.length > 0 ? (
            <button
              className="btn btn--primary"
              onClick={handleAssignSupport}
              disabled={savingSupport}
            >
              {savingSupport ? t('timetable.support_modal_saving') : t('timetable.support_modal_assign')}
            </button>
          ) : null}
        </div>
      </FormModal>
    </>
  );
}

export default MarkdownTimetable;
