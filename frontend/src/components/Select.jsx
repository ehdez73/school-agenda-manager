import { useState, useRef, useEffect } from 'react';
import './Select.css';

export default function Select({
  value,
  onChange,
  options,
  placeholder = '',
  className = '',
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const wrapperRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    setHighlightedIndex(-1);
  }, [isOpen]);

  const selectedOption = options.find(o => String(o.value) === String(value));
  const displayText = selectedOption ? selectedOption.label : placeholder;

  function handleSelect(option) {
    onChange({ target: { value: option.value } });
    setIsOpen(false);
  }

  function handleKeyDown(e) {
    if (!isOpen) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') {
        setIsOpen(true);
        return;
      }
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(i => Math.min(i + 1, options.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(i => Math.max(i - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < options.length) {
          handleSelect(options[highlightedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        break;
    }
  }

  return (
    <div
      className={`custom-select ${className} ${isOpen ? 'custom-select--open' : ''}`}
      ref={wrapperRef}
    >
      <button
        type="button"
        className={`custom-select__trigger ${!selectedOption ? 'custom-select__trigger--placeholder' : ''}`}
        onClick={() => setIsOpen(o => !o)}
        onKeyDown={handleKeyDown}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span>{displayText}</span>
        <span className="custom-select__arrow" aria-hidden="true" />
      </button>
      {isOpen && (
        <div className="custom-select__dropdown" role="listbox">
          {options.map((option, index) => (
            <div
              key={option.value}
              role="option"
              aria-selected={String(option.value) === String(value)}
              className={`custom-select__option ${
                index === highlightedIndex ? 'custom-select__option--highlighted' : ''
              } ${String(option.value) === String(value) ? 'custom-select__option--selected' : ''}`}
              onClick={() => handleSelect(option)}
              onMouseEnter={() => setHighlightedIndex(index)}
            >
              {option.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
