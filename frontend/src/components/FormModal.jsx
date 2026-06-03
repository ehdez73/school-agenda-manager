
import { useEffect } from 'react';
import './FormModal.css';

export default function FormModal({ open, children, onClose }) {
  useEffect(() => {
    if (!open) return;
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="form-modal-overlay" onClick={onClose}>
      <div className="form-modal" onClick={(e) => e.stopPropagation()}>
        {children}
        <button className="form-modal-close" onClick={onClose}>×</button>
      </div>
    </div>
  );
}
