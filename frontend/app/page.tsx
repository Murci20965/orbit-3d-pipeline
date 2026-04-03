"use client";
import { useState } from "react";
import dynamic from "next/dynamic";
import { Loader2, Send, Box, GraduationCap, Upload, X } from "lucide-react";

const ThreeViewer = dynamic<{ url: string }>(
  () => import("../components/ThreeViewer").then((mod) => mod.ThreeViewer), 
  { ssr: false, loading: () => <div className="flex-grow min-h-[500px] bg-zinc-900/20 border border-zinc-800/50 rounded-2xl flex items-center justify-center"><p className="text-blue-400 animate-pulse font-medium">Booting 3D Engine...</p></div> }
);

export default function Dashboard() {
  const[prompt, setPrompt] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const[loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPrompt(""); // Clear the text prompt if the user uploads an image
      setPreview(URL.createObjectURL(selectedFile));
    }
  };

  const removeFile = () => {
    setFile(null);
    setPreview(null);
  };

const generateMesh = async () => {
    if (!prompt && !file) return;
    setLoading(true);
    setResult(null);

    try {
      const engineUrl = process.env.NEXT_PUBLIC_ENGINE_URL || "http://localhost:8000";
      
      const formData = new FormData();
      if (prompt) formData.append("prompt", prompt);
      if (file) formData.append("file", file);

      console.log(`[*] API Request: Sending multimodal generation payload to ${engineUrl}/generate`);
      
      const res = await fetch(`${engineUrl}/generate`, {
        method: "POST",
        body: formData, 
      });
      
      if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
      const data = await res.json();

      if (data.status === "success") {
        setResult(data);
      } else {
        alert("Pipeline Error: " + (data.detail || data.message));
      }
    } catch (error) {
      console.error("[!] API Request Failed:", error);
      alert("Network Error: Connection to the API failed. Please ensure the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 max-w-6xl mx-auto flex flex-col gap-8">
      <header className="flex items-center gap-3 border-b border-zinc-800 pb-6">
        <Box className="w-8 h-8 text-blue-500" />
        <h1 className="text-3xl font-bold tracking-tight">Orbit-3D Engine</h1>
        <span className="ml-auto bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full text-sm font-medium border border-blue-500/20">
          v1.0.0 Production
        </span>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="flex flex-col gap-6 lg:col-span-1">
          <div className="bg-zinc-900/40 p-6 rounded-2xl border border-zinc-800/50 shadow-xl">
            <h2 className="text-lg font-semibold mb-4 text-zinc-200">Multimodal Generator</h2>
            <div className="flex flex-col gap-4">
              
              {/* Text Input */}
              <textarea 
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-4 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all disabled:opacity-50"
                rows={3}
                placeholder="Describe an object (e.g., 'A vintage brass telescope')"
                value={prompt}
                disabled={!!file} // Disable text if image is uploaded
                onChange={(e) => setPrompt(e.target.value)}
              />

              <div className="flex items-center gap-2 w-full">
                <hr className="flex-grow border-zinc-800" />
                <span className="text-xs text-zinc-500 font-medium">OR UPLOAD IMAGE</span>
                <hr className="flex-grow border-zinc-800" />
              </div>

              {/* Image Upload Zone */}
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <label className="flex flex-col items-center justify-center w-full p-4 border-2 border-dashed border-zinc-700 rounded-xl cursor-pointer hover:border-blue-500 hover:bg-blue-500/10 transition-all">
                    <input type="file" accept="image/png, image/jpeg, image/webp" className="hidden" onChange={handleFileChange} />
                    <Upload className="w-5 h-5 text-zinc-400 mb-1" />
                    <span className="text-xs text-zinc-400 font-medium">Select JPG/PNG</span>
                  </label>
                </div>
                {preview && (
                  <div className="w-16 h-16 rounded-xl overflow-hidden border border-blue-500/50 relative shadow-lg shadow-blue-500/20">
                    <img src={preview} alt="Preview" className="object-cover w-full h-full" />
                    <button onClick={removeFile} className="absolute top-0 right-0 bg-red-500/90 text-white p-1 rounded-bl-lg hover:bg-red-600 transition-colors">
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                )}
              </div>

              <button 
                onClick={generateMesh}
                disabled={loading || (!prompt && !file)}
                className="w-full mt-2 bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-xl flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-900/20"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                {loading ? "Generating 3D Asset..." : "Generate 3D Asset"}
              </button>
            </div>
          </div>

          {result?.educational_context && (
            <div className="bg-emerald-950/20 p-6 rounded-2xl border border-emerald-900/30 shadow-xl animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div className="flex items-center gap-2 mb-3 text-emerald-400">
                <GraduationCap className="w-5 h-5" />
                <h3 className="font-semibold">Llama-3 Insights</h3>
              </div>
              <p className="text-emerald-100/80 text-sm leading-relaxed">
                {result.educational_context}
              </p>
            </div>
          )}
        </div>

        <div className="lg:col-span-2 flex flex-col">
          {result?.optimized_web_url ? (
            <div className="flex-grow min-h-[500px] animate-in zoom-in-95 duration-700">
              <ThreeViewer url={result.optimized_web_url} />
            </div>
          ) : (
            <div className="flex-grow min-h-[500px] bg-zinc-900/20 border border-zinc-800/50 rounded-2xl border-dashed flex items-center justify-center text-zinc-600 shadow-inner">
              <div className="text-center flex flex-col items-center gap-4">
                <Box className={`w-12 h-12 ${loading ? 'animate-bounce text-blue-500' : 'opacity-50'}`} />
                <div>
                  <p className="font-medium text-zinc-400">Waiting for generation...</p>
                  {loading && <p className="text-sm text-blue-400/80 mt-1">Running Pipeline... This takes ~90 seconds</p>}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}