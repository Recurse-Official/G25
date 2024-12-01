import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { LucideBookOpen, Info, Hash, BookCopy, Route, Folder, ChevronDown, ChevronRight, CircleDotDashed, ArrowLeft, Loader2, FileIcon, MessageSquare } from 'lucide-react';
import { toast } from 'react-toastify';
import Modal from 'react-modal';
import Docs from '../components/Docs';

Modal.setAppElement('#root'); // or '#__next' for Next.js

const customStyles = {
    content: {
        top: '50%',
        left: '50%',
        right: 'auto',
        bottom: 'auto',
        transform: 'translate(-50%, -50%)',
        maxWidth: '400px',
        width: '90%',
        padding: '20px',
        borderRadius: '8px',
    },
    overlay: {
        backgroundColor: 'rgba(0, 0, 0, 0.75)'
    }
};

const TreeView = ({ data }) => {
    const [expanded, setExpanded] = useState({});

    const toggleDir = (path) => {
        setExpanded(prev => ({
            ...prev,
            [path]: !prev[path]
        }));
    };

    const renderTree = (items) => {
        return items.map(item => (
            <div key={item.path} className="ml-4">
                {item.type === 'directory' ? (
                    <div>
                        <div
                            onClick={() => toggleDir(item.path)}
                            className="flex items-center gap-2 py-1 hover:bg-gray-50 cursor-pointer text-sm group"
                        >
                            <div className={`transform transition-transform duration-200 ${expanded[item.path] ? 'rotate-90' : ''}`}>
                                <ChevronRight size={16} />
                            </div>
                            <Folder size={16} className="text-blue-500" />
                            <span>{item.name}</span>
                        </div>
                        <div className={`overflow-hidden transition-all duration-200 ${expanded[item.path] ? 'max-h-[1000px] opacity-100' : 'max-h-0 opacity-0'}`}>
                            <div className="ml-2 border-l border-gray-200">
                                {renderTree(item.children)}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center gap-2 py-1 pl-6 text-sm text-gray-600">
                        <FileIcon size={16} className="text-gray-400" />
                        <span>{item.name}</span>
                    </div>
                )}
            </div>
        ));
    };

    return renderTree(data);
};

