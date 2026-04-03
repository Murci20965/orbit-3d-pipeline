"use client";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, ContactShadows, Gltf } from "@react-three/drei";
import { Suspense } from "react";

export function ThreeViewer({ url }: { url: string }) {
  return (
    <div className="w-full h-full min-h-[400px] bg-zinc-900/50 rounded-2xl overflow-hidden border border-zinc-800 shadow-2xl relative cursor-grab active:cursor-grabbing">
      <Canvas camera={{ position: [0, 2, 5], fov: 45 }}>
        <Suspense fallback={null}>
          
          {/* 1. CINEMATIC LIGHTING: Uses a pre-baked HDRI map (city) for photorealistic reflections */}
          <Environment preset="city" />
          <ambientLight intensity={0.5} />
          
          {/* 2. THE MESH */}
          <Gltf src={url} />

          <ContactShadows 
            position={[0, -1, 0]} 
            opacity={0.7} 
            scale={10} 
            blur={2} 
            far={4} 
            color="#000000" 
          />
        </Suspense>
        
        <OrbitControls autoRotate autoRotateSpeed={1.5} makeDefault />
      </Canvas>
    </div>
  );
}