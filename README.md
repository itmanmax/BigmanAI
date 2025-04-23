# ZJU Chat API Client 与 后端服务示例

本项目包含两个主要部分：

1.  **`zju_chat_client/`**:
    *   一个 Python 客户端库，用于方便地与浙江大学 `chat.zju.edu.cn` 的 AI 模型 API 进行交互。
    *   它封装了 API 请求、认证和响应处理（包括流式响应）。
    *   包含使用示例 (`examples/`)。
    *   详细信息请参阅 **`zju_chat_client/README.md`**。

2.  **`FlaskORFastApi/`**:
    *   一个基于 Flask 的简单后端 Web 服务示例。
    *   该服务使用 `zju_chat_client` 库，并为前端应用 (如 React, Vue) 提供了一个安全的 `/api/chat` 端点来调用 ZJU Chat API，避免在前端暴露 API Key。
    *   包含运行、配置和部署说明。
    *   详细信息请参阅 **`FlaskORFastApi/README.md`**。

## 快速开始

1.  **客户端库**: 如果您想在自己的 Python 项目中直接使用 API 客户端，请查看 `zju_chat_client/` 目录及其 README。
2.  **后端服务**: 如果您需要一个后端服务来桥接前端应用和 API，请查看 `FlaskORFastApi/` 目录及其 README。

请根据您的需求，查阅对应子目录中的 README 文件获取详细的安装、配置和使用指南。 