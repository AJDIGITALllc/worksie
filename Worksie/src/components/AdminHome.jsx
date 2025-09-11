import React from 'react';

// A mock Button component to make the UI work.
// In a real app, this would come from a UI library like ShadCN or MUI.
const Button = ({ onClick, children, variant }) => {
  const baseStyle = "px-4 py-2 rounded-md font-semibold text-white transition-colors";
  const variants = {
    default: "bg-blue-600 hover:bg-blue-700",
    secondary: "bg-gray-500 hover:bg-gray-600",
    destructive: "bg-red-600 hover:bg-red-700",
  };
  const style = `${baseStyle} ${variants[variant] || variants.default}`;
  return <button onClick={onClick} className={style}>{children}</button>;
};

// Mock toast object
const toast = {
  success: (message) => console.log(`Toast Success: ${message}`),
  error: (message) => console.error(`Toast Error: ${message}`),
};

const AdminHome = () => {
  // Mock data for ML models
  const models = [
    { id: "2025.09.10-auto-v7", sha: "a1b2c3d4", metrics: { val_mae: 42.1, p95_ms: 1750 }, isActive: true, rolloutRatio: 0.10, notes: "auto damage v7 canary" },
    { id: "2025.08.31-v6", sha: "e5f6g7h8", metrics: { val_mae: 45.5, p95_ms: 1600 }, isActive: false, rolloutRatio: 1.0, notes: "previous stable" },
    { id: "2025.07.15-v5", sha: "i9j0k1l2", metrics: { val_mae: 48.2, p95_ms: 1550 }, isActive: false, rolloutRatio: 1.0, notes: "archived" },
  ];

  // Placeholder for auth token. In a real app, this would come from an auth context.
  const token = "your-bearer-token";

  async function promote(modelId, ratio) {
    try {
      const response = await fetch((process.env.NEXT_PUBLIC_API || 'http://localhost:8000') + "/v1/admin/models/promote", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ modelId, rolloutRatio: ratio, notes: `canary ${ratio * 100}%`, trigger: "pubsub" })
      });
      if (!response.ok) throw new Error('Promotion request failed');
      toast.success(`Promoted ${modelId} to ${ratio * 100}%`);
    } catch (error) {
      toast.error(error.message);
    }
  }

  async function rollout(modelId) {
    await promote(modelId, 1.0);
  }

  async function rollback(toModelId) {
    try {
      const response = await fetch((process.env.NEXT_PUBLIC_API || 'http://localhost:8000') + "/v1/admin/models/rollback", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ toModelId })
      });
      if (!response.ok) throw new Error('Rollback request failed');
      toast.success(`Rollback queued`);
    } catch (error) {
      toast.error(error.message);
    }
  }

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Admin Console: Model Registry</h1>
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full leading-normal">
          <thead>
            <tr className="border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
              <th className="px-5 py-3">Model ID</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3">Rollout</th>
              <th className="px-5 py-3">Notes</th>
              <th className="px-5 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {models.map((m) => (
              <tr key={m.id} className="border-b border-gray-200">
                <td className="px-5 py-5 text-sm">
                  <p className="text-gray-900 whitespace-no-wrap font-semibold">{m.id}</p>
                  <p className="text-gray-600 whitespace-no-wrap text-xs">{m.sha}</p>
                </td>
                <td className="px-5 py-5 text-sm">
                  {m.isActive ? (
                    <span className="relative inline-block px-3 py-1 font-semibold text-green-900 leading-tight">
                      <span aria-hidden className="absolute inset-0 bg-green-200 opacity-50 rounded-full"></span>
                      <span className="relative">Active</span>
                    </span>
                  ) : (
                    <span className="relative inline-block px-3 py-1 font-semibold text-gray-700 leading-tight">
                      <span aria-hidden className="absolute inset-0 bg-gray-200 opacity-50 rounded-full"></span>
                      <span className="relative">Inactive</span>
                    </span>
                  )}
                </td>
                <td className="px-5 py-5 text-sm">
                  <p className="text-gray-900 whitespace-no-wrap">{m.rolloutRatio * 100}%</p>
                </td>
                <td className="px-5 py-5 text-sm">
                  <p className="text-gray-900 whitespace-no-wrap">{m.notes}</p>
                </td>
                <td className="px-5 py-5 text-sm">
                  <div className="flex gap-2">
                    <Button onClick={() => promote(m.id, 0.10)}>Canary 10%</Button>
                    <Button onClick={() => promote(m.id, 0.50)} variant="secondary">50%</Button>
                    <Button onClick={() => rollout(m.id)}>Rollout 100%</Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="p-4 bg-gray-50 border-t-2 border-gray-200 flex justify-end">
             <Button onClick={() => rollback()} variant="destructive">Rollback to Previous</Button>
        </div>
      </div>
    </div>
  );
};

export default AdminHome;
