import React from 'react';
import './FormModal.css';

export default function FormModal({ open, children, onClose }) {
  React.useEffect(() => {
    if (!open) return;
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="form-modal-overlay">
      <div className="form-modal">
        {children}
        <button className="form-modal-close" onClick={onClose}>×</button>
      </div>
    </div>
  );
}
