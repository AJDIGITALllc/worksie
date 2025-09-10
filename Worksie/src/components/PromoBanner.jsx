import { useState, useEffect } from 'react';
import { getRemoteConfigValue } from '../logic/remoteConfig.js';

const PromoBanner = () => {
  const [isEnabled, setIsEnabled] = useState(false);
  const [text, setText] = useState('');

  useEffect(() => {
    const enabled = getRemoteConfigValue('promo_banner_enabled').asBoolean();
    const bannerText = getRemoteConfigValue('promo_banner_text').asString();
    setIsEnabled(enabled);
    setText(bannerText);
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
