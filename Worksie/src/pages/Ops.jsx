import React, { useEffect, useState } from "react";

// Mock UI components. In a real app, these would come from a shared library.
const Card = ({ children, className }) => <div className={`bg-white shadow-lg rounded-lg ${className}`}>{children}</div>;
const CardContent = ({ children, className }) => <div className={`p-6 ${className}`}>{children}</div>;
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

// A tiny SVG sparkline component
function Sparkline({ data }) {
  if (!data?.length) return <div className="w-[240px] h-[60px] bg-gray-100 rounded-md flex items-center justify-center text-xs text-gray-400">No P95 data</div>;

  const w = 240, h = 60, pad = 4;
  const xs = data.map(d => d[0]);
  const ys = data.map(d => d[1]);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const minX = Math.min(...xs), maxX = Math.max(...xs);

  const pts = data.map(([t, y], i) => {
    const x = pad + ((t - minX) / (maxX - minX || 1)) * (w - 2 * pad);
    const v = (y - minY) / (maxY - minY || 1);
    const yy = h - pad - v * (h - 2 * pad);
    return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${yy.toFixed(1)}`;
  }).join(" ");

  return (
    <svg width={w} height={h} className="text-indigo-500">
      <path d={pts} fill="none" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}

export default function Ops() {
  const [ops, setOps] = useState(null);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      // In a real app, the API URL and credentials would be handled more robustly.
      const r = await fetch((process.env.NEXT_PUBLIC_API || 'http://localhost:8000') + "/v1/ops/summary");
      if (!r.ok) throw new Error(`HTTP error! status: ${r.status}`);
      const j = await r.json();
      setOps(j);
    } catch (e) {
      setError(e.message);
      console.error("Failed to fetch ops summary:", e);
    }
  };

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, 30000); // Poll every 30 seconds
    return () => clearInterval(id);
  }, []);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API || 'http://localhost:8000';

  // Mock toast object for user feedback
  const toast = {
    success: (message) => alert(`SUCCESS: ${message}`),
    error: (message) => alert(`ERROR: ${message}`),
  };

  const promote = async (ratio) => {
    if (!ops?.model?.version) {
      toast.error("No active model selected.");
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/v1/admin/models/promote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }, // Auth handled by browser cookies for gcloud run
        body: JSON.stringify({
          modelId: ops.model.version,
          rolloutRatio: ratio,
          notes: `UI promote ${ratio * 100}%`,
          trigger: "pubsub",
        }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Promotion request failed");
      }
      toast.success(`Promotion to ${ratio * 100}% initiated for ${ops.model.version}.`);
      fetchData(); // Refresh data after action
    } catch (e) {
      toast.error(e.message);
    }
  };

  const rollback = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/admin/models/rollback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}), // Rollback to previous model
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Rollback request failed");
      }
      toast.success("Rollback initiated.");
      fetchData(); // Refresh data after action
    } catch (e) {
      toast.error(e.message);
    }
  };

  if (error) {
    return <div className="p-6 text-red-500">Error fetching ops data: {error}</div>;
  }
  if (!ops) {
    return <div className="p-6">Loading ops dashboard...</div>;
  }

  return (
    <main className="grid gap-6 p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold">ML Ops Service Catalog</h1>
      <Card className="rounded-2xl">
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-500">Active Model</div>
              <div className="text-xl font-semibold">{ops.model?.version || "N/A"}</div>
              <div className="text-sm text-gray-600">
                Canary: {(ops.model?.rolloutRatio ?? 0) * 100}% · Prev: {ops.model?.prevModelId || "—"}
              </div>
              {ops.model?.notes && <div className="text-xs text-gray-500 mt-1">{ops.model.notes}</div>}
            </div>
            <Sparkline data={ops.p95 || []} />
          </div>
          <div className="mt-4 flex gap-3">
            <Button onClick={() => promote(0.10)}>Canary 10%</Button>
            <Button onClick={() => promote(0.50)} variant="secondary">50%</Button>
            <Button onClick={() => promote(1.0)}>Rollout 100%</Button>
            <Button onClick={rollback} variant="destructive">Rollback</Button>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}
