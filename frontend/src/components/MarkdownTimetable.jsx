import React, { useEffect, useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import './MarkdownTimetable.css';
import api from '../lib/api';
import { t } from '../i18n';
import SectionLayout from './SectionLayout';

const POLL_INTERVAL_MS = 2000;
const POLL_RETRY_MS = 3000;


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
  const timetableRef = useRef();
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
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
              components={{
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
              }}
            >
              {markdown}
            </ReactMarkdown>
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
