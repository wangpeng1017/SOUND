"""
简化的Vercel Blob存储服务 - Vercel部署版本
"""

import os
import httpx
import uuid
from datetime import datetime
import mimetypes
from typing import Optional
from fastapi import UploadFile

class BlobStorage:
    """Vercel Blob存储服务类"""
    
    def __init__(self):
        self.token = os.getenv("BLOB_READ_WRITE_TOKEN")
        if not self.token:
            print("⚠️ BLOB_READ_WRITE_TOKEN not found, using mock storage")
    
    async def upload_file(
        self, 
        file: UploadFile, 
        folder: str = "audio",
        custom_filename: Optional[str] = None
    ) -> dict:
        """
        上传文件到Vercel Blob存储
        """
        try:
            # 生成文件名
            if custom_filename:
                filename = custom_filename
            else:
                file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                filename = f"{timestamp}_{unique_id}{file_ext}"
            
            # 构建完整路径
            blob_path = f"{folder}/{filename}"
            
            # 读取文件内容
            content = await file.read()
            
            if self.token:
                # 使用真实的Vercel Blob API
                async with httpx.AsyncClient() as client:
                    response = await client.put(
                        "https://blob.vercel-storage.com",
                        headers={
                            "authorization": f"Bearer {self.token}",
                            "x-content-type": file.content_type or "application/octet-stream"
                        },
                        params={"filename": blob_path},
                        content=content,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "url": result.get("url", f"https://blob.vercel-storage.com/{blob_path}"),
                            "size": len(content),
                            "filename": filename,
                            "path": blob_path,
                            "content_type": file.content_type or mimetypes.guess_type(filename)[0]
                        }
                    else:
                        raise Exception(f"Upload failed: {response.status_code} - {response.text}")
            else:
                # 模拟存储（开发/测试环境）
                mock_url = f"https://mock-storage.example.com/{blob_path}"
                return {
                    "url": mock_url,
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
        """
        try:
            blob_path = f"{folder}/{filename}"
            
            if self.token:
                # 使用真实的Vercel Blob API
                async with httpx.AsyncClient() as client:
                    response = await client.put(
                        "https://blob.vercel-storage.com",
                        headers={
                            "authorization": f"Bearer {self.token}",
                            "x-content-type": content_type or "application/octet-stream"
                        },
                        params={"filename": blob_path},
                        content=content,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "url": result.get("url", f"https://blob.vercel-storage.com/{blob_path}"),
                            "size": len(content),
                            "filename": filename,
                            "path": blob_path,
                            "content_type": content_type
                        }
                    else:
                        raise Exception(f"Upload failed: {response.status_code} - {response.text}")
            else:
                # 模拟存储
                mock_url = f"https://mock-storage.example.com/{blob_path}"
                return {
                    "url": mock_url,
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
        """
        try:
            if self.token and "blob.vercel-storage.com" in url:
                async with httpx.AsyncClient() as client:
                    response = await client.delete(
                        url,
                        headers={"authorization": f"Bearer {self.token}"},
                        timeout=30.0
                    )
                    return response.status_code == 200
            else:
                # 模拟删除
                print(f"Mock delete: {url}")
                return True
        except Exception as e:
            print(f"文件删除失败: {str(e)}")
            return False
    
    async def list_files(self, prefix: Optional[str] = None) -> list:
        """
        列出文件
        """
        try:
            if self.token:
                async with httpx.AsyncClient() as client:
                    params = {}
                    if prefix:
                        params["prefix"] = prefix
                    
                    response = await client.get(
                        "https://blob.vercel-storage.com",
                        headers={"authorization": f"Bearer {self.token}"},
                        params=params,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result.get("blobs", [])
            
            # 模拟文件列表
            return []
        except Exception as e:
            print(f"文件列表获取失败: {str(e)}")
            return []

# 全局存储实例
storage = BlobStorage()
