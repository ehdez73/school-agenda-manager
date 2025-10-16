import React, { useEffect, useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import './MarkdownTimetable.css';
import api from '../lib/api';
import { t } from '../i18n';


function MarkdownTimetable() {
  const [markdown, setMarkdown] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [clearing, setClearing] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const timetableRef = useRef();

  const fetchTimetable = async () => {
    setLoading(true);
    setError(null);
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
    try {
      await api.del('/api/timetable');
      await api.post('/api/timetable');
      fetchTimetable();
    } catch (err) {
      setError(err.message);
    } finally {
      setClearing(false);
    }
  };

  const handleGenerate = async () => {
    setClearing(true);
    setError(null);
    try {
      await api.post('/api/timetable');
      fetchTimetable();
    } catch (err) {
      setError(err.message);
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

  return (
    <div className="markdown-timetable">
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', alignItems: 'center' }}>
        {markdown.trim() ? (
          <button onClick={handleClear} disabled={clearing} className="btn btn--danger">
            {clearing ? t('timetable.recreating') : t('timetable.recreate')}
          </button>
        ) : (
          <button onClick={handleGenerate} disabled={clearing} className="btn btn--primary">
            {clearing ? t('timetable.generating') : t('timetable.generate')}
          </button>
        )}
        <button
          onClick={handleDownloadMarkdown}
          disabled={downloading || loading || !!error || !markdown.trim()}
          className="btn"
          style={{ backgroundColor: '#0069d9', borderColor: '#0069d9', color: 'white' }}
        >
          {downloading ? t('timetable.downloading_md') : (t('timetable.download_md') || 'Download Markdown')}
        </button>
      </div>
      {loading && <p className="loading-message">{t('timetable.loading')}</p>}
      {error && (
        <div>
          <p className="error-message">{error}</p>
          {error.includes(t('timetable.no_schedule'))}
        </div>
      )}
      {!loading && !error && markdown.trim() && (
        <div className="timetable-container" ref={timetableRef}>
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeRaw]}
          >
            {markdown}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
}

export default MarkdownTimetable;
