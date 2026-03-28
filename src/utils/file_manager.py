import os
import aiofiles

from pathlib import Path

from src.config.logger import Logger

root_folder = Path(__name__).parent.parent
logger = Logger(__name__)

class FileManager:
    def __init__(self, folder:str = "output"):
        self.path = root_folder
        self.folder = folder
        
    def get_full_path(self, filename: str):
        full_folder = os.path.join(self.path, self.folder)
        os.makedirs(full_folder, exist_ok=True)
        return os.path.join(full_folder, filename)
    
    async def save_content_as_file(self, filename: str, ext: str, content: str, index:int = 1, ) -> str:
        filename = "{filename}-{index}.{ext}".format(
            filename=filename,
            ext=ext,
            index=index
        )
        
        file_path = self.get_full_path(filename=filename)
        
        async with aiofiles.open(file_path, "w") as fp:
            await fp.write(content)
            
        return file_path
    
    async def save_content_bytes_as_file(self, filename: str, ext: str, content: str, index:int = 1, ) -> str:
        filename = "{filename}-{index}.{ext}".format(
            filename=filename,
            ext=ext,
            index=index
        )
        
        file_path = self.get_full_path(filename=filename)
        
        async with aiofiles.open(file_path, "wb") as fp:
            await fp.write(content)
            
        return file_path