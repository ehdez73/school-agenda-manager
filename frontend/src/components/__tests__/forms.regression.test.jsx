import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';

import ConfigForm from '../ConfigForm';

const { apiMock, configResponse } = vi.hoisted(() => {
  const response = {
    classes_per_day: 5,
    days_per_week: 5,
    hour_names: ['9:00', '10:00', '11:00', '12:00', '13:00'],
    day_indices: [0, 1, 2, 3, 4],
  };

  return {
    apiMock: {
      get: vi.fn().mockResolvedValue(response),
      post: vi.fn().mockResolvedValue(response),
      del: vi.fn().mockResolvedValue({}),
    },
    configResponse: response,
  };
});

vi.mock('../../lib/api', () => ({
  default: apiMock,
}));

vi.mock('../../i18n', () => ({
  t: key => key,
}));

describe('Forms regression guard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiMock.get.mockResolvedValue(configResponse);
    apiMock.post.mockResolvedValue(configResponse);
  });

  it('renders config tabs and keeps save action available', async () => {
    render(<ConfigForm />);

    expect(await screen.findByRole('button', { name: 'config.tab_days' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'config.tab_hours' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'config.tab_backup' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'common.save' })).toBeInTheDocument();
  });

  it('keeps day validation behavior for invalid ranges', async () => {
    render(<ConfigForm />);

    const daysInput = await screen.findByRole('spinbutton', { name: /config.days_per_week/i });
    fireEvent.change(daysInput, { target: { value: 0 } });

    const form = daysInput.closest('form');
    fireEvent.submit(form);

    expect(await screen.findByText('config.invalid_days_per_week')).toBeInTheDocument();
    expect(apiMock.post).not.toHaveBeenCalled();
  });
});
