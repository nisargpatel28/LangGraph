# Agentic Image Flow (LangGraph style)

This repo contains a minimal, local LangGraph-like SDK and an example agentic
flow that: 1) creates content from a prompt, 2) generates an image from the
content, 3) post-processes that image (resize + watermark), and 4) generates
concise alt text.

Quick start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key in environment:

Windows (PowerShell):

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

Linux / macOS:

```bash
export OPENAI_API_KEY="sk-..."
```

3. Run the flow:

```bash
python run_flow.py --prompt "A vintage poster of a robot baker" --outdir output
```

Outputs will be written into the `output` directory.

Notes
- This is a minimal example to demonstrate an agentic flow. Replace the
  OpenAI calls or extend nodes as needed.
- If you want to swap in a different image-generation provider, modify
  `flows/agentic_image_flow.py` in the `generate_image` node.
# 🏥 Medical Appointment System using LangGraph, FastAPI, and Streamlit

A **multi-agent, AI-powered Doctor Appointment Booking System** designed to handle user queries about doctor availability, specialization, and appointment scheduling.  
This project demonstrates intelligent workflow automation between agents using **LangGraph**, **LangChain**, and a clean **FastAPI–Streamlit** integration.

---

## 🚀 Features
- AI-driven appointment scheduling and doctor recommendations  
- Multi-agent coordination for query handling and decision-making  
- Dynamic workflow automation using **LangGraph**  
- Simple, interactive frontend built with **Streamlit**  
- REST API powered by **FastAPI** for backend execution  
- CSV-based data management with **Python** and **Pandas**

---

## 🧠 Tech Stack

| Technology | Purpose |
|-------------|----------|
| **LangGraph** | Workflow automation between agents |
| **LangChain** | Model loading, prompt creation, and tool usage |
| **FastAPI** | Serves API endpoints and executes logic |
| **Streamlit** | Frontend interface for user interaction |
| **Python + Pandas + CSV** | Data handling and storage |

---

## 🧩 Architecture Overview

1. **User Input** → Streamlit UI  
2. **Query Handling** → LangChain-powered Agent  
3. **Workflow Coordination** → LangGraph automates inter-agent communication  
4. **Backend Execution** → FastAPI processes requests and returns responses  
5. **Data Management** → Pandas reads/writes appointment data via CSV  

---

## 🩺 Example Use Case



---

## ⚙️ How to Run Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/medical-appointment-system.git

# Navigate to the project directory
cd medical-appointment-system

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI backend
uvicorn main:app --reload

# Run the Streamlit frontend
streamlit run app.py
