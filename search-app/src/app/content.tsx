'use client';
import React, { useState, useMemo } from "react";

const ResultItem = ({ filePath }) => {
    const parts = filePath.split('/'); // Split the string by "/"
    return (
      <div className="bg-white bg-white text-gray-700 shadow-md p-4 rounded-lg mb-4 hover:bg-gray-100 transition" dir="ltr">
        {parts.map((part, index) => (
        <React.Fragment key={index}>
          {part}
          {index < parts.length - 1 && <strong className="mx-1">/</strong>} {/* Bold "/" */}
        </React.Fragment>
      ))}
      </div>
    );
  };

export default function Content({ indices }) {
    const [selectedIndex, setSelectedIndex] = useState("");
    const [searchResults, setSearchResults] = useState(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const fetchSearchResults = async () => {
        setIsLoading(true);
        const params = new URLSearchParams({
            query: searchQuery, // The text search query
            index: selectedIndex, // The index/category
          });
        const response = await fetch(`/api/search?${params.toString()}`);
        const data = await response.json();
        setSearchResults(data);
        setIsLoading(false);
    };
    
    const selectedIndexItem = useMemo(() => indices.find((item) => item.index === selectedIndex), [indices, selectedIndex]);
    const isSearchDisabled = !selectedIndexItem || isLoading || !searchQuery || searchQuery.length < 3;
    return (
    <>
    <div className="flex flex-col items-center w-full max-w-lg mb-6">
    <select
      className="border border-gray-300 bg-white text-gray-700 rounded p-2 mb-4 w-full"
      value={selectedIndex}
      onChange={(e) => setSelectedIndex(e.target.value)}
    >
      <option value="" disabled>קורס</option>
      {indices.map((item: any) => (
        <option key={item.index} value={item.index}>
          {item.index}
        </option>
      ))}
    </select>
      
      {selectedIndexItem && <div className="mt-4 text-sm text-gray-600">
        עודכן לאחרונה ב {selectedIndexItem?.lastUpdated?.split('T')[0]} ומכיל {selectedIndexItem.documentsCount} מסמכים
      </div>}
  </div>

  {/* Search Bar */}
  <div className="flex items-center w-full max-w-lg">
  <input
    type="text"
    value={searchQuery}
    onChange={(e) => setSearchQuery(e.target.value)}
    placeholder="חפש משהו..."
    className="w-full p-2 border bg-white text-gray-700 border-gray-300 rounded-r-md focus:outline-none focus:ring-2 focus:ring-blue-500"
  />
  <button
      disabled={isLoading}
      className={`bg-blue-500 text-white p-2 rounded-l-md hover:bg-blue-600 transition flex items-center justify-center ${
        isSearchDisabled ? 'opacity-50 cursor-not-allowed' : ''
      }`}
      onClick={fetchSearchResults}
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="size-6">
<path fillRule="evenodd" d="M10.5 3.75a6.75 6.75 0 1 0 0 13.5 6.75 6.75 0 0 0 0-13.5ZM2.25 10.5a8.25 8.25 0 1 1 14.59 5.28l4.69 4.69a.75.75 0 1 1-1.06 1.06l-4.69-4.69A8.25 8.25 0 0 1 2.25 10.5Z" clipRule="evenodd" />
</svg>
    </button>
    </div>
    {searchResults !== null && (<div className="mt-6 w-full max-w-3xl mx-auto">
      {searchResults.length > 0 ? (
        searchResults.map((result, index) => (
          <ResultItem key={index} filePath={result.file_path} />
        ))
      ) : (
        <p className="text-center text-gray-500">אין תוצאות</p>
      )}
    </div>)}
</>)
}