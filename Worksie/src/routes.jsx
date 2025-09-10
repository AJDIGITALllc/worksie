import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Home from './pages/Home.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Reports from './pages/Reports.jsx';
import Tasks from './pages/Tasks.jsx';
import CRM from './pages/CRM.jsx';
import Settings from './pages/Settings.jsx';
import Support from './pages/Support.jsx';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Home />,
  },
  {
    path: '/dashboard',
    element: <Dashboard />,
  },
  {
    path: '/reports',
    element: <Reports />,
  },
  {
    path: '/tasks',
    element: <Tasks />,
  },
  {
    path: '/crm',
    element: <CRM />,
  },
  {
    path: '/settings',
    element: <Settings />,
  },
  {
    path: '/support',
    element: <Support />,
  },
]);

const AppRoutes = () => {
  return <RouterProvider router={router} />;
};

export default AppRoutes;
