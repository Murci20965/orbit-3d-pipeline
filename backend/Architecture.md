# **Orbit-3D Architecture & Technical Explanation**

This document serves as the technical explanation for the Orbit-3D prototype, outlining the system design, challenges solved, and future scalability for NexEra's human training modules.

## **1\. What Was Built**

Orbit-3D is a highly modular, decoupled Monorepo consisting of:

* A Next.js 15 Frontend featuring a multimodal drag-and-drop UI and an interactive WebGL 3D Viewer.  
* A Dockerized FastAPI Backend that acts as an orchestration engine, asynchronously managing AI mesh generation, Headless Blender optimization, and Llama-vision contextualization.

## **2\. Architecture and AI Logic**

 graph TD
    %% Define Styles
    classDef frontend fill:#09090b,stroke:#3b82f6,stroke-width:2px,color:#fff
    classDef backend fill:#09090b,stroke:#10b981,stroke-width:2px,color:#fff
    classDef external fill:#09090b,stroke:#f59e0b,stroke-width:2px,color:#fff
    classDef storage fill:#09090b,stroke:#8b5cf6,stroke-width:2px,color:#fff

    %% Nodes
    User((User))
    UI["Orbit-UI<br/>(Next.js 15 / R3F)"]:::frontend
    API["Orbit-Engine<br/>(FastAPI)"]:::backend
    Groq["Groq API<br/>(Llama-4-Scout / Llama-3.3)"]:::external
    Tripo["Tripo3D API<br/>(v3.1)"]:::external
    Blender["Headless Blender 4.0<br/>(Docker Subprocess)"]:::backend
    TempStore[("Temp Volume<br/>(/temp)")]:::storage

    %% Flow
    User -- "Text Prompt or Image Upload" --> UI
    UI -- "Multipart Form Data" --> API
    
    API -- "Concurrent Task 1:<br/>Vision/Text Prompt" --> Groq
    API -- "Concurrent Task 2:<br/>Image/Text to 3D" --> Tripo
    
    Groq -. "Educational Context" .-> API
    Tripo -. "Raw Mesh URL" .-> API
    
    API -- "Downloads Raw .glb" --> TempStore
    API -- "Triggers bpy Script" --> Blender
    
    Blender -- "Reads Raw Mesh" --> TempStore
    Blender -- "Centers, Scales, <br/>Draco Compresses" --> TempStore
    
    API -- "Returns JSON + Web URL" --> UI
    UI -- "Renders 3D Canvas" --> User

## The pipeline follows a strict, asynchronous data flow:

1. **The Ingestion Layer:** The user submits a text prompt or uploads a physical .jpg/.png via multipart/form-data in the Next.js UI.  
2. **Concurrent AI Processing:**  
   * **Tripo3D (Generation):** If an image is uploaded, the backend securely uploads it to Tripo's servers to receive an image\_token, then initiates the v3.1 generation sequence. If text, it initiates a text-to-model sequence.  
   * **Groq (Contextualization):** Simultaneously, the input is routed to Groq. Uploaded images are Base64-encoded and passed to meta-llama/llama-4-scout-17b-16e-instruct to visually identify the object. Text prompts are passed to llama-3.3-70b-versatile.  
3. **The Optimization Layer (Headless Blender):** Raw AI meshes are downloaded to a secure temp/ volume. A subprocess triggers a Python (bpy) script inside a Headless Blender instance. The script clears default scenes, centers the geometry bounds, scales the asset to 1 unit (perfect for WebGL), and exports it with Google Draco compression.  
4. **The Presentation Layer:** Next.js dynamically imports the 3D Canvas (bypassing SSR) and renders the Draco-compressed .glb using Image-Based Lighting (IBL) and Contact Shadows to ensure high performance on all hardware.

## **3\. Challenges & Engineering Solutions**

* **The WebGL SSR Conflict:** Next.js Server-Side Rendering (SSR) attempts to render components in a Node.js environment lacking the window object, which crashes Three.js. **Solution:** Implemented explicit Named Exports and dynamic imports (next/dynamic) with ssr: false to force client-side execution.  
* **The OS-Level Blender Dependency:** Running Blender's bpy module directly on local machines causes severe library conflicts (libgl1, libxrender1). **Solution:** Containerized the entire backend using Docker, utilizing a Debian-slim base image to guarantee the 3D pipeline runs identically on local Windows, macOS, and Render cloud servers.  
* **GPU Resource Management:** Utilizing heavy cinematic shadow mapping (\<Stage\>) in React Three Fiber caused WebGL Shader Errors (1282) on lower-end hardware. **Solution:** Transitioned to an optimized "Cinematic Performance Mode" using environment maps and fake contact shadows.

## **4\. Scalability within NexEra**

To transition this prototype into a core NexEra feature handling thousands of simultaneous educators:

* **Event-Driven Architecture:** Move from HTTP polling to WebSockets for real-time progress bars in the UI.  
* **Decoupled Task Queues:** Separate the FastAPI router from the Blender optimization layer using Celery and Redis. This allows a fleet of auto-scaling worker nodes to handle heavy 3D math without blocking the API.  
* **Global Caching:** Implement an AWS S3 \+ CloudFront CDN layer. If an educator requests a "Hard Hat," the system checks the CDN first, bypassing AI generation costs and delivering the optimized asset in under 100ms.
