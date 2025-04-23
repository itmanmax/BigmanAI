# ZJU Chat API Client

一个用于与浙江大学 chat.zju.edu.cn API 交互的 Python 客户端库。

## 可用模型 (截至信息更新时)

API 支持多种模型，适用于不同的任务场景：

| 模型名称                    | 类型         | 描述                                                                                                                     | 备注        |
| --------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------ | ----------- |
| `deepseek-r1-distill-qwen`  | 本地文本生成 | 基于Qwen2.5-32B的蒸馏大型语言模型                                                                                      | 限时免费    |
| `deepseek-r1-671b`          | 云端文本生成 | 拥有6710亿参数的混合专家（MoE）大模型，支持高精度推理与多任务处理                                                        | 限时免费    |
| `deepseek-v3-671b`          | 云端文本生成 | 拥有671B 参数的混合专家（MoE）大语言模型，推理时激活37B 亿参数，显著提升了理解与生成能力                                    | 限时免费    |
| `qwen2.5-instruct`          | 本地文本生成 | 通义千问研发，在长文本生成、结构化数据处理和多语言支持上具有优势                                                         | 限时免费    |
| `bge-m3`                    | 本地嵌入模型 | 智源开源的多语言多模态向量模型，支持百种语言与跨模态检索                                                                 | 限时免费    |
| `bge-reranker-v2-m3`        | 本地Reranker | 智源研究院推出的高效重排模型，支持8192 tokens长文本，适用于中英文RAG场景                                                   | 限时免费    |
| `llava-onevision-qwen2-7b-ov` | 本地多模态   | 基于Qwen2开发的多模态模型，通过LLaVA-OneVision数据集训练，可理解图像、视频内容                                            | 限时免费    |
| `QwQ-32B`                   | 云端文本模型 | 通过大规模强化学习，在数学推理和代码生成等场景表现卓越，部署成本低                                                       | 限时免费    |

*注意：模型列表和可用性可能会变化，请以官方信息为准。*

## 功能

-   封装了对 `/chat/completions` 端点的调用。
-   支持普通响应和流式响应。
-   通过环境变量或直接参数配置 API Key。
-   基本的错误处理。
-   使用 `requests.Session` 进行连接复用。

## 安装

1.  **克隆或下载此仓库:**
    ```bash
    # git clone <your-repo-url> # 如果这是一个 git 仓库
    cd zju_chat_client
    ```

2.  **安装依赖:**
    建议在虚拟环境中使用：
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate  # Windows
    pip install -r requirements.txt
    ```
    或者，如果您想将此客户端作为依赖项安装到您的其他项目中（这样可以在任何地方导入 `zju_chat_client`）：
    ```bash
    pip install .
    ```

## 使用方法

### 1. 设置 API Key

**强烈建议** 使用环境变量 `ZJU_API_KEY` 来存储您的 API Key。您可以从以下地址获取或查看您的 API Key:

[https://chat.zju.edu.cn/model-service-apikey?name=%E8%B0%83%E7%94%A8%E7%AE%A1%E7%90%86&hideRight=true&iframeSrc=https://chat.zju.edu.cn/model-square/%23/call-management](https://chat.zju.edu.cn/model-service-apikey?name=%E8%B0%83%E7%94%A8%E7%AE%A1%E7%90%86&hideRight=true&iframeSrc=https://chat.zju.edu.cn/model-square/%23/call-management)

在 Linux/macOS 上:
```bash
export ZJU_API_KEY='您的API_KEY'
```

在 Windows (Command Prompt) 上:
```bash
set ZJU_API_KEY=您的API_KEY
```

在 Windows (PowerShell) 上:
```powershell
$env:ZJU_API_KEY='您的API_KEY'
```

或者，您可以在创建 `ZjuChatClient` 实例时直接传递 `api_key` 参数，但这不够安全，不推荐用于生产环境。

### 2. 编写代码

```python
from zju_chat_client import ZjuChatClient
import os

# 模型名称
model = "deepseek-r1-671b" # 替换为实际模型
# 用户问题
prompt = "杭州今天天气怎么样？"

# 检查 API Key 是否已设置（推荐方式）
if not os.getenv("ZJU_API_KEY"):
    print("错误：请先设置 ZJU_API_KEY 环境变量。")
    # exit() # 或者抛出异常

# --- 非流式调用 ---
try:
    # 使用 'with' 语句确保资源被释放
    # 客户端将自动从环境变量读取 API Key (如果未在参数中提供)
    with ZjuChatClient() as client:
        response = client.get_completion(model=model, user_content=prompt, stream=False)
        print("--- 非流式响应 ---")
        # print(response) # 打印完整响应字典

        # 提取内容
        if response and 'choices' in response and response['choices']:
            content = response['choices'][0].get('message', {}).get('content')
            print("助手回答:", content)
            print("Token 使用:", response.get('usage'))
        else:
            print("无法解析响应。")

except Exception as e:
    print(f"非流式调用发生错误: {e}")


# --- 流式调用 ---
print("\n--- 流式调用 ---")
try:
    with ZjuChatClient() as client:
        stream = client.get_completion(model=model, user_content=prompt, stream=True)
        print("助手回答 (流式):")
        full_content = ""
        for chunk in stream:
             # print(chunk) # 打印原始数据块
             if chunk and 'choices' in chunk and chunk['choices']:
                delta_content = chunk['choices'][0].get('delta', {}).get('content')
                if delta_content:
                    print(delta_content, end='', flush=True)
                    full_content += delta_content
        print() # 结束换行
        # print("\n完整流式内容:", full_content)

except Exception as e:
    print(f"流式调用发生错误: {e}")


## 后端服务示例 (Flask)

为了方便将此客户端集成到 Web 应用中（例如 React, Vue），本项目在 `FlaskORFastApi/` 目录下提供了一个简单的 Flask 后端服务示例。

该服务封装了 `zju_chat_client` 的调用，并提供了一个 `/api/chat` 端点供前端安全调用，避免在前端暴露 API Key。

**请参考 `FlaskORFastApi/README.md` 获取详细的设置、运行和部署说明。**

### 3. 运行示例

确保您已设置 `ZJU_API_KEY` 环境变量。然后导航到 `examples` 目录并运行示例脚本：

```bash
cd examples
python usage_example.py
```
如果您将 `zju_chat_client` 安装为包 (`pip install .`)，则可以直接在项目根目录或其他地方运行包含上述使用代码的 Python 脚本。

## 注意事项

-   **流式处理:** `_handle_stream_response` 方法假设响应流是标准的 Server-Sent Events (SSE) 格式，以 `data: ` 开头，并以 `data: [DONE]` 结束。如果实际格式不同，您需要相应地修改解析逻辑。
-   **错误处理:** 当前的错误处理会打印错误并可能重新引发异常。您可以根据需要调整它，例如添加重试逻辑、更详细的日志记录等。
-   **模型名称:** 请确保使用您有权访问的正确模型名称。
-   **依赖管理:** 示例代码包含临时修改 `sys.path` 的部分，以便在不安装包的情况下直接从 `examples` 目录运行。如果您将 `zju_chat_client` 安装为包，则不需要这些 `sys.path` 的修改。 