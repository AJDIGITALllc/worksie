import { getRemoteConfig, fetchAndActivate, getValue } from "firebase/remote-config";
import { app } from './firebase.js';

const rc = getRemoteConfig(app);

// Set a minimum fetch interval to avoid frequent requests
rc.settings.minimumFetchIntervalMillis = 3600000; // 1 hour

// Set default values (optional, but good practice)
rc.defaultConfig = {
  "promo_banner_enabled": false,
  "promo_banner_text": "Welcome!",
  "app_primary_color": "#007BFF",
};

export const initializeRemoteConfig = async () => {
  await fetchAndActivate(rc);
};

export const getRemoteConfigValue = (key) => {
  return getValue(rc, key);
};
