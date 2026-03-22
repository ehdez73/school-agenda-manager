import { describe, it, expect } from 'vitest';
import { renderSection } from '../../test/layoutFixtures';

describe('SectionLayout – action hierarchy contract (C-3)', () => {
  it('renders actions slot when actions prop is provided', () => {
    renderSection({
      title: 'My Section',
      actions: <button className="btn btn--primary">Add Item</button>,
    });
    expect(document.querySelector('.section-layout__actions')).toBeInTheDocument();
  });

  it('actions slot is inside the header heading-row', () => {
    renderSection({
      title: 'My Section',
      actions: <button className="btn btn--primary">Add Item</button>,
    });
    const headingRow = document.querySelector('.section-layout__heading-row');
    expect(headingRow.querySelector('.section-layout__actions')).toBeInTheDocument();
  });

  it('does not render actions container when actions prop is not provided', () => {
    renderSection({ title: 'My Section' });
    expect(document.querySelector('.section-layout__actions')).not.toBeInTheDocument();
  });

  it('primary action uses btn--primary class', () => {
    renderSection({
      title: 'My Section',
      actions: <button className="btn btn--primary">Primary Action</button>,
    });
    const primaryBtn = document.querySelector('.btn.btn--primary');
    expect(primaryBtn).toBeInTheDocument();
    expect(primaryBtn).toHaveTextContent('Primary Action');
  });

  it('content zone is separate from the header zone', () => {
    renderSection({
      title: 'My Section',
      actions: <button className="btn btn--primary">Add</button>,
      children: <p>Main content here</p>,
    });
    const content = document.querySelector('.section-layout__content');
    const header = document.querySelector('.section-layout__header');
    expect(content).toBeInTheDocument();
    expect(header).toBeInTheDocument();
    // Content should NOT be inside header
    expect(header.contains(content)).toBe(false);
  });
});
