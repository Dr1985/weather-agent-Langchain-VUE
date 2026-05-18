# 🌤️ weather-agent-langchain-VUE

基于 **LangChain**、**FastAPI** 和 **Vue 3** 搭建的智能天气查询助手。后端通过大模型驱动的天气 Agent 自动调用工具获取实时数据，前端提供轻量、直观的聊天式交互界面。

> 📘 语言切换说明：如果你想查看英文版文档，请打开 `README_EN.md`。

## 🛠️ 技术栈

- **后端 (Backend)**: Python, FastAPI, LangChain, 阿里云通义千问大模型 (`qwen-max`), Uvicorn
- **前端 (Frontend)**: Vue 3 (Vite 驱动), 原生 Fetch 流式读取

## ✨ 页面效果

- 聊天气泡展示：用户在右、AI 在左
- 流式输出：后端通过 `/api/chat/stream` 逐段返回内容
- 历史对话保留：不会发送一次就清空
- 状态提示：展示“思考中 / 流式输出中”

## 📂 项目结构

```text
weather-agent-langchain-VUE/
├── .venv/               # Python 后端虚拟环境 (已加入 .gitignore)
├── frontend/            # Vue 3 前端工程
│   ├── src/            # 前端源码
│   └── node_modules/    # 前端依赖包 (已加入 .gitignore)
├── .env                 # 敏感隐私配置 (已加入 .gitignore)
├── .gitignore           # Git 忽略规则
├── main.py              # FastAPI 后端核心入口与 Agent 逻辑
└── README.md            # 项目说明文档
```



🚀 快速开始
1. 准备环境与敏感配置
在项目根目录下新建一个 .env 文件，并填入你的阿里云 API Key：

```Plaintext
DASHSCOPE_API_KEY=你的阿里云真实ApiKey
```
2. 启动 Python 后端
进入项目根目录，确保虚拟环境已激活，安装依赖并运行：

```Bash
# 安装 Python 依赖
pip install -r requirements.txt
```
# 启动后端服务 (运行在 [http://127.0.0.1:8000](http://127.0.0.1:8000))
```
python main.py
```
3. 启动 Vue 前端
打开一个新的终端标签页，进入 frontend 目录，安装依赖并启动：
```Bash
# 进入前端目录
cd frontend

# 安装前端依赖
npm install

# 开启本地开发服务器 (运行在 http://localhost:5173)
npm run dev
```
如果后端地址不是 `http://127.0.0.1:8000`，可以在前端启动时设置 `VITE_API_BASE_URL`。
打开浏览器访问终端输出的本地链接（通常为 http://localhost:5173），即可开始与天气智能体交互！

💡 核心特性
工具调用 (Tool Calling): 智能体能够自主判断用户意图，当遇到天气查询时自动触发内置的 get_current_weather 函数。

前后端分离: 前端 Vue 3 通过 Fetch 流式调取 FastAPI 提供的 /api/chat/stream 接口，解耦彻底。

安全隔离: 敏感的 API 密钥及庞大的依赖库已完美配置在 .gitignore 中，确保代码提交安全。