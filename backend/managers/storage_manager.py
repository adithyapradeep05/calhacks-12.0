import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
import httpx
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages Supabase Storage operations for file uploads and downloads."""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not all([self.url, self.key]):
            raise ValueError("SUPABASE_URL and SUPABASE_KEY are required")
        
        # Use service key for admin operations
        self.client: Client = create_client(self.url, self.service_key or self.key)
        
        # Available buckets by category
        self.category_buckets = {
            "legal": "legal",
            "technical": "technical", 
            "financial": "financial",
            "hr": "hr",  # Keep "hr" for Supabase bucket name
            "hr_docs": "hr",  # Map hr_docs to hr bucket
            "general": "general"
        }
    
    def upload_file(self, local_file_path: str, category: str, 
                   filename: Optional[str] = None) -> str:
        """Upload a file to the appropriate Supabase Storage bucket."""
        try:
            bucket_name = self.category_buckets.get(category, "general")
            
            # Read file content
            with open(local_file_path, 'rb') as f:
                file_content = f.read()
            
            # Generate unique filename if not provided
            if not filename:
                filename = Path(local_file_path).name
            
            # Upload to Supabase Storage
            result = self.client.storage.from_(bucket_name).upload(
                path=filename,
                file=file_content,
                file_options={"content-type": self._get_content_type(filename)}
            )
            
            if result:
                # Return the public URL
                return self.get_public_url(bucket_name, filename)
            else:
                raise Exception("Upload failed")
                
        except Exception as e:
            logger.error(f"Error uploading file {local_file_path} to {category}: {e}")
            raise
    
    def get_public_url(self, bucket_name: str, filename: str) -> str:
        """Get the public URL for a file in storage."""
        try:
            result = self.client.storage.from_(bucket_name).get_public_url(filename)
            return result
        except Exception as e:
            logger.error(f"Error getting public URL for {bucket_name}/{filename}: {e}")
            raise
    
    def download_file(self, bucket_name: str, filename: str, 
                     local_path: str) -> bool:
        """Download a file from Supabase Storage."""
        try:
            result = self.client.storage.from_(bucket_name).download(filename)
            
            if result:
                with open(local_path, 'wb') as f:
                    f.write(result)
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error downloading file {bucket_name}/{filename}: {e}")
            return False
    
    def delete_file(self, bucket_name: str, filename: str) -> bool:
        """Delete a file from Supabase Storage."""
        try:
            result = self.client.storage.from_(bucket_name).remove([filename])
            return len(result) > 0
        except Exception as e:
            logger.error(f"Error deleting file {bucket_name}/{filename}: {e}")
            return False
    
    def list_files(self, bucket_name: str, category: Optional[str] = None) -> list:
        """List files in a bucket."""
        try:
            bucket = self.category_buckets.get(category, bucket_name)
            result = self.client.storage.from_(bucket).list()
            return result
        except Exception as e:
            logger.error(f"Error listing files in {bucket_name}: {e}")
            return []
    
    def get_file_info(self, bucket_name: str, filename: str) -> Optional[Dict[str, Any]]:
        """Get information about a file."""
        try:
            result = self.client.storage.from_(bucket_name).list()
            for file_info in result:
                if file_info.get('name') == filename:
                    return file_info
            return None
        except Exception as e:
            logger.error(f"Error getting file info for {bucket_name}/{filename}: {e}")
            return None
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension."""
        extension = Path(filename).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }
        return content_types.get(extension, 'application/octet-stream')
    
    def health_check(self) -> bool:
        """Check if Supabase Storage is accessible."""
        try:
            # Try to list files in the general bucket
            result = self.client.storage.from_("general").list()
            return True
        except Exception as e:
            logger.error(f"Supabase Storage health check failed: {e}")
            return False
    
    def create_buckets_if_not_exist(self):
        """Create storage buckets if they don't exist."""
        try:
            for bucket_name in self.category_buckets.values():
                try:
                    # Try to list the bucket to see if it exists
                    self.client.storage.from_(bucket_name).list()
                except:
                    # If listing fails, try to create the bucket
                    try:
                        self.client.storage.create_bucket(bucket_name, public=True)
                        logger.info(f"Created bucket: {bucket_name}")
                    except Exception as e:
                        logger.warning(f"Could not create bucket {bucket_name}: {e}")
        except Exception as e:
            logger.error(f"Error creating buckets: {e}")
