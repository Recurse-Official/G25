import React from 'react';
import { Brain, Lock } from 'lucide-react';
import { FaGithub } from "react-icons/fa";


const FeatureCard = ({ title, description, icon: Icon }) => {
  return (
    <div 
      className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 relative overflow-hidden hover:shadow-xl transition-shadow duration-300"
    >

      <div className="mb-6 relative flex items-center justify-center w-full">
        <div className="w-14 h-14 bg-indigo-50 rounded-lg flex items-center justify-center relative z-10">
          <Icon className="w-7 h-7 text-[#6366F1]" />
        </div>
      </div>

      <h3 className="text-gray-900 text-xl font-semibold mb-3">{title}</h3>
      <p className="text-gray-600 text-sm leading-relaxed">{description}</p>

    </div>
  );
};

const Features = () => {
  const features = [
    {
      title: 'Real-time Sync',
      description: 'Documentation automatically updates with your code changes through GitHub webhooks.',
      icon: FaGithub
    },
    {
      title: 'AI-Powered',
      description: 'Intelligent analysis of your codebase using advanced AI agents to generate comprehensive docs.',
      icon: Brain
    },
    {
      title: 'Privacy First',
      description: 'All documentation lives in your repository. No external storage or privacy concerns.',
      icon: Lock
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {features.map((feature, index) => (
        <FeatureCard
          key={index}
          title={feature.title}
          description={feature.description}
          icon={feature.icon}
        />
      ))}
    </div>
  );
};

export default Features;