import os
from dotenv import load_dotenv
from google import genai

load_dotenv("apikey.env") 
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 客户的真实投诉内容
text = "The trading platform is lagging again during my forex trade! I lost money because of this latency. I need someone to check my account and process a refund ASAP!"

# 要求 AI 输出 JSON 的提示词
prompt = f"""
请分析以下客户支持工单，并严格以 JSON 格式返回以下三个字段，不要输出任何其他多余的文字：
- "sentiment": (填写 Positive, Neutral, 或 Negative)
- "urgency": (填写 High, Medium, 或 Low)
- "category": (例如 Technical Issue, Billing, General Inquiry 等)

工单内容: "{text}"
"""

response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=prompt,
)

print(response.text)