import React from 'react';

export default function useEscapeToCancel(onCancel) {
  React.useEffect(() => {
    if (typeof onCancel !== 'function') return undefined;

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        onCancel();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onCancel]);
}