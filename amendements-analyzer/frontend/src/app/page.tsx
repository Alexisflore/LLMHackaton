'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import Chatbot from './components/Chatbot';
import React from 'react';

type Amendment = {
  uid: string;
  titre: string;
  exposeSommaire: string;
  auteur: string;
  sort: string;
};

type Cluster = {
  cluster_id: string;
  amendments: Amendment[];
  summary: string;
  theme: string;
  key_points: string[];
};

export default function Home() {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<Cluster | null>(null);
  const [loading, setLoading] = useState(true);
  const [sortValues, setSortValues] = useState([]);
  const [instanceValues, setInstanceValues] = useState([]);
  const [selectedSort, setSelectedSort] = useState<string | null>(null);
  const [selectedInstance, setSelectedInstance] = useState<string | null>(null);

  useEffect(() => {
    fetchClusters();
    fetchFilterValues();
  }, []);

  const fetchClusters = async () => {
    try {
      const url = new URL('http://localhost:8000/api/clusters');
      if (selectedSort) {
        url.searchParams.append('sort_filter', selectedSort);
      }
      if (selectedInstance) {
        url.searchParams.append('instance_filter', selectedInstance);
      }

      const response = await axios.get(url.toString());
      setClusters(response.data);
    } catch (error) {
      console.error('Error fetching clusters:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchClustersUids = (sort: string | null, instance: string | null) => {
    const params = new URLSearchParams();
    if (sort) params.append('sort_filter', sort);
    if (instance) params.append('instance_filter', instance);
    fetch(`/api/get_clusters_uids?${params.toString()}`)
      .then(response => response.json())
      .then(data => {
        // Traitez les données des clusters ici
      });
  };

  const handleSortChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedSort(event.target.value || null);
    fetchClusters();
  };

  const handleInstanceChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedInstance(event.target.value || null);
    fetchClusters();
  };

  const fetchFilterValues = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/get_filter_values');
      const data = await response.json();
      setSortValues(data.sort_values);
      setInstanceValues(data.instance_values);
    } catch (error) {
      console.error('Erreur lors de la récupération des valeurs de filtre :', error);
    }
  };

  return (
    <>
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8 text-blue-600">Analyse des Amendements</h1>
        
        <div className="mb-4 text-black">
          <label htmlFor="sort-filter" className="mr-2">
            Filtrer par Sort de l'amendement :
          </label>
          <select
            id="sort-filter"
            value={selectedSort || ''}
            onChange={handleSortChange}
            className="border rounded-md px-2 py-1 text-black"
          >
            <option value="">Tous</option>
            {sortValues
              .filter((value) => value !== 'nan')
              .map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
          </select>

          <label htmlFor="instance-filter" className="ml-4 mr-2">
            Filtrer par Instance :
          </label>
          <select
            id="instance-filter"
            value={selectedInstance || ''}
            onChange={handleInstanceChange}
            className="border rounded-md px-2 py-1 text-black"
          >
            <option value="">Tous</option>
            {instanceValues
              .filter((value) => value !== 'nan')
              .map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
          </select>
        </div>
        
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Liste des clusters */}
            <div className="md:col-span-1 space-y-4">
              <h2 className="text-xl font-semibold mb-4 text-black">Groupes d'amendements</h2>
              {clusters.map((cluster) => (
                <div
                  key={cluster.cluster_id}
                  className={`p-4 rounded-lg shadow cursor-pointer transition-colors
                    ${selectedCluster?.cluster_id === cluster.cluster_id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 hover:bg-gray-300 text-black'}`}
                  onClick={() => setSelectedCluster(cluster)}
                >
                  <h3 className="font-medium">{cluster.theme}</h3>
                  <p className="text-sm mt-2">
                    {cluster.amendments.length} amendements
                  </p>
                </div>
              ))}
            </div>

            {/* Détails du cluster sélectionné */}
            <div className="md:col-span-2">
              {selectedCluster ? (
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-2xl font-bold mb-4 text-black">
                    Cluster {selectedCluster.cluster_id}
                  </h2>
                  
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-2 text-black">Résumé</h3>
                    <p className="text-black">{selectedCluster.summary}</p>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-black">Amendements</h3>
                    {selectedCluster.amendments.map((amendment) => (
                      <div
                        key={amendment.uid}
                        className="border rounded-lg p-4"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-medium text-black">{amendment.titre}</h4>
                          <span className={`px-2 py-1 rounded text-sm
                            ${amendment.sort === 'Tombé' 
                              ? 'bg-red-100 text-red-800' 
                              : 'bg-green-100 text-green-800'}`}>
                            {amendment.sort}
                          </span>
                        </div>
                        <p className="text-sm text-black">
                          Auteur: {amendment.auteur}
                        </p>
                        <div className="mt-2 text-sm text-black">
                          {amendment.exposeSommaire}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-lg shadow p-6 text-center text-black">
                  Sélectionnez un groupe d'amendements pour voir les détails
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
    <Chatbot />
    </>
  );
}