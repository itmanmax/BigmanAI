# Allows importing zju_chat_client from the parent directory
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zju_chat_client import ZjuChatClient # 从包中导入

# --- 配置 ---
# 强烈建议使用环境变量来存储 API Key
# 您可以在运行脚本前设置环境变量： export ZJU_API_KEY='your_api_key_here'
# 或者，如果您确实需要，可以直接在这里提供 api_key 参数，但不推荐用于生产环境
# api_key = "your_api_key_here" # 不推荐
api_key = None # 让客户端从环境变量 ZJU_API_KEY 读取

model_name = "deepseek-r1-671b" # 替换为您需要使用的模型
user_prompt = "3.11与3.9谁大"
# --- 配置结束 ---

def run_non_streaming_example():
    """演示非流式调用。"""
    print("--- 非流式调用示例 ---")
    try:
        # 使用 'with' 语句确保会话被正确关闭
        with ZjuChatClient(api_key=api_key) as client:
            response_data = client.get_completion(
                model=model_name,
                user_content=user_prompt,
                stream=False # 获取完整响应
            )
            print("API 响应:")
            # print(response_data) # 打印原始字典

            # 提取并打印助手的回答内容
            if response_data and 'choices' in response_data and len(response_data['choices']) > 0:
                assistant_message = response_data['choices'][0].get('message', {})
                content = assistant_message.get('content')
                if content:
                    print("\n助手回答:")
                    print(content)
                else:
                    print("未在响应中找到 'content'。")
                # 打印 token 使用情况
                usage = response_data.get('usage')
                if usage:
                    print(f"\nToken 使用情况: {usage}")
            else:
                print("响应格式不符合预期，无法提取回答。")

    except ValueError as e:
        print(f"配置错误或 API 错误: {e}")
    except Exception as e:
        print(f"发生未预料的错误: {e}")
    print("-" * 20 + "\n")

def run_streaming_example():
    """演示流式调用。"""
    print("--- 流式调用示例 ---")
    accumulated_content = ""
    try:
        with ZjuChatClient(api_key=api_key) as client:
            response_stream = client.get_completion(
                model=model_name,
                user_content=user_prompt,
                stream=True # 请求流式响应
            )
            print("助手回答 (流式):")
            for chunk in response_stream:
                 # print(f"收到数据块: {chunk}") # 打印原始数据块以供调试
                 if chunk and 'choices' in chunk and len(chunk['choices']) > 0:
                    delta = chunk['choices'][0].get('delta', {})
                    content_piece = delta.get('content')
                    if content_piece:
                        print(content_piece, end='', flush=True) # 实时打印内容
                        accumulated_content += content_piece
                    # 可以在这里检查 finish_reason，如果需要的话
                    # finish_reason = chunk['choices'][0].get('finish_reason')
                    # if finish_reason:
                    #     print(f"\n流结束原因: {finish_reason}")
            print() # 换行

            # 流结束后可以处理完整内容，如果需要的话
            # print("\n--- 完整流式内容 ---")
            # print(accumulated_content)


    except ValueError as e:
        print(f"配置错误或 API 错误: {e}")
    except Exception as e:
        print(f"发生未预料的错误: {e}")
    print("-" * 20 + "\n")

if __name__ == "__main__":
    if not os.getenv("ZJU_API_KEY"):
        print("警告：环境变量 ZJU_API_KEY 未设置。")
        print("请设置 ZJU_API_KEY='your_api_key_here' 后再运行。")
        # 或者取消下面一行的注释并直接填入 key（不推荐）
        # api_key = "your_api_key_here"
        # if not api_key:
        #     exit("错误：需要 API Key。")

    run_non_streaming_example()
    run_streaming_example() 