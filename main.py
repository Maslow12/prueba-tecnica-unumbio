import asyncio
import argparse

from src.config.logger import Logger
from src.scrapers.cambodia_ip.scraper import CambodiaIpScraper

logger = Logger(__name__)

async def execute_scraper(scraper: CambodiaIpScraper):
    try:
        await scraper.scrape()
        await scraper.close()
    except Exception:
        await scraper.close()

async def main(filing_numbers: list):
    tasks = [execute_scraper(scraper=CambodiaIpScraper(filing_number=filing_number)) for filing_number in filing_numbers]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Process a list of Filing Number.")
    parser.add_argument("-i", "--filing_numbers", nargs='+', help="The list of the filing numbers")
    
    args = parser.parse_args()
    
    default_values = [
        "KH/49633/12",
        "KH/59286/14",
        "KH/83498/19",
        "KF/388383/19", # Wrong Number,
        "KF/345354/19", # Wrong Number,
        "KH/122290/26", # No Image
    ]
    
    list_filing_number = args.filing_numbers if args.filing_numbers else default_values
    
    try:
        asyncio.run(main(filing_numbers=list_filing_number))
        logger.info("Finish the scraping")
    except KeyboardInterrupt:
        logger.error("The process interrupted")
        exit(0)