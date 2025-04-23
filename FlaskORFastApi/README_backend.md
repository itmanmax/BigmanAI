# ZJU Chat API Backend Service README

这个 Flask 应用提供了一个简单的后端服务，作为您的前端应用 (React, Vue, etc.) 与父目录中的 `zju_chat_client` 模块之间的桥梁，用于安全地调用 ZJU Chat API。

## 目的

-   **封装 API 调用:** 将直接与 ZJU Chat API 的交互封装在后端。
-   **保护 API Key:** 避免在前端代码中暴露敏感的 `ZJU_API_KEY`。
-   **提供接口:** 为前端提供一个统一的 HTTP 端点来访问聊天功能。

## 先决条件

-   Python 3.7+
-   pip (Python 包安装器)
-   `zju_chat_client` 库 (位于项目根目录):
    -   **推荐:** 在项目根目录 (`zju_chat_client/`) 运行 `pip install .` 将其安装到您的环境中。
    -   **或者:** 确保项目根目录 (`zju_chat_client/`) 在 Python 的可导入路径中（例如，通过设置 `PYTHONPATH` 环境变量，或者如果您从根目录运行后端应用）。

## 安装依赖

首先，确保您已安装 `zju_chat_client` 库及其依赖 (参考根目录的 `README.md`)。

然后，在此目录 (`FlaskORFastApi/`) 中，运行以下命令安装后端服务所需的库：

```bash
# 建议在虚拟环境中使用 (与 zju_chat_client 使用同一个虚拟环境)
# python -m venv ../venv  # 在父目录创建 venv (如果尚不存在)
# source ../venv/bin/activate  # Linux/macOS
# ..\\venv\\Scripts\\activate    # Windows

# 安装 Flask 相关依赖
pip install -r requirements.txt
```
此目录下的 `requirements.txt` 文件包含:
```
Flask>=2.0
Flask-Cors>=3.0
gunicorn>=20.0 # 可选，用于生产部署
```

## 配置

**最重要的步骤是设置 API Key 环境变量。** 后端服务启动时会读取此变量。

在 Linux/macOS 上:
```bash
export ZJU_API_KEY='您的真实API_KEY'
```

在 Windows (Command Prompt) 上:
```bash
set ZJU_API_KEY=您的真实API_KEY
```

在 Windows (PowerShell) 上:
```powershell
$env:ZJU_API_KEY='您的真实API_KEY'
```

**其他可选环境变量:**

-   `PORT`: 设置服务监听的端口号 (默认为 `5001`)。
    ```bash
    export PORT=8000
    ```
-   `FLASK_DEBUG`: 设置为 `True` 以启用 Flask 的调试模式 (仅限开发环境!)。
    ```bash
    export FLASK_DEBUG=True
    ```

## 运行服务

**重要:** 运行命令需要在**项目根目录** (`zju_chat_client/`) 下执行，或者需要确保 Python 能找到 `zju_chat_client` 模块。

### 开发环境

1.  确保设置了 `ZJU_API_KEY` 环境变量。
2.  确保已安装 `zju_chat_client` 或项目根目录在 `PYTHONPATH` 中。
3.  在**项目根目录** (`zju_chat_client/`) 下运行：
    ```bash
    # 告诉 Python 从当前目录导入 FlaskORFastApi 模块
    python -m FlaskORFastApi.backend_app
    ```
    或者，如果您在 `FlaskORFastApi` 目录中：
    ```bash
    # 确保根目录在 PYTHONPATH
    # export PYTHONPATH="${PYTHONPATH}:.." # Linux/macOS 示例
    # set PYTHONPATH=%PYTHONPATH%;.. # Windows CMD 示例
    python backend_app.py
    ```

服务将在默认端口 `5001` (或您通过 `PORT` 环境变量指定的端口) 上启动。

### 生产环境

在生产环境中，**不应** 使用 Flask 内置的开发服务器 (`app.run`)。推荐使用生产级的 WSGI 服务器，例如 Gunicorn 或 uWSGI。

**使用 Gunicorn (示例):**

1.  安装 Gunicorn:
    ```bash
    pip install gunicorn
    ```
