import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { renderSectionWithState } from '../../test/layoutFixtures';
import SectionLayout from '../SectionLayout';

describe('SectionLayout – view-states contract (C-4)', () => {
  it('renders children in ready state', () => {
    render(
      <SectionLayout title="Test" state="ready">
        <p data-testid="ready-content">Ready content</p>
      </SectionLayout>
    );
    expect(screen.getByTestId('ready-content')).toBeInTheDocument();
  });

  it('does not render children in loading state', () => {
    render(
      <SectionLayout title="Test" state="loading">
        <p data-testid="hidden-content">Should not appear</p>
      </SectionLayout>
    );
    expect(screen.queryByTestId('hidden-content')).not.toBeInTheDocument();
  });

  it('renders loading indicator with role="status" in loading state', () => {
    renderSectionWithState('loading');
    expect(document.querySelector('[role="status"]')).toBeInTheDocument();
    expect(document.querySelector('.state-loading')).toBeInTheDocument();
  });

  it('renders error message with role="alert" in error state', () => {
    renderSectionWithState('error', { errorMsg: 'Something went wrong' });
    const alert = screen.getByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveTextContent('Something went wrong');
    expect(alert).toHaveClass('state-error');
  });

  it('does not render children in error state', () => {
    render(
      <SectionLayout title="Test" state="error" errorMsg="Error!">
        <p data-testid="hidden-content">Should not appear</p>
      </SectionLayout>
    );
    expect(screen.queryByTestId('hidden-content')).not.toBeInTheDocument();
  });

  it('renders empty message in empty state', () => {
    renderSectionWithState('empty', { emptyMsg: 'No items found' });
    const emptyEl = document.querySelector('.state-empty');
    expect(emptyEl).toBeInTheDocument();
    expect(emptyEl).toHaveTextContent('No items found');
  });

  it('does not render children in empty state', () => {
    render(
      <SectionLayout title="Test" state="empty" emptyMsg="Nothing here">
        <p data-testid="hidden-content">Should not appear</p>
      </SectionLayout>
    );
    expect(screen.queryByTestId('hidden-content')).not.toBeInTheDocument();
  });

  it('defaults to ready state when no state prop given', () => {
    render(
      <SectionLayout title="Test">
        <p data-testid="content">Default content</p>
      </SectionLayout>
    );
    expect(screen.getByTestId('content')).toBeInTheDocument();
  });
});
