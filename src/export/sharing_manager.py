"""
Sharing Manager - Handles sharing functionality for research reports.
Generates shareable links and manages sharing options.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from apify import Actor


class SharingManager:
    """
    Handles sharing functionality for research reports.
    Generates shareable links and manages sharing options.
    """
    
    def __init__(self):
        """Initialize sharing manager."""
        pass
    
    def generate_shareable_link(
        self,
        report_id: str,
        expiration_days: int = 30,
        access_level: str = "view"
    ) -> Dict:
        """
        Generate shareable link for report.
        
        Args:
            report_id: Report/run ID
            expiration_days: Days until link expires
            access_level: Access level (view, download, edit)
            
        Returns:
            Shareable link information
        """
        # Generate share token (simplified - would use proper token generation in production)
        import secrets
        share_token = secrets.token_urlsafe(32)
        
        expiration_date = datetime.now() + timedelta(days=expiration_days)
        
        # Store sharing info in Key-Value Store
        sharing_info = {
            'report_id': report_id,
            'token': share_token,
            'expiration_date': expiration_date.isoformat(),
            'access_level': access_level,
            'created_at': datetime.now().isoformat(),
            'access_count': 0
        }
        
        share_key = f'share_{share_token}'
        # Note: Would use await Actor.set_value() in async context
        # For now, return the info
        
        # Generate shareable URL (would be actual URL in production)
        shareable_url = f"https://apify.com/share/{share_token}"
        
        return {
            'shareable_url': shareable_url,
            'token': share_token,
            'expiration_date': expiration_date.isoformat(),
            'access_level': access_level,
            'sharing_info': sharing_info
        }
    
    def create_public_link(
        self,
        report_id: str,
        password: Optional[str] = None
    ) -> Dict:
        """
        Create public link (no expiration, optional password).
        
        Args:
            report_id: Report/run ID
            password: Optional password protection
            
        Returns:
            Public link information
        """
        import secrets
        public_token = secrets.token_urlsafe(32)
        
        public_info = {
            'report_id': report_id,
            'token': public_token,
            'is_public': True,
            'has_password': password is not None,
            'created_at': datetime.now().isoformat()
        }
        
        public_url = f"https://apify.com/public/{public_token}"
        
        return {
            'public_url': public_url,
            'token': public_token,
            'has_password': password is not None,
            'public_info': public_info
        }
    
    def get_sharing_options(self) -> Dict:
        """
        Get available sharing options.
        
        Returns:
            Dictionary with sharing options
        """
        return {
            'shareable_link': {
                'name': 'Shareable Link',
                'description': 'Generate a link that expires after specified days',
                'supports_expiration': True,
                'supports_password': False,
                'access_levels': ['view', 'download']
            },
            'public_link': {
                'name': 'Public Link',
                'description': 'Create a permanent public link (optional password)',
                'supports_expiration': False,
                'supports_password': True,
                'access_levels': ['view']
            },
            'email_share': {
                'name': 'Email Share',
                'description': 'Send report via email',
                'supports_expiration': False,
                'supports_password': False,
                'access_levels': ['view']
            },
            'embed_code': {
                'name': 'Embed Code',
                'description': 'Generate embed code for websites',
                'supports_expiration': True,
                'supports_password': False,
                'access_levels': ['view']
            }
        }
    
    def generate_embed_code(
        self,
        report_id: str,
        width: int = 800,
        height: int = 600
    ) -> Dict:
        """
        Generate embed code for report.
        
        Args:
            report_id: Report/run ID
            width: Embed width in pixels
            height: Embed height in pixels
            
        Returns:
            Embed code information
        """
        import secrets
        embed_token = secrets.token_urlsafe(32)
        
        embed_url = f"https://apify.com/embed/{embed_token}"
        
        embed_code = f"""<iframe 
    src="{embed_url}" 
    width="{width}" 
    height="{height}" 
    frameborder="0" 
    allowfullscreen>
</iframe>"""
        
        return {
            'embed_code': embed_code,
            'embed_url': embed_url,
            'token': embed_token,
            'width': width,
            'height': height
        }


def create_sharing_manager() -> SharingManager:
    """Create a sharing manager instance."""
    return SharingManager()



