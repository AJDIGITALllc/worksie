import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import PromoBanner from './PromoBanner';
import { initializeRemoteConfig, getRemoteConfigValue } from '../logic/remoteConfig';

// Mock the remoteConfig module
vi.mock('../logic/remoteConfig.js', () => ({
  initializeRemoteConfig: vi.fn(),
  getRemoteConfigValue: vi.fn(),
}));

describe('PromoBanner', () => {
  it('should not render when disabled', async () => {
    getRemoteConfigValue.mockImplementation((key) => {
      if (key === 'promo_banner_enabled') {
        return { asBoolean: () => false };
      }
      return { asString: () => '' };
    });

    const { container } = render(<PromoBanner />);

    await waitFor(() => {
      expect(initializeRemoteConfig).toHaveBeenCalled();
    });

    expect(container.firstChild).toBeNull();
  });

  it('should render with the correct text when enabled', async () => {
    const bannerText = 'Special promotion!';
    getRemoteConfigValue.mockImplementation((key) => {
      if (key === 'promo_banner_enabled') {
        return { asBoolean: () => true };
      }
      if (key === 'promo_banner_text') {
        return { asString: () => bannerText };
      }
      return { asBoolean: () => false, asString: () => '' };
    });

    render(<PromoBanner />);

    await waitFor(() => {
      expect(initializeRemoteConfig).toHaveBeenCalled();
    });

    expect(screen.getByText(bannerText)).toBeInTheDocument();
  });
});
