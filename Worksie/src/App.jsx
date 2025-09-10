import { useEffect } from 'react';
import AppRoutes from './routes.jsx';
import { requestForToken } from './logic/firebase.js';

function App() {
  useEffect(() => {
    requestForToken();
  }, []);

  return (
    <div className="App">
      <AppRoutes />
    </div>
  );
}

export default App;
