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
  const [clearing, setClearing] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const timetableRef = useRef();

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

  const handleClear = async () => {
    setClearing(true);
    setError(null);
    setDetails(null);
    try {
      await api.del('/api/timetable');
      await api.post('/api/timetable');
      fetchTimetable();
    } catch (err) {
      setError(err.message);
      setDetails(err.details || null);
    } finally {
      setClearing(false);
    }
  };

  const handleGenerate = async () => {
    setClearing(true);
    setError(null);
    setDetails(null);
    try {
      await api.post('/api/timetable');
      fetchTimetable();
    } catch (err) {
      setError(err.message);
      setDetails(err.details || null);
    } finally {
      setClearing(false);
    }
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
            {markdown.trim() ? (
              <button onClick={handleClear} disabled={clearing} className="btn btn--danger btn--compact">
                {clearing ? t('timetable.recreating') : t('timetable.recreate')}
              </button>
            ) : (
              <button onClick={handleGenerate} disabled={clearing} className="btn btn--primary btn--compact">
                {clearing ? t('timetable.generating') : t('timetable.generate')}
              </button>
            )}
            <button
              onClick={handleDownloadMarkdown}
              disabled={downloading || loading || !!error || !markdown.trim()}
              className="btn btn--secondary btn--compact"
            >
              {downloading ? t('timetable.downloading_md') : (t('timetable.download_md') || 'Download Markdown')}
            </button>
          </>
        }
      >
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
