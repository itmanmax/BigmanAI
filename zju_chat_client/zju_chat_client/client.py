import requests
import os
import json
from typing import List, Dict, Optional, Generator, Union

class ZjuChatClient:
    """
    与 chat.zju.edu.cn API 交互的客户端。
    """
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://chat.zju.edu.cn/api/ai/v1"):
        """
        初始化客户端。

        Args:
            api_key: 您的 API Key。如果未提供，将尝试从环境变量 ZJU_API_KEY 读取。
            base_url: API 的基础 URL。
        """
        self.api_key = api_key or os.getenv("ZJU_API_KEY")
        if not self.api_key:
            raise ValueError("API Key 未提供，并且未设置 ZJU_API_KEY 环境变量。")
        self.base_url = base_url
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        })

    def _prepare_messages(self, user_content: str, system_content: Optional[str] = None) -> List[Dict[str, str]]:
        """准备 API 请求的消息列表。"""
        messages = []
        if system_content:
            messages.append({"role": "system", "content": system_content})
        messages.append({"role": "user", "content": user_content})
        return messages

    def get_completion(
        self,
        model: str,
        user_content: str,
        system_content: Optional[str] = "You are a helpful assistant.",
        stream: bool = False
    ) -> Union[Dict, Generator[Dict, None, None]]:
        """
        获取聊天补全结果。

        Args:
            model: 要使用的模型名称 (例如 "deepseek-r1-671b")。
            user_content: 用户输入的内容。
            system_content: 可选的系统提示内容。
            stream: 是否使用流式响应。

        Returns:
            如果 stream=False，返回包含完整响应的字典。
            如果 stream=True，返回一个生成器，逐块产生响应内容。

        Raises:
            requests.exceptions.RequestException: 如果发生网络或 API 错误。
            ValueError: 如果 API 返回错误信息。
        """
        url = f"{self.base_url}/chat/completions"
        messages = self._prepare_messages(user_content, system_content)
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }

        try:
            response = self._session.post(url, json=payload, stream=stream)
            response.raise_for_status() # 检查 HTTP 错误状态

            if stream:
                return self._handle_stream_response(response)
            else:
                return response.json()

        except requests.exceptions.RequestException as e:
            # 可以添加更详细的错误处理，例如记录日志
            error_msg = f"请求 API 时发生错误: {e}"
            # 尝试读取响应体中的错误信息
            error_details = None
            try:
                # 确保在访问 response.json() 前检查 response 是否存在且有内容
                if hasattr(e, 'response') and e.response is not None and e.response.content:
                     error_details = e.response.json()
                     error_msg += f"\nAPI 错误详情: {error_details}"
            except (json.JSONDecodeError, AttributeError):
                # 如果无法解析 JSON 或 response 对象不存在
                 pass
            print(error_msg) # 打印包含详情的错误消息
            # 根据需要重新抛出更具体的异常或 ValueError
            # 如果有 API 返回的具体错误，使用它
            if error_details:
                 raise ValueError(f"API 返回错误: {error_details}") from e
            else:
                 raise e # 重新抛出原始的网络异常

    def _handle_stream_response(self, response: requests.Response) -> Generator[Dict, None, None]:
        """处理流式响应 (SSE)。"""
        try:
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith('data: '):
                    try:
                        data_str = line[len('data: '):].strip()
                        if data_str == "[DONE]": # 检查流结束标记
                             break
                        if data_str:
                            yield json.loads(data_str)
                    except json.JSONDecodeError:
                         print(f"无法解析流中的 JSON 数据: {line}")
                         # 可以选择跳过无效行或引发错误
                         continue
        except Exception as e:
            print(f"处理流时发生错误: {e}")
            raise # 重新抛出异常


    def close(self):
        """关闭 HTTP 会话。"""
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 