import { useState } from "react";
import { Toaster } from "react-hot-toast";
import UploadZone from "./components/UploadZone";
import QueryBox from "./components/QueryBox";
import ResultCard from "./components/ResultCard";

export default function App() {
  const [page, setPage] = useState("upload");
  const [results, setResults] = useState([]);
  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      <nav className="bg-white border-b border-gray-100 px-6 py-3 flex items-center gap-6">
        <span className="font-semibold text-gray-900">ResumeRAG</span>
        {["upload","query"].map(p=>(
          <button key={p} onClick={()=>setPage(p)} className={`px-4 py-1.5 rounded-md text-sm capitalize ${page===p?"bg-blue-600 text-white":"text-gray-500 hover:text-gray-700"}`}>{p}</button>
        ))}
      </nav>
      <div className="max-w-2xl mx-auto py-12 px-4">
        {page==="upload"
          ? <><h1 className="text-2xl font-semibold mb-8">Resume ingestion</h1><UploadZone /></>
          : <><h1 className="text-2xl font-semibold mb-8">Query candidates</h1>
             <QueryBox onResult={r=>setResults(p=>[r,...p])} />
             <div className="mt-8 space-y-4">{results.map((r,i)=><ResultCard key={i} item={r}/>)}</div></>}
      </div>
    </div>
  );
}


// Open: http://localhost:5173