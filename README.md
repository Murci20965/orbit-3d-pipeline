# **ORBIT-3D: Automated AI Asset Pipeline**

This repository contains **Orbit-3D**, a high-performance interactive prototype developed for the NexEra AI Engineer assessment (Test 1). It successfully bridges the gap between raw generative AI and optimized, interactive 3D learning environments.

**Technical Deep Dive:** For a comprehensive explanation of the architecture, AI logic, engineering challenges, and scaling plans, please see [**backend/Architecture.md**](backend/Architecture.md).

## **🚀 Project Overview & Assessment Delivery**

**Orbit-3D** acts as a fully automated "Text/Image-to-Optimized-Mesh" engine. It solves the critical pipeline challenge of generating raw AI 3D content, mathematically optimizing it for web delivery without manual artist intervention, and providing educational context.

### **What the user does:**

* Learner types an unstructured prompt (e.g., *"A vintage brass telescope"*) OR uploads a physical .jpg/.png image of an object.  
* Uses mouse/touch to orbit, zoom, and inspect the optimized 3D asset in real-time.

### **What the system does:**

1. **Concurrent AI Processing:** The backend routes the request simultaneously to Tripo3D (for mesh generation) and Groq (for contextualization) using asyncio.gather for maximum speed.  
2. **Vision Analysis:** a vision model on Groq (`qwen/qwen3.8-27b`) physically "looks" at the uploaded image to deduce what it is and generates a historical/scientific fact. Text prompts use `openai/gpt-oss-20b`. (The prototype shipped on Llama 4 Scout and Llama 3.3 70B, both retired by Groq in 2026.)  
3. **Headless Optimization:** A Dockerized Headless Blender script intercepts the raw AI mesh, centers its geometry at the origin (0, 0, 0) and scales its largest dimension to exactly 1 unit, so it fits the WebGL camera viewport, then exports it as a Draco-compressed .glb.  
4. **Execution:** The React Three Fiber frontend dynamically imports the optimized .glb file using a highly performant Image-Based Lighting (IBL) and Contact Shadow setup.  
5. **Contextualization:** The UI displays the AI-generated educational rationale alongside the 3D model.

## **🏗️ Tech Stack**

### **Frontend (Orbit-UI)**

* **Framework:** Next.js 16.2 (App Router, Turbopack, React 19) + TypeScript  
* **3D Engine:** React Three Fiber (@react-three/fiber), @react-three/drei, Three.js  
* **Lighting:** Cinematic Performance Mode (HDRI Environment Mapping + Fake Contact Shadows)  
* **Styling:** Tailwind CSS v4, Lucide React (Icons)

### **Backend (Orbit-Engine)**

* **Framework:** FastAPI (Asynchronous Python), Pydantic v2, python-multipart  
* **3D Processing:** Headless Blender 4.0.2 (via bpy and subprocess)  
* **AI Engine:** Groq API (Qwen 3.8 27B vision / gpt-oss-20b) & Tripo3D API (v3.1)  
* **Containerization:** Docker (python:3.11-slim base with the Debian C++ GL libraries Blender needs)
* **Hosting:** Hugging Face Spaces (backend, Docker SDK) and Vercel (frontend)

## **⚙️ Setup & Execution Instructions**

To maintain a strict Separation of Concerns, the API and the UI must be run concurrently.

### **1. The Backend (Orbit-Engine)**

1. Navigate to the backend directory: cd backend  
2. Create a .env file and add your AI keys:  
   TRIPO_API_KEY=your_tripo_key_here  
   GROQ_API_KEY=your_groq_key_here

3. **Run via Docker** (Mandatory for Blender OS Dependencies):  
   docker build -t orbit-engine .  
   docker run -p 7860:7860 -v "${PWD}:/app" --name orbit-director orbit-engine

4. **Health Check:** Visit http://localhost:7860/

### **2. The Frontend (Orbit-UI)**

1. Navigate to the frontend directory: cd frontend  
2. Create a .env.local file and link the API: NEXT_PUBLIC_ENGINE_URL=http://localhost:7860  
3. Install dependencies and run Turbopack:  
   npm install    
   npm run dev

4. **Application:** Visit http://localhost:3000

## **🛡️ Limits**

Each generation spends Tripo3D and Groq credits and runs Blender for minutes, so `/generate` is
capped in-process (`backend/app/api/routes.py`, `backend/app/core/rate_limit.py`):
**2 generations at a time**, **30 per hour in total**, and **5 per hour per client** (best effort,
keyed on the proxy-appended address). Over a limit the API answers `429` and the UI says the
engine is busy. CORS admits only the live UI and `http://localhost:3000`; CORS stops other
websites' browsers, not scripts, which is why the caps exist.

**Tests:** `cd backend && pip install -r requirements.txt pytest httpx && python -m pytest tests`
(generation is stubbed, so no credits are used).

## **🚧 Limitations & Next Steps**

* **Synchronous HTTP Timeouts:** High-fidelity 3D generation can take 2-3 minutes, which breaks standard Cloud Load Balancer limits (e.g., Render's 100s timeout).  
  * *Next Step:* Implement decoupled Task Queues (Celery/Redis) to process Blender tasks in the background, and use WebSockets to stream real-time progress bars to the UI.  
* **Repetitive Generation Costs:** Currently, every request burns API credits, even if an object was generated before.  
  * *Next Step:* Implement a Global CDN Caching layer (AWS S3). If a user requests a "Green Apple", the system pulls the pre-optimized .glb from the cache in <100ms.