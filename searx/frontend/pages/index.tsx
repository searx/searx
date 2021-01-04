import Link from 'next/link';
import { useRouter } from 'next/router';
import React from 'react';

import Navbar from '../components/Navbar';

const Home = () => {
  const [query, setQuery] = React.useState("");
  const { push } = useRouter();
  const handleSearchKeypress = (event) => {
    if (event.key == "Enter") {
      push(`/search?q=${query}`);
    }
  };

  return (
    <div className="h-screen flex flex-col justify-between">
      <Navbar />
      <main className="flex flex-col justify-center items-center space-y-3 mb-12">
        <div className="mb-6">
          <img src="/images/logo_searx_a.png" className="w-64" />
        </div>
        <div className="relative text-gray-900">
          <input
            type="text"
            className="h-12 w-96 pr-8 pl-5 rounded z-0 focus:shadow focus:outline-none"
            placeholder="Search for..."
            value={query}
            onChange={(e) => setQuery(e.currentTarget.value)}
            onKeyPress={handleSearchKeypress}
          />
          <div className="absolute top-3 right-3">
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              ></path>
            </svg>
          </div>
        </div>
        <button>Advanced Settings</button>
      </main>
      <footer className="flex justify-center items-center flex-col space-y-2 py-2 text-xs">
        <div>
          Powered by searx - Fork - a privacy-respecting, hackable search engine
        </div>
        <div>Source Code | Issue Tracker | Public Instances</div>
      </footer>
    </div>
  );
};
export default Home;
