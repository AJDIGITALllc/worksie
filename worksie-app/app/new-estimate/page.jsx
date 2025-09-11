"use client";
import React, { useState } from 'react';

export default function NewEstimate() {
  const [estimate, setEstimate] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCreateEstimate = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(process.env.NEXT_PUBLIC_API_URL + '/v1/estimates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          imagePath: '/path/to/image.jpg',
          domain: 'auto',
          orgId: 'org-123',
          projectId: 'proj-456',
        }),
      });
      if (!response.ok) {
        throw new Error('Failed to create estimate');
      }
      const data = await response.json();
      setEstimate(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">New Estimate</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <button
          onClick={handleCreateEstimate}
          disabled={isLoading}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400"
        >
          {isLoading ? 'Creating...' : 'Create New Estimate'}
        </button>
        {error && <p className="text-red-500 mt-4">Error: {error}</p>}
        {estimate && (
          <div className="mt-4 p-4 bg-gray-100 rounded">
            <h2 className="text-xl font-bold">Estimate Created</h2>
            <p>ID: {estimate.estimateId}</p>
            <p>Fast Estimate Total: ${estimate.fastEstimate.total}</p>
            <p>Confidence: {estimate.fastEstimate.confidence * 100}%</p>
          </div>
        )}
      </div>
    </div>
  );
}
