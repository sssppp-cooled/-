from enum import Enum
from datetime import datetime, timedelta


class BlockType(Enum):
    CF_CHALLENGE = "cf_challenge"
    CF_BLOCK = "cf_block"
    RATE_LIMIT = "rate_limit"
    CAPTCHA = "captcha"
    GEO_BLOCK = "geo_block"
    UNKNOWN = "unknown"


class ErrorHandler:
    def __init__(self, proxy_pool):
        self.pool = proxy_pool
    
    def detect(self, content: str, status_code: int = 200) -> BlockType:
        text = content.lower()
        if status_code == 403 and "cf-challenge" in text:
            return BlockType.CF_CHALLENGE
        elif status_code == 403 and "1020" in text:
            return BlockType.CF_BLOCK
        elif status_code == 429:
            return BlockType.RATE_LIMIT
        elif "captcha" in text or "turnstile" in text:
            return BlockType.CAPTCHA
        elif status_code == 403 and ("access denied" in text or "blocked" in text):
            return BlockType.GEO_BLOCK
        return BlockType.UNKNOWN
    
    def handle(self, proxy, block_type: BlockType, attempt: int) -> float:
        if block_type == BlockType.CF_BLOCK:
            proxy.fail_count = 999
        elif block_type == BlockType.RATE_LIMIT:
            proxy.last_fail = datetime.now() + timedelta(hours=2)
        elif block_type == BlockType.CAPTCHA:
            proxy.fail_count += 2
        elif block_type == BlockType.GEO_BLOCK:
            proxy.fail_count = 9999
        
        backoff = min(300, (2 ** attempt) * 5 + random.uniform(0, 10))
        return backoff
