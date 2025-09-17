import React from 'react';
import { render, screen, act } from '@testing-library/react';
import PromoBanner from './PromoBanner';
import { getRemoteConfigValue } from '../logic/remoteConfig.js';
import { onConfigUpdated, fetchAndActivate } from 'firebase/remote-config';

jest.mock('../logic/remoteConfig.js', () => ({
  getRemoteConfigValue: jest.fn(),
}));

jest.mock('firebase/remote-config', () => ({
  getRemoteConfig: jest.fn(),
  onConfigUpdated: jest.fn(),
  fetchAndActivate: jest.fn(),
}));

jest.mock('../logic/firebase.js', () => ({
  app: {},
}));

describe('PromoBanner', () => {
  beforeEach(() => {
    getRemoteConfigValue.mockImplementation((key) => {
      if (key === 'promo_banner_enabled') {
        return { asBoolean: () => true };
      }
      if (key === 'promo_banner_text') {
        return { asString: () => 'Initial Banner Text' };
      }
      return { asString: () => '', asBoolean: () => false };
    });
    fetchAndActivate.mockResolvedValue(true);
  });

  test('updates banner text when remote config changes', async () => {
    let onUpdateCallback;
    onConfigUpdated.mockImplementation((rc, callback) => {
      onUpdateCallback = callback;
      return () => {}; // Return an unsubscribe function
    });

    render(<PromoBanner />);

    expect(screen.getByText('Initial Banner Text')).toBeInTheDocument();

    getRemoteConfigValue.mockImplementation((key) => {
      if (key === 'promo_banner_enabled') {
        return { asBoolean: () => true };
      }
      if (key === 'promo_banner_text') {
        return { asString: () => 'Updated Banner Text' };
      }
      return { asString: () => '', asBoolean: () => false };
    });

    await act(async () => {
      onUpdateCallback();
    });

    expect(screen.getByText('Updated Banner Text')).toBeInTheDocument();
  });
});