2.  运行:
    ```bash
    # 在项目根目录运行
    # 设置 ZJU_API_KEY 环境变量!
    # -w 4: 使用 4 个 worker 进程 (根据服务器 CPU 核心数调整)
    # -b 0.0.0.0:8000: 绑定到所有接口的 8000 端口
    # FlaskORFastApi.backend_app:app: 指向 FlaskORFastApi 目录内 backend_app.py 文件中的 app 实例
    gunicorn -w 4 -b 0.0.0.0:8000 FlaskORFastApi.backend_app:app
    ```

通常还需要结合 Nginx 或其他反向代理来处理 HTTPS、负载均衡和静态文件服务。

## API 端点

### `POST /api/chat`

这是主要的聊天接口。

**请求 (Request):**

-   **方法:** `POST`
-   **头部 (Headers):** `Content-Type: application/json`
-   **正文 (Body - JSON):**
    ```json
    {
      "user_content": "您想问的问题或输入的文本",
      "model": "deepseek-r1-671b", // 可选，默认为 'deepseek-r1-671b'，参考项目根目录的 README.md 获取更多模型
      "system_content": "You are a helpful assistant.", // 可选的系统提示
      "stream": false // 可选，默认为 false。如果为 true，则启用流式响应
    }
    ```

**响应 (Response):**

1.  **非流式 (`stream: false`):**
    -   **状态码:** `200 OK` (成功)
    -   **正文 (Body - JSON):** 返回与 `ZjuChatClient.get_completion` 相同的 JSON 结构，包含 `choices`、`usage` 等字段。
      ```json
      {
        "id": "chat...",
        "object": "chat.completion",
        "created": 174...,
        "model": "deepseek-r1-671b",
        "choices": [
          {
            "index": 0,
            "message": {
              "role": "assistant",
              "content": "助手的回答内容..."
            },
            "finish_reason": "stop"
          }
        ],
        "usage": {
          "prompt_tokens": ...,
          "completion_tokens": ...,
          "total_tokens": ...
        }
      }
      ```

2.  **流式 (`stream: true`):**
    -   **状态码:** `200 OK`
    -   **头部 (Headers):** `Content-Type: text/event-stream`
    -   **正文 (Body):** Server-Sent Events (SSE) 流。每个事件都是 `data: <json_chunk>\n\n` 的形式，其中 `<json_chunk>` 是 `ZjuChatClient` 流式响应返回的 JSON 块。
      ```
      data: {"id":"chat...","object":"chat.completion.chunk","created":...,"model":"...","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

      data: {"id":"chat...","object":"chat.completion.chunk","created":...,"model":"...","choices":[{"index":0,"delta":{"content":"助手"},"finish_reason":null}]}

      data: {"id":"chat...","object":"chat.completion.chunk","created":...,"model":"...","choices":[{"index":0,"delta":{"content":"的"},"finish_reason":null}]}

      ...

      data: {"id":"chat...","object":"chat.completion.chunk","created":...,"model":"...","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

      ```
      *注意：如果流处理过程中发生错误，可能会在流中发送一个包含 `error` 字段的 JSON 对象。*

**错误响应:**

-   `400 Bad Request`: 请求体不是 JSON 或缺少 `user_content`。
-   `415 Unsupported Media Type`: 请求头 `Content-Type` 不是 `application/json`。
-   `500 Internal Server Error`: 后端发生未预料的错误，或者无法初始化 `ZjuChatClient` (可能是 API Key 未设置)，或者 ZJU API 返回了错误。
-   `503 Service Unavailable`: 后端无法连接到 ZJU Chat API。

## 注意事项

-   **CORS 配置:** `backend_app.py` 中的 CORS 配置 (`origins="*"`) 允许任何来源访问，这在开发中很方便，但在生产环境中**非常不安全**。请务必将其限制为您前端应用的实际部署域名。
-   **安全性:** 确保您的后端服务器环境安全，特别是 `ZJU_API_KEY` 环境变量的保护。
-   **扩展性:** 对于高并发场景，需要考虑使用更健壮的 WSGI 服务器（如 Gunicorn）并调整 worker 数量，可能还需要异步框架（如 FastAPI + Uvicorn）来获得更好的性能。 