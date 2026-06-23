import { useEffect, useState, useCallback, forwardRef, useImperativeHandle } from 'react';
import api from '../lib/api';
import { t } from '../i18n';
import './TeacherGridTimetable.css';

const DEFAULT_DAY_COLORS = {
  '0': '#e3f2fd',
  '1': '#fff3e0',
  '2': '#e8f5e9',
  '3': '#fce4ec',
  '4': '#f3e5f5',
  '5': '#e0f2f1',
  '6': '#fff8e1',
};

const TeacherGridTimetable = forwardRef(function TeacherGridTimetable({ onViewTeacherTimetable }, ref) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDays, setSelectedDays] = useState(null);
  useEffect(() => {
    setLoading(true);
    setError(null);
    api.get('/timetable/teacher-grid')
      .then(res => {
        setData(res);
        setSelectedDays(new Set(res.day_indices.map(String)));
      })
      .catch(err => {
        if (err.status === 404) {
          setError(t('timetable.teacher_staff_no_data'));
        } else {
          setError(err.message);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const toggleDay = useCallback((dayIdx) => {
    setSelectedDays(prev => {
      const next = new Set(prev);
      if (next.has(dayIdx)) {
        next.delete(dayIdx);
      } else {
        next.add(dayIdx);
      }
      return next;
    });
  }, []);

  const toggleAllDays = useCallback((checked) => {
    if (checked && data) {
      setSelectedDays(new Set(data.day_indices.map(String)));
    } else {
      setSelectedDays(new Set());
    }
  }, [data]);

  const getDayColor = useCallback((dayIdx) => {
    if (!data) return 'transparent';
    const c = (data.day_colors || {})[String(dayIdx)];
    if (c && c !== '#ffffff' && c !== '#fff' && c !== '#ffffffff') return c;
    return DEFAULT_DAY_COLORS[String(dayIdx)] || 'transparent';
  }, [data]);

  const buildMarkdownForDownload = useCallback(() => {
    if (!data) return '';
    const { teachers, day_indices, day_names, hour_names, grid } = data;

    let md = '';
    day_indices.forEach(d => {
      if (!selectedDays.has(String(d))) return;
      const dayName = day_names[day_indices.indexOf(d)] || t(`day.${d}`);
      md += `## ${dayName}\n\n`;

      const headers = [t('timetable.teacher_staff_hour_header'), ...teachers.map(t => t.name)];
      md += '| ' + headers.join(' | ') + ' |\n';
      md += '| ' + headers.map(() => '---').join(' | ') + ' |\n';

      hour_names.forEach((hName, h) => {
        const row = [hName];
        teachers.forEach(t => {
          const cell = grid[String(d)]?.[String(h)]?.[String(t.id)] || null;
          if (!cell) {
            row.push('');
          } else if (cell.is_unavailable) {
            row.push('✕');
          } else {
            row.push(cell.subject_code || '');
          }
        });
        md += '| ' + row.join(' | ') + ' |\n';
      });
      md += '\n';
    });
    return md;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, selectedDays]);

  const handleDownloadMarkdown = useCallback(() => {
    const content = buildMarkdownForDownload();
    if (!content.trim()) return;
    try {
      const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      const date = new Date().toISOString().split('T')[0];
      link.href = url;
      link.download = `teacher-staff-${date}.md`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch {
      // ignore
    }
  }, [buildMarkdownForDownload]);

  const handlePrint = useCallback(() => {
    const style = document.createElement('style');
    style.id = 'teacher-grid-print-style';
    style.textContent = '@page { size: landscape; margin: 10mm 8mm; }';
    document.head.appendChild(style);
    window.print();
    requestAnimationFrame(() => {
      document.head.removeChild(style);
    });
  }, []);

  useImperativeHandle(ref, () => ({
    downloadMarkdown: handleDownloadMarkdown,
    print: handlePrint,
    hasData: () => !!data && Array.isArray(data.teachers) && data.teachers.length > 0,
  }), [handleDownloadMarkdown, handlePrint, data]);

  if (loading) {
    return <div className="state-loading" role="status"><span>{t('timetable.loading')}</span></div>;
  }

  if (error) {
    return <div className="state-error" role="alert">{error}</div>;
  }

  if (!data || !Array.isArray(data.teachers) || data.teachers.length === 0) {
    return <div className="state-empty">{t('timetable.teacher_staff_no_data')}</div>;
  }

  const { teachers, day_indices, day_names, day_colors, hour_names, grid } = data;
  const allSelected = day_indices.every(d => selectedDays.has(String(d)));
  const someSelected = !allSelected && selectedDays.size > 0;

  return (
    <div className="teacher-grid">
      <div className="teacher-grid-filter">
        <span className="teacher-grid-filter__label">{t('timetable.teacher_staff_filter_label')}</span>
        <label className="teacher-grid-filter__all">
          <input
            type="checkbox"
            checked={allSelected}
            ref={input => { if (input) input.indeterminate = someSelected; }}
            onChange={e => toggleAllDays(e.target.checked)}
          />
          <span>{t('common.all')}</span>
        </label>
        {day_indices.map(d => (
          <label key={d} className="teacher-grid-filter__day">
            <input
              type="checkbox"
              checked={selectedDays.has(String(d))}
              onChange={() => toggleDay(String(d))}
            />
            <span>{day_names[day_indices.indexOf(d)] || t(`day.${d}`)}</span>
          </label>
        ))}
      </div>

      <div className="teacher-grid-tables">
        {day_indices.map(d => {
          if (!selectedDays.has(String(d))) return null;
          const dayName = day_names[day_indices.indexOf(d)] || t(`day.${d}`);
          const dayColor = getDayColor(d);

          return (
            <section key={d} className="teacher-grid-day">
              <h3 className="teacher-grid-day__title" style={{ borderLeftColor: dayColor !== 'transparent' ? dayColor : undefined }}>
                {dayName}
              </h3>
              <div className="teacher-grid-table-wrap">
                <table className="teacher-grid-table">
                  <thead>
                    <tr>
                      <th>{t('timetable.teacher_staff_hour_header')}</th>
                      {teachers.map(t => (
                        <th
                          key={t.id}
                          className="teacher-grid-table__th-teacher"
                          title={t.name}
                          onClick={() => onViewTeacherTimetable && onViewTeacherTimetable(t.name)}
                          onKeyDown={e => { if (e.key === 'Enter' && onViewTeacherTimetable) { onViewTeacherTimetable(t.name); } }}
                          tabIndex={0}
                          role="button"
                        >
                          {t.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {hour_names.map((hName, h) => (
                      <tr key={h}>
                        <td className="teacher-grid-table__hour">{hName}</td>
                        {teachers.map(t => {
                          const cell = grid[String(d)]?.[String(h)]?.[String(t.id)] || null;
                          const isEmpty = !cell;
                          const isSupport = cell && cell.is_support;
                          const isUnavailable = cell && cell.is_unavailable;
                          const bgColor = (isEmpty || isSupport) ? 'transparent' : dayColor;
                          return (
                            <td
                              key={t.id}
                              className={`teacher-grid-table__cell${isEmpty ? ' teacher-grid-table__cell--empty' : ''}${isSupport ? ' teacher-grid-table__cell--support' : ''}${isUnavailable ? ' teacher-grid-table__cell--unavailable' : ''}`}
                              style={{ backgroundColor: bgColor }}
                              onClick={() => onViewTeacherTimetable && onViewTeacherTimetable(t.name)}
                              onKeyDown={e => { if (e.key === 'Enter' && onViewTeacherTimetable) { onViewTeacherTimetable(t.name); } }}
                              tabIndex={0}
                              role="button"
                            >
                              {isUnavailable ? <span className="teacher-grid-table__unavailable-icon">✕</span> : (cell ? cell.subject_code : '')}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
});

export default TeacherGridTimetable;