import os
from typing import Any

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

# 1. 加载环境变量 (.env)
load_dotenv()

# 2. 初始化 FastAPI 应用
app = FastAPI(title="Weather Agent API")

# 配置跨域（CORS），允许你本地的 Vue 前端（通常在5173端口）访问这个 Python 后端
app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]
    allow_origins=["*"],  # 本地开发允许所有源，上线时再限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. 定义一个给大模型使用的“查天气工具”
@tool
def get_current_weather(city: str) -> str:
    """当你需要查询某个城市实时天气时，调用此工具。输入参数 city 必须是城市名称（如：北京、上海）。"""
    try:
        # 这里使用一个免 API Key 的开源天气服务作为演示 (wttr.in)
        # 如果你未来有高频、高精度需求，可以换成和风天气或高德天气的 API
        url = f"https://wttr.in/{city}?format=%C+%t+湿度:%h+风向:%w"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return f"{city}的当前天气是：{response.text}"
        return f"暂时无法获取{city}的天气情况。"
    except Exception as e:
        return f"查询天气时发生错误: {str(e)}"


# 4. 初始化 LangChain 智能体 (Agent)
# 使用阿里云通义千问的 OpenAI 兼容模式
llm = ChatOpenAI(
    model="qwen-turbo",  # qwen3.5-flash
    api_key=lambda: os.getenv("DASHSCOPE_API_KEY") or "",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0,
)

# 将我们写好的天气工具绑定给大模型
tools = [get_current_weather]

# 创建智能体图（LangChain 1.3.x 新接口）
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个非常友善的天气播报助手。你必须使用工具来获取实时的天气信息。回答时要亲切、简练。",
    debug=True,
)


# 5. 定义前端发来的数据格式
class ChatMessage(BaseModel):
    message: str


def _extract_reply(result: dict[str, Any]) -> str:
    messages = result.get("messages", [])
    if not messages:
        return "没有收到有效回复。"

    last_message = messages[-1]
    content = getattr(last_message, "content", None)
    if isinstance(content, str) and content.strip():
        return content
    if isinstance(content, list):
        text_parts = [str(item.get("text", "")) for item in content if isinstance(item, dict)]
        joined = "".join(text_parts).strip()
        if joined:
            return joined
    return str(content) if content is not None else "没有收到有效回复。"


def _extract_stream_text(chunk: Any) -> str:
    if chunk is None:
        return ""

    if isinstance(chunk, tuple) and chunk:
        chunk = chunk[0]

    content = getattr(chunk, "content", None)
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                for key in ("text", "content", "token"):
                    value = item.get(key)
                    if isinstance(value, str):
                        parts.append(value)
                        break
        return "".join(parts)

    if isinstance(chunk, dict):
        for key in ("content", "text", "token", "output"):
            value = chunk.get(key)
            if isinstance(value, str):
                return value
            if isinstance(value, list):
                nested = []
                for item in value:
                    if isinstance(item, str):
                        nested.append(item)
                    elif isinstance(item, dict):
                        nested.extend(
                            str(item.get(key_name, ""))
                            for key_name in ("text", "content", "token")
                            if isinstance(item.get(key_name), str)
                        )
                if nested:
                    return "".join(nested)

    return ""


# 6. 编写聊天数据接口
@app.post("/api/chat")
async def chat_with_agent(data: ChatMessage):
    # 接收前端传来的用户提问
    user_input = data.message

    if not user_input.strip():
        raise HTTPException(status_code=400, detail="message 不能为空")

    if not os.getenv("DASHSCOPE_API_KEY"):
        raise HTTPException(status_code=500, detail="未配置 DASHSCOPE_API_KEY")

    # 让智能体思考并执行
    response = agent.invoke({"messages": [{"role": "user", "content": user_input}]})

    # 将智能体最终的回答返回给 Vue 前端
    return {"reply": _extract_reply(response)}


@app.post("/api/chat/stream")
async def chat_with_agent_stream(data: ChatMessage):
    user_input = data.message

    if not user_input.strip():
        raise HTTPException(status_code=400, detail="message 不能为空")

    if not os.getenv("DASHSCOPE_API_KEY"):
        raise HTTPException(status_code=500, detail="未配置 DASHSCOPE_API_KEY")

    def event_stream():
        try:
            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                stream_mode="messages",
            ):
                text = _extract_stream_text(chunk)
                if text:
                    yield text
        except Exception as e:
            yield f"\n[ERROR] 查询天气时发生错误: {str(e)}"

    return StreamingResponse(event_stream(), media_type="text/plain; charset=utf-8")


# 7. 本地测试运行入口
if __name__ == "__main__":
    import uvicorn

    # 启动本地服务器，运行在 8000 端口
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)