import React, { useState } from 'react';
import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';
import YAML from 'yaml';
import { FileJson, Download, GitGraph, X } from 'lucide-react';
import { FaFilePdf as FilePdf } from "react-icons/fa6";
import Modal from 'react-modal';
import MermaidViewer from './MermaidViewer';

// Set the app element for accessibility
Modal.setAppElement('#root');  // Make sure to set this to your root element id

const Docs = ({ docs, diagram }) => {
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const spec = typeof docs === 'string' ? YAML.parse(docs) : docs;
  
  const customModalStyles = {
    content: {
      top: '50%',
      left: '50%',
      right: 'auto',
      bottom: 'auto',
      marginRight: '-50%',
      transform: 'translate(-50%, -50%)',
      width: '90%',
      maxWidth: '1200px',
      height: '80vh',
      padding: '20px',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      backgroundColor: 'white',
    },
    overlay: {
      backgroundColor: 'rgba(0, 0, 0, 0.75)',
      zIndex: 1000,
    }
  };

  const downloadAsYAML = () => {
    const yamlString = YAML.stringify(spec);
    const blob = new Blob([yamlString], { type: 'application/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'api-documentation.yaml';
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadAsJSON = () => {
    const jsonString = JSON.stringify(spec, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'api-documentation.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-full">
      {/* Export buttons */}
      <div className="flex justify-end gap-2 p-4 bg-white border-b">
        <button
          onClick={downloadAsYAML}
          className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <FileJson className="h-4 w-4 mr-2" />
          Export YAML
        </button>
        <button
          onClick={downloadAsJSON}
          className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <Download className="h-4 w-4 mr-2" />
          Export JSON
        </button>
        <button
          onClick={() => setModalIsOpen(true)}
          className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <GitGraph className="h-4 w-4 mr-2" />
          View Dependency
        </button>
      </div>

      {/* Modal for Dependency Graph */}
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={() => setModalIsOpen(false)}
        style={customModalStyles}
        contentLabel="Dependency Graph"
      >
        <div className="h-full flex flex-col">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">API Dependency Graph</h2>
            <button
              onClick={() => setModalIsOpen(false)}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <div className="flex-1 overflow-auto">
            <MermaidViewer diagram={diagram} />
          </div>
        </div>
      </Modal>

      {/* Documentation */}
      <div className="docs-container">
        <SwaggerUI 
          spec={spec}
          docExpansion="list" 
          defaultModelsExpandDepth={-1}  
          filter={true}  
          tryItOutEnabled={true}
          supportedSubmitMethods={['get', 'post', 'put', 'delete', 'patch']}
        />
      </div>
    </div>
  );
};

export default Docs;