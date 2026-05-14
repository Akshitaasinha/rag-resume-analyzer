export default function ResultCard({ item }) {
  const c={rag:"bg-blue-50 text-blue-700 border-blue-200",agent:"bg-purple-50 text-purple-700 border-purple-200",error:"bg-red-50 text-red-700 border-red-200"};
  return (
    <div className="border border-gray-100 rounded-xl p-5 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-medium text-gray-800">{item.question}</p>
        <span className={`text-xs px-2 py-0.5 rounded border flex-shrink-0 ${c[item.mode]}`}>{item.mode}</span>
      </div>
      <div className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap bg-gray-50 rounded-lg p-4">{item.answer}</div>
    </div>
  );
}