export default function RepositoryDetails() {

    const id = parseInt(useParams().id);
    const location = useLocation();
    const repo = location.state?.repo;
    const [activeTab, setActiveTab] = useState('details');

    const [repository, setRepository] = useState(repo);
    const [backendPath, setBackendPath] = useState(repo.backend_path || '');
    const [repoDetails, setRepoDetails] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const navigate = useNavigate();
    const tabs = [
        { id: 'details', label: 'Details', icon: Info },
        { id: 'status', label: 'Repository Status', icon: CircleDotDashed },
        { id: 'docs', label: 'Documentation', icon: LucideBookOpen },
        { id: 'chat', label: 'Chat', icon: MessageSquare }
    ];

    // const diagram = `
    //     graph TD
    //     A[Start] --> B[Process]
    //     B --> C[End]
    // `;

    // State declarations
    const [docs, setDocs] = useState(null);
    const [diagram, setDiagram] = useState(null);
    const [docsLoading, setDocsLoading] = useState(false);

    const fetchDocumentation = async () => {
        const fullName = repository.full_name;
        const accessToken = JSON.parse(localStorage.getItem('tokenInfo')).access_token;

        if (!fullName || !accessToken) {
            toast.error('Invalid repository details');
            return null;
        }

        try {
            setDocsLoading(true);
            const response = await fetch('http://localhost:8000/api/repo/read_docs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    full_name: fullName,
                    access_token: accessToken
                })
            });

            const responseData = await response.json();

            if (!response.ok) {
                toast.error(responseData.Message || 'Failed to fetch documentation');
                console.error('Error response:', responseData);
                setDocsLoading(false);
                setDocs(null);
                setDiagram(null);
                return;
            }

            if (responseData.Message === "Documentation files not found in doccie branch") {
                toast.info('Could not find documentation files');
                setDocsLoading(false);
                setDocs(null);
                setDiagram(null);
                return;
            }

            // Update both documentation and dependency states
            if (responseData.data) {
                setDocs(responseData.data);
            }

            if (responseData.dependency) {
                setDiagram(responseData.dependency);
            } else {
                setDiagram(null);
            }

            toast.success('Documentation fetched successfully');
            setDocsLoading(false);

        } catch (error) {
            console.error('Error fetching documentation:', error);
            toast.error('Failed to fetch documentation');
            setDocsLoading(false);
            setDocs(null);
            setDiagram(null);
            return null;
        }
    };

    // Function to activate a repository
    const activateRepository = async (repoData) => {
        try {
            const req = JSON.stringify({
                id: repoData.id,
                name: repoData.name,
                full_name: repoData.full_name,
                is_active: "true",
                backend_path: repoData.backend_path
            });
            const response = await fetch('http://localhost:8000/api/github/create-webhook', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('tokenInfo')).access_token}`,
                    'Content-Type': 'application/json',
                },
                body: req
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                toast.error(data.Message || 'Failed to activate repository');
                return
            }

            toast.success('Repository is now montiored');
            return data;
        } catch (error) {
            console.error('Error activating repository:', error);
            throw error;
        }
    };
    
    // Function to deactivate a repository
    const deactivateRepository = async (repoData) => {
        
        try {
            const req = JSON.stringify({
                id: repoData.id,
                name: repoData.name,
                full_name: repoData.full_name,
                is_active: "true",
                backend_path: repoData.backend_path
            });

            const response = await fetch('http://localhost:8000/api/github/delete-webhook', {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('tokenInfo')).access_token}`,
                    'Content-Type': 'application/json',
                },
                body: req
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.Message || 'Failed to deactivate repository');
                return
            }

            setRepository(prev => ({
                ...prev,
                is_active: false
            }));
            toast.warn('Repository is no longer montiored');
            setIsModalOpen(false);
            return data;
        } catch (error) {
            console.error('Error deactivating repository:', error);
            throw error;
        }
    };

    const switchTab = (tabId) => {
        setActiveTab(tabId);
        if (tabId === 'docs' && docs == null) {
            fetchDocumentation();
        }
    };

    const handleRepositoryToggle = async () => {
        const shouldActivate = !repository.is_active;
        try {
            if (shouldActivate) {
                console.log("Activate the repository")
                if (repository.backend_path === "" || repository.backend_path === null) {
                    toast.error('Please enter a valid backend path');
                    return;
                }
                const result = await activateRepository(repository);
                console.log('Repository activated:', result);
                setRepository(prev => ({
                    ...prev,
                    is_active: true
                }));
            } else {
                setIsModalOpen(true);
            }
        } catch (error) {
            console.error('Failed to toggle repository:', error);
        }

    };

    const handlePathChange = (e) => {
        setBackendPath(e.target.value);
        setRepository(prev => ({
            ...prev,
            backend_path: e.target.value
        }));
    };

    useEffect(() => {
        if (repoDetails || !id) {
            setIsLoading(false);
            return;
        }

        const getRepositoryDetails = async (repoId) => {
            try {
                const tokenInfo = localStorage.getItem('tokenInfo');
                if (!tokenInfo) {
                    throw new Error('No authentication token found');
                }

                const response = await fetch(`http://localhost:8000/api/repo/${repoId}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${JSON.parse(tokenInfo).access_token}`,
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch repository details');
                }

                const data = await response.json();
                setRepoDetails(data);
                setIsLoading(false);
                console.log(data);
            } catch (error) {
                console.error('Error fetching repository details:', error);
                toast.error('Failed to fetch repository details');
                setIsLoading(false);
            }
        };

        getRepositoryDetails(id);
    }, [id, repoDetails]); // Added proper dependencies

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
            </div>
        );
    }
    return (
        <div className="py-32">
            <Modal
                isOpen={isModalOpen}
                onRequestClose={() => setIsModalOpen(false)}
                style={customStyles}
                contentLabel="Confirm Deactivation"
            >
                <div className="space-y-4">
                    <h2 className="text-xl font-semibold">Confirm Deactivation</h2>
                    <p className="text-gray-600">
                        Are you sure you want to deactivate repository "{repository.name}"?
                        This will remove it from active monitoring.
                    </p>
                    <div className="flex justify-end gap-2 mt-6">
                        <button
                            onClick={() => setIsModalOpen(false)}
                            className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={() => deactivateRepository(repository)}
                            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                        >
                            Deactivate
                        </button>
                    </div>
                </div>
            </Modal>

            <div className="max-w-7xl mx-auto px-4">
                <div className="flex justify-between items-start mb-8">
                    <div className="">
                        <div className='flex items-center gap-3'>
                            <span
                                className={`h-2.5 w-2.5 rounded-full ${repository.is_active ? 'bg-green-500' : 'bg-red-500'}`}
                                title={repository.is_active ? 'Active' : 'Inactive'}
                            />
                            <h1 className="text-2xl font-semibold mb-1">{repository.name}</h1>
                        </div>
                        <p className="text-sm text-gray-500">{repository.full_name}</p>
                    </div>
                    <div
                        className="flex items-center gap-3 cursor-pointer"
                        onClick={() => navigate('/repository')}
                    >
                        <ArrowLeft size={20} className="text-gray-500" />
                        <span className="text-sm text-gray-500">View all Repositories</span>
                    </div>
                </div>

                <div className="border-b border-gray-200 mb-6">
                    <nav className="flex gap-8">
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => switchTab(tab.id)}
                                className={`flex items-center gap-2 px-1 py-4 text-sm font-medium border-b-2 transition-colors ${activeTab === tab.id
                                    ? 'border-indigo-500 text-indigo-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                <tab.icon size={16} />
                                {tab.label}
                            </button>
                        ))}
                    </nav>
                </div>

                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    {
                        activeTab === 'details' ? (
                            <div className="flex gap-8">
                                <div className="flex-1 space-y-4">
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <Hash size={16} className="text-gray-400" />
                                            <label className="text-sm font-medium text-gray-700">Repository ID</label>
                                        </div>
                                        <p className="mt-1">{repository.id}</p>
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <BookCopy size={16} className="text-gray-400" />
                                            <label className="text-sm font-medium text-gray-700">Name</label>
                                        </div>
                                        <p className="mt-1">{repository.name}</p>
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <Route size={16} className="text-gray-400" />
                                            <label className="text-sm font-medium text-gray-700">Full Name</label>
                                        </div>
                                        <p className="mt-1">{repository.full_name}</p>
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <Route size={16} className="text-gray-400" />
                                            <label className="text-sm font-medium text-gray-700">Visibility</label>
                                        </div>
                                        <p className="mt-1">{repoDetails.visibility}</p>
                                    </div>
                                </div>

                                <div className="flex-1">
                                    <h3 className="text-sm font-medium text-gray-700 mb-4">Directory Structure</h3>
                                    <div className="border rounded-lg p-4 bg-gray-50">
                                        <TreeView data={repoDetails.directory_structure} />
                                    </div>
                                </div>
                            </div>
                        ) :

                            activeTab === 'status' ? (
                                <div className="space-y-6">
                                    <div className="space-y-1.5">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Folder size={16} className="text-gray-400" />
                                            <label className="text-sm font-medium text-gray-700">Backend Path</label>
                                        </div>
                                        <div className="relative">
                                            <input
                                                type="text"
                                                value={backendPath}
                                                onChange={handlePathChange}
                                                disabled={repository.is_active}
                                                placeholder="Enter Path to your backend Directory"
                                                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 placeholder-gray-400 text-sm"
                                            />
                                        </div>
                                    </div>

                                    <div className="border-t pt-6">
                                        <div className="flex items-center justify-between mb-6">
                                            <div>
                                                <h3 className="text-sm font-medium text-gray-700">Repository Status</h3>
                                                <p className="mt-1 text-sm text-gray-500">
                                                    {repository.is_active ? 'Repository is currently active' : 'Repository is currently inactive'}
                                                </p>
                                            </div>
                                            <span className={`px-3 py-1 rounded-full text-sm ${repository.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                                                {repository.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </div>

                                        <button
                                            onClick={handleRepositoryToggle}
                                            className={`px-4 py-2 rounded-lg text-sm font-medium ${repository.is_active
                                                ? 'bg-red-50 text-red-700 hover:bg-red-100'
                                                : 'bg-green-50 text-green-700 hover:bg-green-100'
                                                }`}
                                        >
                                            {repository.is_active ? 'Deactivate Repository' : 'Activate Repository'}
                                        </button>
                                    </div>
                                </div>
                            ) :

                                activeTab === 'docs' ? (
                                    <div>
                                        {docsLoading ? (
                                            <div className="min-h-[200px] flex items-center justify-center">
                                                <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
                                            </div>
                                        ) : docs == null ? (
                                            <div className="min-h-[200px] flex items-center justify-center">
                                                <p className="text-gray-500">No documentation found</p>
                                            </div>
                                        ) : (
                                            <div className="space-y-4">
                                                <h3 className="text-sm font-medium text-gray-700">Documentation</h3>
                                                <div className="border rounded-lg p-4 bg-gray-50">
                                                    <Docs docs={docs} diagram={diagram} />
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ) : null
                    }
                </div>
            </div>
        </div>
    );
}