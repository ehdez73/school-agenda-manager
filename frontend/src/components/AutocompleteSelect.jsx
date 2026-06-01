import { useState, useRef, useEffect, useMemo } from 'react';
import './AutocompleteSelect.css';

export default function AutocompleteSelect({
    items,
    selectedIds,
    onAdd,
    onRemove,
    getDisplayLabel = (item) => item.full_name || item.name,
    placeholder = 'Search...',
    noResultsText = 'No results',
    singleSelect = false,
}) {
    const [searchTerm, setSearchTerm] = useState('');
    const [isOpen, setIsOpen] = useState(false);
    const [highlightedIndex, setHighlightedIndex] = useState(-1);
    const wrapperRef = useRef(null);
    const inputRef = useRef(null);

    const filteredItems = useMemo(() => {
        const selected = new Set(selectedIds.map(String));
        const query = searchTerm.toLowerCase().trim();
        return items
            .filter(item => {
                if (!singleSelect && selected.has(String(item.id))) return false;
                if (!query) return true;
                const label = getDisplayLabel(item).toLowerCase();
                return label.includes(query);
            })
            .sort((a, b) => (getDisplayLabel(a) || '').localeCompare(getDisplayLabel(b) || ''));
    }, [items, selectedIds, searchTerm, getDisplayLabel, singleSelect]);

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
    }, [filteredItems.length]);

    function handleInputChange(e) {
        setSearchTerm(e.target.value);
        setIsOpen(true);
    }

    function handleSelect(item) {
        if (singleSelect) {
            if (selectedIds.length > 0) {
                onRemove(selectedIds[0]);
            }
            onAdd(String(item.id));
        } else {
            onAdd(String(item.id));
        }
        setSearchTerm('');
        setIsOpen(false);
        inputRef.current?.focus();
    }

    function handleRemove(id) {
        onRemove(String(id));
    }

    function handleKeyDown(e) {
        if (!isOpen) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'Enter') {
                setIsOpen(true);
                return;
            }
        }

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                setHighlightedIndex(i => Math.min(i + 1, filteredItems.length - 1));
                break;
            case 'ArrowUp':
                e.preventDefault();
                setHighlightedIndex(i => Math.max(i - 1, 0));
                break;
            case 'Enter':
                e.preventDefault();
                if (highlightedIndex >= 0 && highlightedIndex < filteredItems.length) {
                    handleSelect(filteredItems[highlightedIndex]);
                }
                break;
            case 'Escape':
                setIsOpen(false);
                break;
        }
    }

    return (
        <div className="autocomplete" ref={wrapperRef}>
            <input
                ref={inputRef}
                type="text"
                className="autocomplete__input"
                value={searchTerm}
                onChange={handleInputChange}
                onFocus={() => setIsOpen(true)}
                onKeyDown={handleKeyDown}
                placeholder={placeholder}
                autoComplete="off"
            />
            {isOpen && (
                <div className="autocomplete__dropdown">
                    {filteredItems.length > 0 ? (
                        filteredItems.map((item, index) => (
                            <div
                                key={item.id}
                                className={`autocomplete__option ${index === highlightedIndex ? 'autocomplete__option--highlighted' : ''}`}
                                onClick={() => handleSelect(item)}
                                onMouseEnter={() => setHighlightedIndex(index)}
                            >
                                {getDisplayLabel(item)}
                            </div>
                        ))
                    ) : (
                        <div className="autocomplete__no-results">{noResultsText}</div>
                    )}
                </div>
            )}
            <div className="subject-selection__list">
                {selectedIds.length > 0 ? (
                    selectedIds.map(id => {
                        const item = items.find(s => String(s.id) === String(id));
                        if (!item) return null;
                        return (
                            <span key={id} className="chip">
                                {getDisplayLabel(item)}
                                <button type="button" className="chip__remove" onClick={() => handleRemove(id)}>×</button>
                            </span>
                        );
                    })
                ) : (
                    <span className="subject-selection__empty">—</span>
                )}
            </div>
        </div>
    );
}
