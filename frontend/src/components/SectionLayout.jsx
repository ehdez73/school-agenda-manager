import './SectionLayout.css';

/**
 * SectionLayout — shared structural wrapper for all main sections.
 *
 * Props:
 *   title       {string}    Required. Section heading (rendered as <h2>).
 *   description {string}    Optional. Short description below the heading.
 *   actions     {ReactNode} Optional. Slot for header-level action buttons (e.g. "Add").
 *   children    {ReactNode} Main content slot (rendered when state === 'ready').
 *   state       {'ready'|'loading'|'error'|'empty'} Default: 'ready'.
 *   errorMsg    {string}    Message shown in error state.
 *   emptyMsg    {string}    Message shown in empty state.
 *   className   {string}    Extra class appended to root element.
 */
export default function SectionLayout({
  title,
  description,
  actions,
  children,
  state = 'ready',
  errorMsg,
  emptyMsg,
  className,
  'data-testid': testId,
}) {
  return (
    <section
      className={`section-layout${className ? ` ${className}` : ''}`}
      data-testid={testId || 'section-layout'}
    >
      <header className="section-layout__header">
        <div className="section-layout__heading-row">
          <h2 className="section-layout__title">{title}</h2>
          {actions && (
            <div className="section-layout__actions">{actions}</div>
          )}
        </div>
        {description && (
          <p className="section-layout__description">{description}</p>
        )}
      </header>
      <div className="section-layout__content">
        {state === 'loading' && (
          <div className="state-loading" role="status" aria-live="polite">
            <span className="visually-hidden">Loading…</span>
          </div>
        )}
        {state === 'error' && (
          <div className="state-error" role="alert">
            {errorMsg}
          </div>
        )}
        {state === 'empty' && (
          <div className="state-empty">{emptyMsg}</div>
        )}
        {state === 'ready' && children}
      </div>
    </section>
  );
}
