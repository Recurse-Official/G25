import React, { useEffect } from 'react';
import Features from '../components/Features';
import { Link } from 'react-router-dom';

const NavButton = ({ children, variant = 'ghost', onClick }) => {
  const baseStyle = "px-4 py-2 rounded-lg font-medium transition-colors duration-200";
  const styles = {
    ghost: "hover:bg-gray-100 text-gray-700",
    primary: "bg-[#24292f] text-white hover:bg-[#31373d] flex items-center gap-2 py-2.5 px-5 text-[16px] rounded-md",
    outline: "border border-gray-300 hover:bg-gray-50",
    danger: "bg-red-500 text-white hover:bg-red-600"
  };

  return (
    <button
      className={`${baseStyle} ${styles[variant]}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};


export default function Home() {

  return (
    <div className="min-h-screen pt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb- text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-6">
          How engineers build
          <div className="mt-2 text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-indigo-400">
            Documentation
          </div>
        </h1>

        <p className="text-xl text-gray-600 mb-5 max-w-2xl mx-auto">
          An open-source platform to automatically generate, maintain, and synchronize API documentation with your codebase.
        </p>

        <div className="flex justify-center gap-4">
          <Link to="/repository">
            <NavButton variant="primary">
              Build Your Docs
            </NavButton>
          </Link>
        </div>

        <section className="py-5">
          <Features />
        </section>
      </div>
    </div>
  );
}