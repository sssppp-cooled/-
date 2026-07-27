import os, base64
from openai import OpenAI

KEY = os.getenv("DASHSCOPE_KEY", "YOUR_KEY")
pngs = [f for f in os.listdir('.') if f.endswith('.png')]

if not pngs:
    print("没图"); exit()

with open(pngs[0], "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

try:
    r = OpenAI(api_key=KEY, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1").chat.completions.create(
        model="qwen3-vl-32b-thinking", 
        extra_body={"enable_thinking": False},
        messages=[{"role":"user", "content":[
            {"type":"image_url", "image_url":{"url":f"data:image/png;base64,{b64}"}}, 
            {"type":"text", "text":"这是啥 /nothink"}
        ]}]
    )
    print("🐒:", r.choices[0].message.content)
except Exception as e:
    print("💥:", e)
