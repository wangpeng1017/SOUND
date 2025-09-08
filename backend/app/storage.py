"""
Vercel Blob存储服务
"""

import os
import aiofiles
from typing import BinaryIO, Optional
from fastapi import UploadFile
import httpx
import uuid
from datetime import datetime
import mimetypes
import json

class BlobStorage:
    """Vercel Blob存储服务类"""
    
    def __init__(self):
        self.token = os.getenv("BLOB_READ_WRITE_TOKEN")
        if not self.token:
            raise ValueError("BLOB_READ_WRITE_TOKEN environment variable is required")
    
    async def upload_file(
        self, 
        file: UploadFile, 
        folder: str = "audio",
        custom_filename: Optional[str] = None
    ) -> dict:
        """
        上传文件到Vercel Blob存储
        
        Args:
            file: FastAPI UploadFile对象
            folder: 存储文件夹
            custom_filename: 自定义文件名
            
        Returns:
            dict: 包含url, size, filename等信息
        """
        try:
            # 生成文件名
            if custom_filename:
                filename = custom_filename
            else:
                # 生成唯一文件名
                file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                filename = f"{timestamp}_{unique_id}{file_ext}"
            
            # 构建完整路径
            blob_path = f"{folder}/{filename}"
            
            # 读取文件内容
            content = await file.read()
            
            # 上传到Vercel Blob (使用HTTP API)
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    "https://blob.vercel-storage.com",
                    headers={
                        "authorization": f"Bearer {self.token}",
                        "x-content-type": file.content_type or "application/octet-stream"
                    },
                    params={"filename": blob_path},
                    content=content
                )

                if response.status_code != 200:
                    raise Exception(f"Upload failed: {response.status_code}")

                result = response.json()
            
            return {
                "url": result.get("url", f"https://blob.vercel-storage.com/{blob_path}"),
                "size": len(content),
                "filename": filename,
                "path": blob_path,
                "content_type": file.content_type or mimetypes.guess_type(filename)[0]
            }
            
        except Exception as e:
            raise Exception(f"文件上传失败: {str(e)}")
    
    async def upload_bytes(
        self, 
        content: bytes, 
        filename: str,
        folder: str = "audio",
        content_type: Optional[str] = None
    ) -> dict:
        """
        上传字节数据到Vercel Blob存储
        
        Args:
            content: 文件字节内容
            filename: 文件名
            folder: 存储文件夹
            content_type: MIME类型
            
        Returns:
            dict: 包含url, size, filename等信息
        """
        try:
            # 构建完整路径
            blob_path = f"{folder}/{filename}"
            
            # 上传到Vercel Blob
            response = await put(
                pathname=blob_path,
                body=content,
                options={
                    "access": "public",
                    "token": self.token,
                    "contentType": content_type or mimetypes.guess_type(filename)[0]
                }
            )
            
            return {
                "url": response.url,
                "size": len(content),
                "filename": filename,
                "path": blob_path,
                "content_type": content_type
            }
            
        except Exception as e:
            raise Exception(f"文件上传失败: {str(e)}")
    
    async def delete_file(self, url: str) -> bool:
        """
        删除文件
        
        Args:
            url: 文件URL
            
        Returns:
            bool: 删除是否成功
        """
        try:
            await delete(url, token=self.token)
            return True
        except Exception as e:
            print(f"文件删除失败: {str(e)}")
            return False
    
    async def list_files(self, prefix: Optional[str] = None) -> list:
        """
        列出文件
        
        Args:
            prefix: 文件路径前缀
            
        Returns:
            list: 文件列表
        """
        try:
            response = await list_blobs(
                options={
                    "token": self.token,
                    "prefix": prefix
                }
            )
            return response.blobs
        except Exception as e:
            print(f"文件列表获取失败: {str(e)}")
            return []

# 全局存储实例
storage = BlobStorage()
