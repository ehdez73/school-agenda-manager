import React, { useEffect, useState } from 'react';
import './ConfigForm.css';
import HourNames from './HourNames';
import DayIndices from './DayIndices';
import api from '../lib/api';
import { t } from '../i18n';

export default function ConfigForm() {
  const [classesPerDay, setClassesPerDay] = useState(5);
  const [daysPerWeek, setDaysPerWeek] = useState(5);
  const [hourNames, setHourNames] = useState(() => ["9:00", "10:00", "11:00", "12:00", "13:00"]);
  const [dayIndices, setDayIndices] = useState(() => [0, 1, 2, 3, 4]);
  // when true, skip the automatic resize to avoid overwriting server values right after save
  const [suppressResize, setSuppressResize] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [exportLoading, setExportLoading] = useState(false);
  const [exportMessage, setExportMessage] = useState('');
  const [activeTab, setActiveTab] = useState('days');

  useEffect(() => {
    api.get('/config').then(data => {
      setClassesPerDay(data.classes_per_day);
      setDaysPerWeek(data.days_per_week);
      setSuppressResize(true);
      setHourNames(data.hour_names && data.hour_names.length ? data.hour_names : Array.from({ length: data.classes_per_day || 5 }, (_, i) => `Hora ${i + 1}`));
      setDayIndices(data.day_indices && data.day_indices.length ? data.day_indices : Array.from({ length: data.days_per_week || 5 }, (_, i) => i));
      setTimeout(() => setSuppressResize(false), 0);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  function handleSubmit(e) {
    e.preventDefault();

    // Validate days_per_week
    const daysNum = Number(daysPerWeek);
    if (isNaN(daysNum) || daysNum < 1 || daysNum > 7) {
      setMessage(t('config.invalid_days_per_week'));
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    // Validate unique day indices
    const uniqueIndices = new Set(dayIndices);
    if (uniqueIndices.size !== dayIndices.length) {
      setMessage(t('config.duplicate_days'));
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    setLoading(true);
    api.post('/config', { classes_per_day: Number(classesPerDay), days_per_week: daysNum, hour_names: hourNames, day_indices: dayIndices })
      .then(data => {
        setClassesPerDay(data.classes_per_day);
        setDaysPerWeek(data.days_per_week);
        setSuppressResize(true);
        setHourNames(data.hour_names && data.hour_names.length ? data.hour_names : Array.from({ length: data.classes_per_day || 5 }, (_, i) => `Hora ${i + 1}`));
        setDayIndices(data.day_indices && data.day_indices.length ? data.day_indices : Array.from({ length: data.days_per_week || 5 }, (_, i) => i));
        setTimeout(() => setSuppressResize(false), 0);
        setMessage(t('config.saved'));
        setLoading(false);
        setTimeout(() => setMessage(''), 2000);
      })
      .catch(err => {
        setMessage(err.message || t('config.saving_error'));
        setLoading(false);
        setTimeout(() => setMessage(''), 3000);
      });
  }

  const handleExport = async () => {
    setExportLoading(true);
    setExportMessage('');
    try {
      const text = await api.get('/api/export', { responseType: 'text', cacheBust: true });
      const blob = new Blob([text], { type: 'application/json;charset=utf-8' });
      const downloadUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = 'agenda_export.json';
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(downloadUrl);
      setExportMessage(t('common.export_success'));
    } catch (err) {
      setExportMessage(err.message || String(err));
    } finally {
      setExportLoading(false);
      setTimeout(() => setExportMessage(''), 4000);
    }
  };

  const handleImportFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setExportLoading(true);
    setExportMessage('');
    try {
      const text = await file.text();
      const jsonData = JSON.parse(text);
      await api.post('/api/import', jsonData);
      setExportMessage(t('common.import_success'));
      // Reload config after successful import
      window.location.reload();
    } catch (err) {
      setExportMessage(err.message || String(err));
    } finally {
      setExportLoading(false);
      setTimeout(() => setExportMessage(''), 4000);
    }
  };

  const handleClearData = async () => {
    const confirmed = window.confirm(t('config.confirm_clear'));

    if (!confirmed) return;

    setExportLoading(true);
    setExportMessage('');
    try {
      await api.del('/api/clear-all');
      setExportMessage(t('common.clear_success'));
      // Reload page after successful clear
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (err) {
      setExportMessage(err.message || String(err));
    } finally {
      setExportLoading(false);
      setTimeout(() => setExportMessage(''), 4000);
    }
  };

  return (
    <div className="config-form-container">
      <h2 className="config-form-title">{t('config.title')}</h2>

      {/* Tabs */}
      <div className="config-tabs">
        <button
          className={`config-tab ${activeTab === 'days' ? 'active' : ''}`}
          onClick={() => setActiveTab('days')}
        >
          {t('config.tab_days')}
        </button>
        <button
          className={`config-tab ${activeTab === 'hours' ? 'active' : ''}`}
          onClick={() => setActiveTab('hours')}
        >
          {t('config.tab_hours')}
        </button>
        <button
          className={`config-tab ${activeTab === 'backup' ? 'active' : ''}`}
          onClick={() => setActiveTab('backup')}
        >
          {t('config.tab_backup')}
        </button>
      </div>

      {/* General Tab */}
      {activeTab === 'days' && (
        <form onSubmit={handleSubmit}>
          <label className="config-form-label">
            {t('config.days_per_week')}
            <input
              type="number"
              min={1}
              max={7}
              value={daysPerWeek}
              onChange={e => setDaysPerWeek(e.target.value)}
              required
              className="config-form-input"
            />
          </label>
          <DayIndices daysPerWeek={daysPerWeek} dayIndices={dayIndices} setDayIndices={setDayIndices} suppressResize={suppressResize} />



          <button type="submit" className="config-form-btn" disabled={loading}>
            {t('common.save')}
          </button>
          {message && <div className="config-form-message">{message}</div>}
        </form>
      )}

      {/* Hours Tab */}
      {activeTab === 'hours' && (
        <form onSubmit={handleSubmit}>

          <label className="config-form-label">
            {t('config.classes_per_day')}
            <input
              type="number"
              min={1}
              value={classesPerDay}
              onChange={e => setClassesPerDay(e.target.value)}
              required
              className="config-form-input"
            />
          </label>
          <HourNames classesPerDay={classesPerDay} hourNames={hourNames} setHourNames={setHourNames} suppressResize={suppressResize} />
          <button type="submit" className="config-form-btn" disabled={loading}>
            {t('common.save')}
          </button>
          {message && <div className="config-form-message">{message}</div>}
        </form>
      )}

      {/* Backup Tab */}
      {activeTab === 'backup' && (
        <div className="backup-section">
          <h3>{t('config.backup_title')}</h3>
          <p style={{ marginBottom: '1rem', color: '#666', fontSize: '0.9rem' }}>
            {t('config.backup_desc')}
          </p>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <button onClick={handleExport} disabled={exportLoading} className="config-form-btn">
              {exportLoading ? t('common.processing') : t('config.export')}
            </button>
            <div style={{ display: 'inline-block' }}>
              <input
                type="file"
                accept=".json,application/json"
                onChange={handleImportFile}
                style={{ display: 'none' }}
                id="import-file-input"
              />
              <button
                className="config-form-btn"
                disabled={exportLoading}
                onClick={() => document.getElementById('import-file-input').click()}
                style={{ backgroundColor: '#6c757d' }}
              >
                {exportLoading ? t('common.processing') : t('config.import')}
              </button>
            </div>
            <button
              onClick={handleClearData}
              disabled={exportLoading}
              className="config-form-btn"
              style={{ backgroundColor: '#dc3545', borderColor: '#dc3545' }}
            >
              {exportLoading ? t('common.processing') : t('config.clear')}
            </button>
          </div>
          {exportMessage && <div className="config-form-message" style={{ marginTop: '1rem' }}>{exportMessage}</div>}
        </div>
      )}
    </div>
  );
}
