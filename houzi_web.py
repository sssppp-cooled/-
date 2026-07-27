import os, base64
from playwright.sync_api import sync_playwright
from openai import OpenAI

KEY = os.getenv("DASHSCOPE_KEY", "YOUR_KEY")
URL = "https://www.truepeoplesearch.com/"

try:
    with sync_playwright() as p:
        pg = p.chromium.launch(headless=True).new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36")
        pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(3000)
        img = pg.screenshot(full_page=True)

    b64 = base64.b64encode(img).decode()
    r = OpenAI(api_key=KEY, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1").chat.completions.create(
        model="qwen3-vl-32b-thinking",
        extra_body={"enable_thinking": False},
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            {"type": "text", "text": "描述排版 /nothink"}
        ]}]
    )
    print("🐒:", r.choices[0].message.content)
except Exception as e:
    print("💥:", e)
