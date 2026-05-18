# 🌤️ weather-agent-langchain-VUE

A weather query assistant built with **LangChain**, **FastAPI**, and **Vue 3**. The backend uses a tool-calling agent powered by a large language model to fetch real-time weather data, while the frontend provides a lightweight and intuitive chat-style interface with streaming responses.

> 📘 Language switch note: If you prefer the Chinese version of this documentation, open `README.md`.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, LangChain, Alibaba Cloud Qwen model (`qwen3.5-flash`), Uvicorn
- **Frontend**: Vue 3 (powered by Vite), native Fetch streaming

## ✨ Features

- Chat bubble UI: user messages on the right, AI messages on the left
- Streaming output: the backend returns responses incrementally through `/api/chat/stream`
- Conversation history: previous messages stay on the page
- Status indicator: shows states like “thinking” and “streaming”
- Quick prompts: one-click sample questions to get started faster

## 📂 Project Structure

```text
weather-agent-langchain-VUE/
├── .venv/               # Python backend virtual environment (ignored by Git)
├── frontend/            # Vue 3 frontend project
│   ├── src/             # Frontend source code
│   └── node_modules/    # Frontend dependencies (ignored by Git)
├── .env                 # Sensitive configuration (ignored by Git)
├── .gitignore           # Git ignore rules
├── main.py              # FastAPI backend entry point and Agent logic
├── README.md            # Chinese project documentation
└── README_EN.md         # English project documentation
```

## 🚀 Quick Start

### 1. Prepare environment variables

Create a `.env` file in the project root and add your Alibaba Cloud API key:

```text
DASHSCOPE_API_KEY=your_real_alibaba_cloud_api_key
```

### 2. Start the Python backend

From the project root, make sure your virtual environment is activated, install the dependencies, and run the backend:

```bash
pip install -r requirements.txt
python main.py
```

The backend will run at:

```text
http://127.0.0.1:8000
```

### 3. Start the Vue frontend

Open a new terminal, enter the `frontend` directory, install dependencies, and start the development server:

```bash
cd frontend
npm install
npm run dev
```

The frontend will usually run at:

```text
http://localhost:5173
```

If your backend is not available at `http://127.0.0.1:8000`, set `VITE_API_BASE_URL` before starting the frontend.

## 💡 Core Highlights

- **Tool Calling**: The agent can decide when to call the built-in `get_current_weather` tool based on user intent.
- **Frontend-Backend Separation**: The Vue 3 frontend communicates with the FastAPI backend through the streaming `/api/chat/stream` endpoint.
- **Security**: Sensitive API keys and dependency folders are excluded through `.gitignore`.

## 📝 Notes

- This project is intended for development and demo purposes.
- The backend model can be adjusted in `main.py` if you want to switch to a cheaper or faster Qwen model.
- The English README intentionally mirrors the Chinese README so both versions stay aligned.

