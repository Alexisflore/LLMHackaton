// frontend/app/page.tsx
'use client';
import { useState } from 'react';
import axios from 'axios';
import { File } from '@/lib/dom';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [similarPairs, setSimilarPairs] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/upload', formData);
      setSimilarPairs(response.data.similar_pairs);
    } catch (error) {
      console.error('Error uploading file:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Analyseur d'Amendements</h1>
        
        <div className="mb-8">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            className="mb-4 block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />
          <button
            onClick={handleSubmit}
            disabled={!file || loading}
            className="bg-blue-500 text-white px-4 py-2 rounded-md
              hover:bg-blue-600 disabled:bg-gray-400"
          >
            {loading ? 'Analyse en cours...' : 'Analyser les amendements'}
          </button>
        </div>

        {similarPairs.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold mb-4">Amendements similaires</h2>
            {similarPairs.map((pair: any, index: number) => (
              <div
                key={index}
                className="p-4 border rounded-md bg-white shadow-sm"
              >
                <p className="text-lg">
                  Amendement {pair.amendement1} et {pair.amendement2}
                </p>
                <p className="text-gray-600">
                  Similarité: {(pair.similarite * 100).toFixed(1)}%
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}