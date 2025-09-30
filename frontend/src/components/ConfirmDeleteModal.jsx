import React from 'react';
import './ConfirmDeleteModal.css';
import { t } from '../i18n';

export default function ConfirmDeleteModal({ open, entity, onConfirm, onCancel, text, id }) {
  React.useEffect(() => {
    if (!open) return;
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        onCancel();
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [open, onCancel]);
  if (!open) return null;
  const defaultMessage = `${t('common.confirm')} ${entity} ${id ? '"' + id + '"' : ''}`;
  return (
    <div className="confirm-modal-overlay">
      <div className="confirm-modal">
        <h3>{t('common.confirm')}</h3>
        <p>{text || defaultMessage}</p>
        <div className="confirm-modal-actions">
          <button className="confirm-modal-cancel" onClick={onCancel}>{t('common.cancel')}</button>
          <button className="confirm-modal-delete" onClick={onConfirm}>{t('common.delete')}</button>
        </div>
      </div>
    </div>
  );
}
