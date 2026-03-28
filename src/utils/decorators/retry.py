import asyncio
import functools

from src.config.logger import Logger

logger = Logger(__name__)

def retry(retries=3, initial_delay=1, backoff_factor=2):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error("The connection raise the error {e}".format(e=str(e)))
                    if attempt == retries:
                        raise e
                    
                    logger.warn(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator