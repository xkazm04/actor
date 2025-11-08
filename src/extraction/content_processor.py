"""
Content Processor - Processes HTML/PDF content and converts to clean Markdown.
Extracts main content, removes ads/navbars, and chunks long content.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from apify import Actor
from src.cache.cache_manager import get_cache_manager


class ContentProcessor:
    """
    Processes raw content (HTML, PDF, text) into clean, structured format.
    """
    
    def __init__(self):
        """Initialize content processor."""
        # Phase 6: Initialize caching
        self.cache_manager = get_cache_manager()
    
    async def process(self, content_data: Dict) -> Dict:
        """
        Process raw content into clean format.
        
        Args:
            content_data: Dictionary with raw content from fetcher
            
        Returns:
            Processed content dictionary with markdown, metadata, and chunks
        """
        url = content_data.get('url', '')
        
        # Phase 6: Check cache for processed content
        if url:
            cached_processed = await self.cache_manager.get_processed_content(url)
            if cached_processed:
                Actor.log.debug(f"Cache hit for processed content: {url[:50]}...")
                return cached_processed
        
        content_type = content_data.get('content_type', 'unknown')
        
        if content_type == 'html':
            result = self._process_html(content_data)
        elif content_type == 'pdf':
            result = self._process_pdf(content_data)
        elif content_type == 'text':
            result = self._process_text(content_data)
        else:
            Actor.log.warning(f"Unknown content type: {content_type}")
            result = self._process_text(content_data)
        
        # Phase 6: Cache processed content
        if url and result.get('status') == 'success':
            await self.cache_manager.set_processed_content(url, result)
        
        return result
    
    def _process_html(self, content_data: Dict) -> Dict:
        """Process HTML content."""
        html = content_data.get('raw_html', '')
        url = content_data.get('url', '')
        
        if not html:
            return {
                'url': url,
                'markdown': '',
                'metadata': content_data.get('metadata', {}),
                'chunks': [],
                'status': 'empty'
            }
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Extract title
            title = None
            if soup.title:
                title_text = soup.title.get_text()
                if title_text:
                    title = title_text.strip()
            else:
                h1 = soup.find('h1')
                if h1:
                    title_text = h1.get_text()
                    if title_text:
                        title = title_text.strip()
            
            # Extract main content
            # Try common article/content selectors
            main_content = None
            for selector in ['article', 'main', '[role="main"]', '.content', '#content', '.post', '.article']:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                # Fallback to body
                main_content = soup.find('body') or soup
            
            # Extract text and convert to markdown-like format
            markdown = self._html_to_markdown(main_content)
            
            # Extract metadata
            metadata = content_data.get('metadata', {}).copy()
            if title:
                metadata['title'] = title
            
            # Extract publish date if available
            publish_date = self._extract_publish_date(soup)
            if publish_date:
                metadata['publish_date'] = publish_date.isoformat()
            
            # Extract author if available
            author = self._extract_author(soup)
            if author:
                metadata['author'] = author
            
            # Chunk content
            chunks = self._chunk_content(markdown, max_tokens=1000)
            
            return {
                'url': url,
                'markdown': markdown,
                'metadata': metadata,
                'chunks': chunks,
                'status': 'success',
                'word_count': len(markdown.split())
            }
        
        except Exception as e:
            Actor.log.error(f"Error processing HTML from {url}: {e}")
            return {
                'url': url,
                'markdown': '',
                'metadata': content_data.get('metadata', {}),
                'chunks': [],
                'status': 'error',
                'error': str(e)
            }
    
    def _html_to_markdown(self, element) -> str:
        """Convert HTML element to Markdown."""
        markdown_parts = []
        
        for child in element.children:
            if hasattr(child, 'name') and child.name is not None:
                tag_name = child.name.lower()
                
                if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    level = int(tag_name[1])
                    text = child.get_text()
                    if text:
                        text = text.strip()
                        if text:
                            markdown_parts.append(f"{'#' * level} {text}\n")
                
                elif tag_name == 'p':
                    text = child.get_text()
                    if text:
                        text = text.strip()
                        if text:
                            markdown_parts.append(f"{text}\n\n")
                
                elif tag_name == 'ul' or tag_name == 'ol':
                    items = child.find_all('li', recursive=False)
                    for item in items:
                        text = item.get_text()
                        if text:
                            text = text.strip()
                            if text:
                                prefix = "- " if tag_name == 'ul' else "1. "
                                markdown_parts.append(f"{prefix}{text}\n")
                    markdown_parts.append("\n")
                
                elif tag_name == 'blockquote':
                    text = child.get_text()
                    if text:
                        text = text.strip()
                        if text:
                            markdown_parts.append(f"> {text}\n\n")
                
                elif tag_name == 'a':
                    text = child.get_text()
                    href = child.get('href', '')
                    if text:
                        text = text.strip()
                    if text and href:
                        markdown_parts.append(f"[{text}]({href})")
                    elif text:
                        markdown_parts.append(text)
                
                elif tag_name == 'strong' or tag_name == 'b':
                    text = child.get_text()
                    if text:
                        text = text.strip()
                        if text:
                            markdown_parts.append(f"**{text}**")
                
                elif tag_name == 'em' or tag_name == 'i':
                    text = child.get_text()
                    if text:
                        text = text.strip()
                        if text:
                            markdown_parts.append(f"*{text}*")
                
                elif tag_name == 'code':
                    text = child.get_text()
                    if text:
                        text = text.strip()
                        if text:
                            markdown_parts.append(f"`{text}`")
                
                else:
                    # Recursively process nested elements
                    nested = self._html_to_markdown(child)
                    if nested.strip():
                        markdown_parts.append(nested)
            else:
                # Text node
                text = str(child).strip()
                if text:
                    markdown_parts.append(text)
        
        return ''.join(markdown_parts)
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publish date from HTML."""
        # Try common meta tags
        for selector in [
            'meta[property="article:published_time"]',
            'meta[name="publish-date"]',
            'meta[name="date"]',
            'time[datetime]'
        ]:
            element = soup.select_one(selector)
            if element:
                date_str = element.get('content') or element.get('datetime')
                if date_str:
                    try:
                        # Try parsing ISO format
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        pass
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from HTML."""
        # Try common meta tags
        for selector in [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '[rel="author"]'
        ]:
            element = soup.select_one(selector)
            if element:
                author = element.get('content')
                if not author:
                    author_text = element.get_text()
                    if author_text:
                        author = author_text
                if author:
                    return str(author).strip()
        
        return None
    
    def _chunk_content(self, content: str, max_tokens: int = 1000) -> List[Dict]:
        """
        Chunk content into manageable sections.
        Uses approximate token counting (1 token ≈ 4 characters).
        
        Args:
            content: Content to chunk
            max_tokens: Maximum tokens per chunk
            
        Returns:
            List of chunk dictionaries
        """
        # Approximate: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        chunks = []
        paragraphs = content.split('\n\n')
        
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            if current_length + para_length > max_chars and current_chunk:
                # Save current chunk
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'token_count': current_length // 4,
                    'char_count': current_length
                })
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length + 2  # +2 for \n\n
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'token_count': current_length // 4,
                'char_count': current_length
            })
        
        return chunks
    
    def _process_pdf(self, content_data: Dict) -> Dict:
        """Process PDF content (placeholder - requires pdfplumber or similar)."""
        url = content_data.get('url', '')
        Actor.log.warning(f"PDF processing not fully implemented for {url}")
        
        return {
            'url': url,
            'markdown': '',
            'metadata': content_data.get('metadata', {}),
            'chunks': [],
            'status': 'pdf_not_processed',
            'note': 'PDF content extraction requires additional libraries'
        }
    
    def _process_text(self, content_data: Dict) -> Dict:
        """Process plain text content."""
        url = content_data.get('url', '')
        content = content_data.get('content', '')
        
        chunks = self._chunk_content(content)
        
        return {
            'url': url,
            'markdown': content,
            'metadata': content_data.get('metadata', {}),
            'chunks': chunks,
            'status': 'success',
            'word_count': len(content.split())
        }


def process_content(content_data: Dict) -> Dict:
    """
    Convenience function to process content.
    
    Args:
        content_data: Raw content dictionary
        
    Returns:
        Processed content dictionary
    """
    processor = ContentProcessor()
    return processor.process(content_data)

