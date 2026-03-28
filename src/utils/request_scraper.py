import aiohttp

from src.config.logger import Logger
from src.utils.decorators.retry import retry

logger = Logger()

class RequestsScraper:
    def __init__(self, session = None, headers: dict = None):
        self.session = session
        self.headers = headers
        
        self.method = {
            "get": self.get,
            "post": self.post   
        }

    async def create_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
            
    async def close(self):
        if self.session:
            await self.session.close()

    @retry(retries=3, initial_delay=2)
    async def get(self, url: str, params: dict = {}, headers: dict = {}, **kwargs) -> aiohttp.ClientResponse:
        if not self.session or self.session.closed:
            await self.create_session()
        try:
            response = await self.session.get(url, params=params, headers=headers, **kwargs)
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            await self.close()
            raise e
            
    @retry(retries=3, initial_delay=2)
    async def post(self, url: str, params: dict = {}, headers: dict = {}, **kwargs) -> aiohttp.ClientResponse:
        if not self.session or self.session.closed:
            await self.create_session()
        try:
            response = await self.session.post(url, params=params, headers=headers, **kwargs)
            return response
            
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            await self.close()
            raise e

    async def get_content(self, url: str, method: str = "get", **kwargs) -> str:
        async with await self.method.get(method)(url=url, **kwargs) as response:
            response.raise_for_status()
            return await response.text()
        
    async def get_content_as_bytes(self, url: str, method: str = "get", **kwargs) -> str:
        async with await self.method.get(method)(url=url, **kwargs) as response:
            response.raise_for_status()
            return await response.read()
        
    async def get_json(self, url: str, method: str = "get", **kwargs) -> str:
        async with await self.method.get(method)(url=url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

    def get_cookies(self) -> dict:
        if not self.session:
            return {}
        return {cookie.key: cookie.value for cookie in self.session.cookie_jar}