import { useEffect } from 'react';
import AppRoutes from './routes.jsx';
import { requestForToken } from './logic/firebase.js';
import { initializeRemoteConfig, getRemoteConfigValue } from './logic/remoteConfig.js';
import PromoBanner from './components/PromoBanner.jsx';

function App() {
  useEffect(() => {
    requestForToken();
    const init = async () => {
      await initializeRemoteConfig();
      const primaryColor = getRemoteConfigValue('app_primary_color').asString();
      document.documentElement.style.setProperty('--primary-color', primaryColor);
    };
    init();
  }, []);

  return (
    <div className="App">
      <PromoBanner />
      <AppRoutes />
    </div>
  );
}

export default App;
