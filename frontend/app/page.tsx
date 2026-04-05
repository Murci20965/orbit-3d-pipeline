"use client";
import { useState, useRef } from "react";
import dynamic from "next/dynamic";
import { Loader2, Send, Box, Image as ImageIcon, X, MousePointer2, MoveVertical, Zap } from "lucide-react";

const ThreeViewer = dynamic<{ url: string }>(
  () => import("../components/ThreeViewer").then((mod) => mod.ThreeViewer), 
  { 
    ssr: false, 
    loading: () => <div className="absolute inset-0 flex items-center justify-center text-blue-500 animate-pulse font-medium">Booting 3D Engine...</div> 
  }
);

export default function OrbitDashboard() {
  const [prompt, setPrompt] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const quickPrompts =[
    "A vintage brass telescope",
    "A low polygon gold crown",
    "A futuristic space helmet",
    "A worn leather armchair"
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPrompt("");
      setPreview(URL.createObjectURL(selectedFile));
    }
  };

  const removeFile = () => {
    setFile(null);
    setPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
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

      console.log(`[*] API Request: Sending multimodal payload to ${engineUrl}/generate`);
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
      alert("Network Error: Could not reach the API.");
    } finally {
      setLoading(false);
    }
  };

  // Determine System State for the UI
  const currentSystemState = loading 
    ? "Processing Pipeline..." 
    : result 
      ? "Optimization Complete" 
      : "Idle";

  return (
    <main className="flex h-screen w-full bg-[#1e1e21] text-zinc-200 overflow-hidden font-sans">
      
      {/* LEFT SIDEBAR: Controls & Context */}
      <aside className="w-80 flex-shrink-0 bg-[#161618] border-r border-zinc-800/50 p-6 flex flex-col z-10 shadow-2xl relative">
        
        {/* BRANDING */}
        <div className="flex items-center gap-3 mb-8 pb-6 border-b border-zinc-800/80">
          <Box className="w-7 h-7 text-blue-500" />
          <div>
            <h1 className="text-lg font-bold tracking-tight leading-tight">Orbit-3D</h1>
            <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Asset Pipeline</p>
          </div>
        </div>

        {/* SYSTEM STATE */}
        <div className="mb-8">
          <h2 className="text-[10px] font-bold text-zinc-500 tracking-widest uppercase mb-3">System State</h2>
          <div className="flex items-center gap-3 bg-blue-900/20 border border-blue-800/40 rounded-lg px-4 py-3">
            <div className={`w-2 h-2 rounded-full ${loading ? 'bg-blue-500 animate-ping' : 'bg-blue-500 animate-pulse'}`} />
            <span className="text-blue-400 text-sm font-medium">{currentSystemState}</span>
          </div>
        </div>

        {/* Llama-3/4 INSIGHTS */}
        <div className="mb-8 flex-1">
          <h2 className="text-[10px] font-bold text-zinc-500 tracking-widest uppercase mb-3">Llama Vision Logic</h2>
          <div className="bg-[#1a1a1c] border border-zinc-800/80 rounded-xl p-4 min-h-[100px] shadow-sm">
            <p className="text-sm text-zinc-400 leading-relaxed">
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" /> Analyzing input...
                </span>
              ) : result?.educational_context ? (
                <span className="text-zinc-300">{result.educational_context}</span>
              ) : (
                "Action completed. Standing by for next generation prompt."
              )}
            </p>
          </div>
        </div>

        {/* QUICK PROMPTS */}
        <div className="overflow-y-auto pr-2 custom-scrollbar pb-6">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-3.5 h-3.5 text-amber-500" />
            <h2 className="text-[10px] font-bold text-zinc-500 tracking-widest uppercase">Quick Prompts</h2>
          </div>
          <div className="flex flex-col gap-2.5">
            {quickPrompts.map((p, i) => (
              <button
                key={i}
                onClick={() => { setPrompt(p); removeFile(); }}
                disabled={loading}
                className="text-left px-4 py-3.5 rounded-xl border border-zinc-800/80 bg-[#1a1a1c] hover:bg-zinc-800 hover:border-zinc-700 transition-all text-xs text-zinc-300 shadow-sm disabled:opacity-50"
              >
                "{p}"
              </button>
            ))}
          </div>
        </div>
      </aside>

      {/* MAIN 3D CANVAS AREA */}
      <section className="flex-1 relative bg-[#1e1e21]">
        
        {/* 3D Canvas Wrapper */}
        <div className="absolute inset-0 flex items-center justify-center">
          {result?.optimized_web_url ? (
             <ThreeViewer url={result.optimized_web_url} />
          ) : (
            <div className="flex flex-col items-center gap-3 text-zinc-700 opacity-60">
              <Box className="w-16 h-16 mb-2" />
              <p className="font-medium tracking-wide">Awaiting Generation Input</p>
            </div>
          )}
        </div>

        {/* BOTTOM MULTIMODAL COMMAND BAR */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 w-full max-w-2xl z-20">
          
          {/* Image Preview Pop-up */}
          {preview && (
            <div className="mb-3 ml-2 relative inline-block">
              <div className="w-20 h-20 rounded-xl overflow-hidden border-2 border-blue-500/50 shadow-xl shadow-black/50">
                <img src={preview} alt="Upload Preview" className="object-cover w-full h-full" />
              </div>
              <button 
                onClick={removeFile} 
                className="absolute -top-2 -right-2 bg-red-500 text-white p-1 rounded-full hover:bg-red-600 transition-colors shadow-lg"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}

          <div className="flex items-center gap-2 bg-[#121214]/90 backdrop-blur-md border border-zinc-800/80 rounded-2xl p-1.5 shadow-2xl">
            
            {/* Hidden File Input & Upload Button */}
            <input 
              type="file" 
              accept="image/png, image/jpeg, image/webp" 
              className="hidden" 
              ref={fileInputRef}
              onChange={handleFileChange} 
            />
            <button 
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
              className="p-3 text-zinc-400 hover:text-blue-400 hover:bg-blue-500/10 rounded-xl transition-colors disabled:opacity-50"
              title="Upload Image"
            >
              <ImageIcon className="w-5 h-5" />
            </button>

            {/* Text Input */}
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={!!file || loading} // Disable if image is uploaded
              placeholder={file ? "Image attached. Click send to analyze & generate." : "Type a description to generate a 3D asset..."}
              className="flex-1 bg-transparent border-none outline-none text-sm text-zinc-200 px-2 placeholder:text-zinc-600 disabled:opacity-50"
              onKeyDown={(e) => e.key === 'Enter' && generateMesh()}
            />
            
            {/* Send Button */}
            <button 
              onClick={generateMesh}
              disabled={loading || (!prompt && !file)}
              className="bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-500 text-white p-3 rounded-xl transition-colors shadow-lg shadow-blue-900/20"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* TOP RIGHT HELPERS */}
        <div className="absolute top-8 right-8 flex flex-col gap-3 z-10 pointer-events-none">
          <div className="flex items-center gap-2 text-zinc-600 text-xs font-medium bg-zinc-900/30 px-3 py-1.5 rounded-full backdrop-blur-sm border border-zinc-800/50 shadow-sm">
            <MousePointer2 className="w-3.5 h-3.5" />
            <span>Click & Drag to Rotate</span>
          </div>
          <div className="flex items-center gap-2 text-zinc-600 text-xs font-medium bg-zinc-900/30 px-3 py-1.5 rounded-full backdrop-blur-sm border border-zinc-800/50 shadow-sm">
            <MoveVertical className="w-3.5 h-3.5" />
            <span>Scroll to Zoom</span>
          </div>
        </div>
        
      </section>
    </main>
  );
}