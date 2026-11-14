"""
Day 2 练习：第一个 Function Calling（函数调用）脚本
--------------------------------------------------
它做的事：让本地大模型在"聊天"时，自己判断该不该调用我们写好的函数，
调用完再把结果翻译成人话回答你。

跑法：python3 weather_fc.py
"""

import json          # 处理 JSON（一种通用的数据格式，长得像 {"键": "值"}）
import urllib.request  # Python 自带的"发网络请求"工具，不用额外装包

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"   # 你本机 Ollama 服务的地址
MODEL = "qwen3:14b"                              # 用哪个模型


# ============ 1. 我们自己写的"真函数" ============
# 这就是 AI 将来能"按"的那个按钮。现在用假数据，
# 以后把这里换成真天气 API（或查你们 SOP 库）就是真业务了。
def get_weather(city: str) -> str:
    """查询某城市天气。city = 城市名"""
    fake_data = {
        "北京": "晴，12℃，北风 3 级，空气质量良",
        "上海": "多云，18℃，东风 2 级",
        "广州": "小雨，24℃，湿度 85%",
        "杭州": "阴，15℃，微风",
    }
    return fake_data.get(city, f"{city}：暂无数据")


# ============ 2. 告诉模型"你有哪些按钮可用" ============
# 这段叫 tool schema（工具描述）：不是代码，是给模型看的说明书。
# 模型靠 description（描述）判断什么时候该按哪个按钮。
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，例如：北京"}
                },
                "required": ["city"],
            },
        },
    }
]


# ============ 3. 和模型对话的通用函数 ============
def chat(messages):
    """把 messages（对话历史）发给模型，拿回它的回复"""
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,      # 带上工具清单
        "stream": False,     # False = 等它说完一次性返回，不逐字吐字
        "think": False,      # 跳过 Qwen3 的思考过程，输出干净些
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),   # 转成字节流发出去
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:   # 等最多 180 秒
        return json.loads(resp.read().decode("utf-8"))["message"]


# ============ 4. 主流程：一轮完整的"函数调用" ============
def main():
    question = "1+1 等于几？"
    print(f"\n👤 我问：{question}\n")

    messages = [{"role": "user", "content": question}]

    # —— 第 1 轮：模型自己决定要不要调用工具 ——
    reply = chat(messages)
    tool_calls = reply.get("tool_calls")

    if not tool_calls:
        print("🤖 模型没调用任何工具，直接回答：")
        print(reply.get("content"))
        return

    print("🔧 模型决定调用工具：")
    messages.append(reply)   # 把模型"要调工具"这一步也记进对话历史

    for call in tool_calls:
        name = call["function"]["name"]
        args = call["function"]["arguments"]      # 模型传回来的参数，如 {"city": "北京"}
        if isinstance(args, str):                  # 有的模型给的是字符串，转成字典
            args = json.loads(args)

        print(f"   → 函数名：{name}")
        print(f"   → 参数：{args}")

        # 真正的执行在这里（模型本身不能执行代码，它只会"说要调"，执行必须我们做）
        result = get_weather(args["city"])
        print(f"   → 函数返回：{result}\n")

        # 把函数结果作为一条 tool（工具）消息塞回对话
        messages.append(
            {"role": "tool", "content": result, "tool_name": name}
        )

    # —— 第 2 轮：模型看着函数结果，用人话回答 ——
    final = chat(messages)
    print("🤖 最终回答：")
    print(final.get("content"))


if __name__ == "__main__":
    main()
