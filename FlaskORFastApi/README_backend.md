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
python-dotenv>=0.19 # 用于加载 .env 文件
gunicorn>=20.0 # 可选，用于生产部署
```

## 配置

后端服务通过环境变量进行配置。推荐的方式是使用此目录下的 `.env` 文件。

1.  **创建 `.env` 文件:** 在 `FlaskORFastApi/` 目录下创建一个名为 `.env` 的文本文件。
2.  **编辑 `.env` 文件:** 添加以下配置项（将值替换为您自己的）：

    ```dotenv
    # .env 文件示例

    # 必需：您的 ZJU API Key
    # ZjuChatClient 会优先使用此值，而不是系统环境变量
    ZJU_API_KEY="您的有效ZJU_API_KEY"

    # 可选：设置后端服务使用的默认模型名称
    # 如果前端请求中未指定模型，将使用此模型
    DEFAULT_MODEL="deepseek-r1-671b"

    # 可选：Flask 相关配置 (如果需要覆盖默认值)
    # PORT=5001
    # FLASK_DEBUG=False # 生产环境应为 False
    ```

当 `backend_app.py` 启动时，它会自动加载 `.env` 文件中的变量。这意味着您**不需要**手动设置同名的系统环境变量（如 `export ZJU_API_KEY=...`），`.env` 文件中的值将优先被使用。

**注意:** `.env` 文件通常包含敏感信息 (API Key)，请**不要**将其提交到 Git 等版本控制系统中。建议将 `.env` 添加到您的 `.gitignore` 文件中。

**传统环境变量 (仍然可用):**

如果您不使用 `.env` 文件，或者 `.env` 文件中缺少某个变量，应用仍然会尝试读取系统的环境变量，例如：

-   `ZJU_API_KEY`: (必需) 如果 `.env` 中未设置，则必须在系统环境中设置。
-   `DEFAULT_MODEL`: (可选) 如果 `.env` 中未设置，则使用代码中的硬编码默认值。
-   `PORT`: (可选) 默认 `5001`。
-   `FLASK_DEBUG`: (可选) 默认 `False`。

## 运行服务

**重要:** 运行命令需要在**项目根目录** (`zju_chat_client/`) 下执行，或者需要确保 Python 能找到 `zju_chat_client` 模块。

### 开发环境

1.  确保在此目录 (`FlaskORFastApi/`) 中创建并配置了 `.env` 文件（包含 `ZJU_API_KEY`）。
2.  确保已安装 `zju_chat_client` 库（例如，在项目根目录运行 `pip install .`）。
3.  确保已在此目录 (`FlaskORFastApi/`) 安装了 Flask 依赖 (`pip install -r requirements.txt`)。
4.  在**项目根目录** (`zju_chat_client/` 的父目录) 下运行：
    ```bash
    # 在项目根目录运行
    # 确保 .env 文件存在于 FlaskORFastApi/ 目录中
    # Gunicorn 通常不会自动加载 .env，因此需要确保 ZJU_API_KEY 等变量已导出为系统环境变量，
    # 或者使用 Gunicorn 的 --env 选项，或者在启动脚本中加载 .env
    # 例如，在启动脚本中:
    # export $(cat FlaskORFastApi/.env | xargs)
    # gunicorn -w 4 -b 0.0.0.0:8000 FlaskORFastApi.backend_app:app

    # 或者直接设置环境变量:
    # export ZJU_API_KEY=$(grep ZJU_API_KEY FlaskORFastApi/.env | cut -d '=' -f2-)
    # export DEFAULT_MODEL=$(grep DEFAULT_MODEL FlaskORFastApi/.env | cut -d '=' -f2-)
    gunicorn -w 4 -b 0.0.0.0:8000 FlaskORFastApi.backend_app:app
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