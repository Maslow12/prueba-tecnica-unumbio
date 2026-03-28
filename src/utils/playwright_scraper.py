from playwright.async_api import (
    async_playwright
)


class PlaywrightScraper:
    def __init__(self, headless: bool = True, options: dict = {}):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.options = options
    
    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            **self.options
        )
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        return self
    
    async def close(self):
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def get_cookies(self, url: str = None) -> list:
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first or use context manager.")
        
        if url:
            cookies = await self.context.cookies([url])
        else:
            cookies = await self.context.cookies()
        
        return cookies
    
    async def get_cookies_as_dict(self, url: str) -> dict:
        cookies = await self.get_cookies(url)
        return {cookie['name']: cookie['value'] for cookie in cookies}
    
    async def get_page_html(self, url: str = None) -> str:
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first or use context manager.")
        
        if url:
            await self.page.goto(url, wait_until="networkidle")

        return await self.page.content()
    
    async def navigate(self, url: str, wait_until: str = "networkidle") -> None:
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first or use context manager.")
        
        await self.page.goto(url, wait_until=wait_until)
    
    async def wait_for_selector(self, selector: str, timeout: int = 5000) -> None:
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first or use context manager.")
        
        await self.page.wait_for_selector(selector, timeout=timeout)
    