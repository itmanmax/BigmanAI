# backend_app.py
import os
from flask import Flask, request, jsonify, Response # 安装 Flask: pip install Flask
from flask_cors import CORS # 安装 CORS: pip install Flask-Cors
from dotenv import load_dotenv # 导入 load_dotenv
# 确保 zju_chat_client 在 Python 路径中，或者将其安装为包 (pip install .)
from zju_chat_client import ZjuChatClient
import json
import logging
import requests # Import requests for exception handling

# 在应用启动时加载 .env 文件
# 这会将 .env 文件中的变量加载到 os.environ 中
# 如果 .env 文件和系统环境变量中都存在同名变量，默认情况下 .env 的值会覆盖系统变量
load_dotenv()

app = Flask(__name__)

# --- 配置 CORS ---
# 生产环境建议更精确地指定允许的来源
# 例如: origins = ["http://your-frontend-domain.com", "https://your-frontend-domain.com"]
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}) # 允许所有来源访问 /api/*

# --- 日志配置 ---
logging.basicConfig(level=logging.INFO)

# --- 全局 ZjuChatClient 实例 (可选，考虑线程安全和配置更新) ---
# 在生产环境中，更推荐在请求上下文或应用上下文中管理客户端实例
# 以确保配置（如API Key）能够动态加载且线程安全。
# 这里为了简单起见，暂时不在全局初始化。
# try:
#     # 确保 ZJU_API_KEY 环境变量在后端服务器上设置好了
#     zju_client = ZjuChatClient()
# except ValueError as e:
#     app.logger.error(f"Failed to initialize ZjuChatClient at startup: {e}")
#     zju_client = None # 或者让应用在启动时失败

@app.route('/api/chat', methods=['POST'])
def chat_handler():
    """处理来自前端的聊天请求。"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.json
    user_content = data.get('user_content')
    # 从环境变量读取默认模型，如果未设置则使用硬编码的默认值
    default_model = os.getenv('DEFAULT_MODEL', 'deepseek-r1-671b')
    model = data.get('model', default_model) # 使用 .env 或系统变量中的默认模型
    stream = data.get('stream', False)
    system_content = data.get('system_content') # 可选的系统提示

    if not user_content:
        return jsonify({"error": "Missing 'user_content' in request body"}), 400

    # 在请求处理函数内部创建客户端实例，确保获取最新的环境变量
    try:
        client = ZjuChatClient() # 读取 ZJU_API_KEY 环境变量
    except ValueError as e:
        app.logger.error(f"Failed to initialize ZjuChatClient: {e}")
        return jsonify({"error": f"Backend configuration error: {e}"}), 500

    try:
        if stream:
            # --- 处理流式响应 --- 
            def event_stream():
                app.logger.info(f"Starting stream for model {model}")
                message_count = 0
                try:
                    for chunk in client.get_completion(model=model, user_content=user_content, system_content=system_content, stream=True):
                        # SSE 格式: data: {...}\n\n
                        if chunk: # 确保 chunk 不为空
                            message_count += 1
                            yield f"data: {json.dumps(chunk)}\n\n"
                        else:
                             app.logger.warning("Received an empty chunk from stream")
                    app.logger.info(f"Stream finished. Sent {message_count} messages.")
                    # 可以选择发送一个结束信号，如果前端需要明确知道流结束
                    # yield f"data: {json.dumps({'event': 'stream_end'})}\n\n"
                except Exception as e:
                    app.logger.error(f"Error during streaming: {e}", exc_info=True)
                    # 在流中发送错误信号给前端
                    error_payload = {"error": f"Error during streaming: {e}"}
                    yield f"data: {json.dumps(error_payload)}\n\n"
                finally:
                    client.close() # 确保关闭会话
                    app.logger.info("Stream client session closed.")

            return Response(event_stream(), mimetype='text/event-stream')
        else:
            # --- 处理非流式响应 ---
            app.logger.info(f"Sending non-stream request for model {model}")
            response_data = client.get_completion(model=model, user_content=user_content, system_content=system_content, stream=False)
            client.close() # 关闭会话
            app.logger.info("Non-stream request successful.")
            return jsonify(response_data)

    except ValueError as e:
        # 通常是 API 返回的错误信息被 ZjuChatClient 包装成了 ValueError
        app.logger.error(f"API Error: {e}")
        # 将 API 返回的错误信息传递给前端可能更友好
        return jsonify({"error": f"API Error: {e}"}), 500
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Network Error communicating with ZJU API: {e}")
        return jsonify({"error": f"Network error communicating with upstream API: {e}"}), 503 # Service Unavailable
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected internal server error occurred."}), 500

if __name__ == '__main__':
    # 获取端口号，允许通过环境变量配置，默认为 5001
    port = int(os.environ.get('PORT', 5001))
    # debug=True 只适用于开发环境，生产环境应使用 Gunicorn 或 uWSGI
    # host='0.0.0.0' 使服务可以从外部访问（如果防火墙允许）
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true', host='0.0.0.0', port=port) 