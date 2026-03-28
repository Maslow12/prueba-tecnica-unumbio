import io
import asyncio
import json

from PIL import Image

from urllib.parse import urlencode

from src.config.logger import Logger
from src.utils.playwright_scraper import PlaywrightScraper
from src.utils.request_scraper import RequestsScraper

from src.scrapers.cambodia_ip.properties import (
    properties,
    get_payload_filter_api,
    build_page_url
)
from src.utils.file_manager import FileManager

logger = Logger(__name__)

class CambodiaIpScraper:
    def __init__(self, filing_number: str, options: dict = {}):
        self.async_requests = RequestsScraper()
        self.playwright_scraper = PlaywrightScraper()
        self.file_manager = FileManager()
        self.filing_number = filing_number
        self.options = options
        
    @staticmethod
    def verify_content_image(content: bytes) -> bool:
        try:
            img = Image.open(io.BytesIO(content))
            img.verify()
            return True, img.format
        except Exception as e:
            return False, None
        
    @staticmethod
    def parse_filename(filing_number:str) -> str:
        return filing_number.replace("/", "")
    
    @staticmethod
    def build_url_with_params(url:str, query_params:dict):
        encoded_params = urlencode(query_params)
        
        return "{url}&{params}".format(
            url=url,
            params=encoded_params
        )
        
    async def download_image(self, code_id: str) -> None:
        image_url = properties["image_url"].format(
            code=code_id
        )
        
        content_bytes = await self.async_requests.get_content_as_bytes(
            url=image_url
        )
        
        if not content_bytes or not self.verify_content_image(content=content_bytes):
            logger.error("Not found image for the filing_number: {filing_number}".format(
                filing_number=self.filing_number
            ))
            return
        
        save_path = await self.file_manager.save_content_bytes_as_file(
            filename=self.parse_filename(self.filing_number),
            ext="jpg",
            content=content_bytes,
            index=2
        )
        
        logger.info("The image is save for the {filing_number} in the path {save_path}".format(
                filing_number=self.filing_number,
                save_path=save_path
            )      
        )
        
    async def download_html_page(self, code_id) -> None:
        
        logger.info("Downloading the HTML for the filing_number: {filing_number}".format(
            filing_number=self.filing_number
        ))
        
        await self.playwright_scraper.start()
        
        url = build_page_url(
            code_id=code_id,
            filing_number=self.filing_number
        )
        
        page_content = await self.playwright_scraper.get_page_html(
            url=url
        )
        
        html_file_path = await self.file_manager.save_content_as_file(
            filename=self.parse_filename(self.filing_number),
            ext="html",
            content=page_content
        )
        
        logger.info("The html page is save for the {filing_number} in the path {save_path}".format(
                filing_number=self.filing_number,
                save_path=html_file_path
            )      
        )
        
    async def scrape(self):
        logger.info("Start the scraping for the filing_number: {filing_number}".format(
            filing_number=self.filing_number
        ))
        
        payload_filter = json.dumps(get_payload_filter_api(filing_number=self.filing_number))
        api_json = await self.async_requests.get_json(
            url=properties["api_url"], 
            method="post", 
            data=payload_filter, 
            headers=properties["api_headers"]
        )
        
        data = api_json.get("data", {}).get("data", {})
        
        if data and len(data) > 0:
            register:dict = data[0]
            code_id = register.get("id")
        else:
            logger.error("Not found data for the filing_number: {filing_number}".format(
                filing_number=self.filing_number
            ))
            return
        
        if code_id:
            
            logger.info("Download the image for the code {code}".format(
                code=code_id
            ))
            
            await asyncio.gather(
                self.download_image(code_id=code_id),
                self.download_html_page(code_id=code_id)
            )
    
        else:
            logger.warn("Not found code ID for download the image and the HTML page for the filling_number: {filing_number}".format(
                filing_number=self.filing_number
            ))
        return
    
    async def close(self):
        await self.playwright_scraper.close()
        await self.async_requests.close()