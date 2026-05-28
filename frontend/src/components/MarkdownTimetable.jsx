import React, { useEffect, useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import './MarkdownTimetable.css';
import api from '../lib/api';
import { t } from '../i18n';
import SectionLayout from './SectionLayout';


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

  const stopGeneration = () => {
    if (pollingRef.current) clearTimeout(pollingRef.current);
    if (elapsedRef.current) clearInterval(elapsedRef.current);
    setGenerating(false);
    setPhase(null);
    setElapsed(0);
  };

  const pollTaskStatus = async (tid) => {
    try {
      const result = await api.get(`/api/timetable/status/${tid}`);
      if (!result || !result.status) {
        pollingRef.current = setTimeout(() => pollTaskStatus(tid), 2000);
        return;
      }
      if (result.phase) setPhase(result.phase);
      if (result.phase && result.phase_details) {
        setDetails(result.phase_details);
      }
      if (result.status === 'success') {
        stopGeneration();
        fetchTimetable();
        return;
      }
      if (result.status === 'error') {
        stopGeneration();
        setError(result.error);
        setDetails(result.details || result.phase_details || null);
        return;
      }
      if (result.status === 'cancelled') {
        stopGeneration();
        return;
      }
      pollingRef.current = setTimeout(() => pollTaskStatus(tid), 2000);
    } catch {
      pollingRef.current = setTimeout(() => pollTaskStatus(tid), 3000);
    }
  };

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearTimeout(pollingRef.current);
      if (elapsedRef.current) clearInterval(elapsedRef.current);
    };
  }, []);

  const fetchTimetable = async () => {
    setLoading(true);
    setError(null);
    setDetails(null);
    try {
      const data = await api.get('/api/timetable', { responseType: 'text' });
      if (!data) {
        setError(t('timetable.no_schedule'));
        setMarkdown('');
        return;
      }
      setMarkdown(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimetable();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    setDetails(null);
    setMarkdown('');
    try {
      const result = await api.post('/api/timetable');
      const tid = result.task_id;
      setTaskId(tid);
      startTimeRef.current = Date.now();
      elapsedRef.current = setInterval(() => {
        setElapsed(Math.floor((Date.now() - startTimeRef.current) / 1000));
      }, 1000);
      pollTaskStatus(tid);
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
    try {
      await api.del('/api/timetable');
      const result = await api.post('/api/timetable');
      const tid = result.task_id;
      setTaskId(tid);
      startTimeRef.current = Date.now();
      elapsedRef.current = setInterval(() => {
        setElapsed(Math.floor((Date.now() - startTimeRef.current) / 1000));
      }, 1000);
      pollTaskStatus(tid);
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
            <span>{phase === 'phase3' ? t('timetable.diagnosing_causes') : t('timetable.generating_async')}{elapsed > 0 ? ` (${elapsed}s)` : ''}</span>
          </div>
        )}
        {!loading && !error && markdown.trim() && (
          <div className="timetable-container markdown-timetable" ref={timetableRef}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
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
