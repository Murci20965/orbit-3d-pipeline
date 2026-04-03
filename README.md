# **ORBIT-3D: Multimodal AI Asset Pipeline**

This repository contains the **Orbit-3D Pipeline**, aA prototype developed for the NexEra AI Engineer assessment (Test 1). It bridges the gap between raw generative AI and optimized, interactive 3D learning environments.

## **🚀 Project Overview**

**Orbit-3D** is a fully automated "Text/Image-to-Optimized-Mesh" engine. It solves the three primary pain points of AI-generated 3D content for web platforms:

1. **Multimodal Generation:** Generates raw meshes from text prompts or physical image uploads via the Tripo3D API (v3.1-2026).
2. **Headless Optimization:** Programmatically centers, scales, and applies Draco compression using a Headless Blender Python script running in a Dockerized environment.
3. **Vision Contextualization:** Uses Groq's Llama-4-Scout Vision Model and Llama-3.3-70B to physically analyze inputs and return educational facts.

## **🏗️ Tech Stack**

### **Frontend (Orbit-UI)**
* **Framework:** Next.js 15 (App Router, Turbopack) + TypeScript
* **3D Engine:** React Three Fiber (`@react-three/fiber`), `@react-three/drei`, Three.js
* **Styling:** Tailwind CSS, Lucide React
* **Hosting:** Vercel

### **Backend (Orbit-Engine)**
* **API Framework:** FastAPI (Asynchronous Python), `python-multipart`
* **3D Processing:** Headless Blender 4.0 (via `bpy` and `subprocess`)
* **Environment:** Docker (Debian Linux base with required C++ GL libraries)
* **AI Routing:** Groq (Llama-4-Scout-17b / Llama-3.3-70b) & Tripo3D
* **Hosting:** Render.com (Web Service via Docker)

## **⚙️ Setup Instructions**

### **1. Orbit-Engine (Backend)**
Requires Docker to ensure Blender libraries run correctly.
```bash
cd backend
# Create a .env file with TRIPO_API_KEY and GROQ_API_KEY
docker build -t orbit-engine .
docker run -p 8000:8000 --env-file .env -v "${PWD}:/app" orbit-engine