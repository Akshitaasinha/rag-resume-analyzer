import { useDropzone } from "react-dropzone";
import { useState } from "react";
import toast from "react-hot-toast";
import { uploadResume } from "../api/client";

export default function UploadZone({ onSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [files, setFiles] = useState([]);

  const onDrop = async (accepted) => {
    const pdfs = accepted.filter(f => f.type === "application/pdf");
    if (!pdfs.length) { toast.error("PDF only"); return; }
    setUploading(true);
    for (const file of pdfs) {
      try {
        const res = await uploadResume(file);
        setFiles(p => [...p, { name: file.name, chunks: res.chunks_created }]);
        toast.success(`${file.name} — ${res.chunks_created} chunks indexed`);
        onSuccess?.(res);
      } catch { toast.error(`Failed: ${file.name}`); }
    }
    setUploading(false);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { "application/pdf": [".pdf"] }, multiple: true
  });

    return (
    <div className="space-y-4">
      <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-200 hover:border-gray-300"}`}>
        <input {...getInputProps()} />
        {uploading ? <p className="text-blue-600 font-medium">Indexing...</p>
          : isDragActive ? <p className="text-blue-600">Drop PDFs here</p>
          : <><p className="text-gray-600 font-medium">Drag and drop resumes here</p>
             <p className="text-gray-400 text-sm mt-1">PDF only · click to browse</p></>}
      </div>
      {files.map((f,i) => (
        <div key={i} className="flex justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
          <span className="text-sm text-green-800 font-medium">{f.name}</span>
          <span className="text-xs text-green-600">{f.chunks} chunks</span>
        </div>
      ))}
    </div>
  );
}