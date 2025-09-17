import { useState, useEffect } from 'react';
import { getRemoteConfig, onConfigUpdated, fetchAndActivate } from "firebase/remote-config";
import { getRemoteConfigValue } from '../logic/remoteConfig.js';
import { app } from '../logic/firebase.js';

const PromoBanner = () => {
  const [isEnabled, setIsEnabled] = useState(false);
  const [text, setText] = useState('');

  const updateBannerData = () => {
    const enabled = getRemoteConfigValue('promo_banner_enabled').asBoolean();
    const bannerText = getRemoteConfigValue('promo_banner_text').asString();
    setIsEnabled(enabled);
    setText(bannerText);
  };

  useEffect(() => {
    updateBannerData();

    const rc = getRemoteConfig(app);
    const unsubscribe = onConfigUpdated(rc, async () => {
      await fetchAndActivate(rc);
      updateBannerData();
    });

    return () => {
      unsubscribe();
    };
  }, []);

  if (!isEnabled) {
    return null;
  }

  return (
    <div className="bg-primary text-white text-center p-2">
      <p>{text}</p>
    </div>
  );
};

export default PromoBanner;
