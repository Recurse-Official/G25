import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookCopy, Loader2, Route, Search, ChevronDown } from 'lucide-react';
import React from 'react';

const StatusDropdown = ({ selectedStatuses, onStatusChange }) => {
    const [open, setOpen] = useState(false);

    return (
        <div className="relative">
            <button
                onClick={() => setOpen(!open)}
                className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg text-zinc"
            >
                <div className="flex gap-1">
                    <span className="h-3 w-3 rounded-full bg-green-500"></span>
                    <span className="h-3 w-3 rounded-full bg-red-500"></span>
                </div>
                <span>Status {selectedStatuses.length}/2</span>
                <ChevronDown size={16} />
            </button>

            {open && (
                <div className="absolute top-full mt-2 right-0 bg-white text-zinc-900 rounded-lg shadow-lg p-2 min-w-[150px]">
                    {[
                        { label: 'Active', color: 'bg-green-500' },
                        { label: 'Inactive', color: 'bg-red-500' }
                    ].map(status => (
                        <label key={status.label} className="flex items-center gap-2 px-3 py-2 w-[145px] hover:bg-gray-10 rounded cursor-pointer">
                            <input
                                type="checkbox"
                                checked={selectedStatuses.includes(status.label)}
                                onChange={(e) => {
                                    const newStatuses = e.target.checked
                                        ? [...selectedStatuses, status.label]
                                        : selectedStatuses.filter(s => s !== status.label);
                                    onStatusChange(newStatuses);
                                    setOpen(false);
                                }}
                                className="hidden"
                            />
                            <div className={`h-3 w-3 rounded-full ${status.color}`} />
                            <span className="text-zinc-900 text-sm">{status.label}</span>
                            {selectedStatuses.includes(status.label) && <span className="ml-auto text-zinc-900">✓</span>}
                        </label>
                    ))}
                </div>
            )}
        </div>
    );
};

const RepositoryList = ({ repositories }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedStatuses, setSelectedStatuses] = useState(['Active', 'Inactive']);
    const navigate = useNavigate();

    const handleStatusChange = (newStatuses) => {
        setSelectedStatuses(newStatuses);
    };

    const filteredRepos = repositories.filter(repo =>
        repo.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        selectedStatuses.includes(repo.is_active ? 'Active' : 'Inactive')
    );

    return (
        <div className="max-w-7xl mx-auto px-4">
            <div className="flex items-center gap-4 mb-6">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                    <input
                        type="text"
                        placeholder="All Repositories..."
                        className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
                <StatusDropdown
                    selectedStatuses={selectedStatuses}
                    onStatusChange={handleStatusChange}
                />
            </div>

            <div className="space-y-4">
                {
                    filteredRepos.length === 0 && (
                        <div className="p-4 bg-white rounded-lg border border-gray-200 text-gray-600">
                            No repositories found with the selected filters.
                        </div>
                    )
                }
                {filteredRepos.map(repo => (
                    <div
                        key={repo.id}
                        onClick={() => navigate(`/repository/${repo.id}`, { state: { repo } })}
                        className="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                        <div>
                            <div className='flex gap-2 items-center'>
                                <BookCopy className="text-zinc-400" size={16} />
                                <h3 className="font-medium text-gray-800">{repo.name}</h3>
                            </div>
                            <div className='flex gap-2 items-center mt-1'>
                                <Route className="text-zinc-400" size={16} />
                                <p className="text-sm text-gray-600">{repo.full_name}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            {repo.backend_path && (
                                <span className="text-xs px-2 py-1 bg-indigo-50 text-indigo-600 rounded-full">
                                    {repo.backend_path}
                                </span>
                            )}
                            <span className={`w-2 h-2 rounded-full ${repo.is_active ? 'bg-green-500' : 'bg-gray-300'}`} title={repo.is_active ? 'Active' : 'Inactive'} />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default function Repository() {
    const [isLoading, setIsLoading] = useState(true);
    const [repositoriesData, setRepositoriesData] = useState(null);

    useEffect(() => {
        const fetchRepositories = async () => {
            try {
                const tokenInfo = localStorage.getItem('tokenInfo');
                if (!tokenInfo) {
                    throw new Error('No token found');
                }

                const response = await fetch('http://localhost:8000/api/repo/list', {
                    headers: {
                        'Authorization': `Bearer ${JSON.parse(tokenInfo).access_token}`,
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch repositories');
                }

                const data = await response.json();
                setRepositoriesData(data);
            } catch (error) {
                console.error('Error fetching repositories:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchRepositories();
    }, []);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
            </div>
        );
    }

    return (
        <div className='py-32'>
            {repositoriesData && repositoriesData.length > 0 ? (
                <RepositoryList repositories={repositoriesData} />
            ) : (
                <div className="flex flex-col items-center justify-center py-12 px-4">
                    <div className="h-24 w-24 text-gray-300 mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                        </svg>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No repositories found</h3>
                    <p className="text-gray-600 max-w-sm mb-6 text-center">
                        We couldn't find any repositories in your GitHub account. Make sure you have repositories with the required access permissions.
                    </p>
                    <button
                        onClick={() => window.open('https://github.com/new', '_blank')}
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        Create New Repository
                    </button>
                </div>
            )}
        </div>
    );
}