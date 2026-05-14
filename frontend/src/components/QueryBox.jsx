import { useState } from "react";
import { queryResumes } from "../api/client";
const EX = ["Find Python ML engineers","Who has strongest backend background?","What skills are missing for senior AI role?","Rank by leadership experience"];

export default function QueryBox({ onResult }) {
  const [q, setQ] = useState("");
  const [agent, setAgent] = useState(false);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!q.trim()) return;
    setLoading(true);
    try {
      const data = await queryResumes(q, agent);
      onResult({ question: q, answer: data.answer, mode: agent ? "agent" : "rag" });
      setQ("");
    } catch (err) { onResult({ question: q, answer: "Error: "+err.message, mode: "error" }); }
    finally { setLoading(false); }
  };
    return (
    <div className="space-y-4">
      <form onSubmit={submit} className="flex gap-3">
        <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Ask about candidates..." disabled={loading}
          className="flex-1 px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-blue-400" />
        <button type="submit" disabled={loading||!q.trim()} className="px-5 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium disabled:opacity-40">{loading ? "Thinking..." : "Search"}</button>
      </form>
      <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
        <input type="checkbox" checked={agent} onChange={e=>setAgent(e.target.checked)} className="rounded"/>
        Use ReAct agent (smarter, ~10s) vs RAG chain (fast, ~2s)
      </label>
      <div className="flex flex-wrap gap-2">
        {EX.map((ex,i)=><button key={i} onClick={()=>setQ(ex)} className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600">{ex}</button>)}
      </div>
    </div>
  );
}