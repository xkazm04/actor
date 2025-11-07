"""
Style Adapter - Applies writing style configuration to reports.
Adapts tone, reading level, and perspective based on user preferences.
"""

from typing import Dict, Optional
from apify import Actor


class StyleAdapter:
    """
    Adapts report writing style based on configuration.
    Applies tone, reading level, and perspective.
    """
    
    def __init__(self, scope_config):
        """
        Initialize style adapter.
        
        Args:
            scope_config: OutputScopeConfig instance
        """
        self.scope_config = scope_config
        self.writing_style = scope_config.writing_style
    
    def adapt_text(self, text: str) -> str:
        """
        Adapt text based on writing style configuration.
        
        Args:
            text: Original text
            
        Returns:
            Adapted text
        """
        # Apply tone
        text = self._apply_tone(text)
        
        # Apply reading level
        text = self._apply_reading_level(text)
        
        # Apply perspective
        text = self._apply_perspective(text)
        
        return text
    
    def get_style_instructions(self) -> str:
        """
        Get style instructions for LLM report generation.
        
        Returns:
            Style instructions string
        """
        instructions = []
        
        # Tone instructions
        tone = self.writing_style.get('tone', 'professional')
        tone_instructions = {
            'academic': 'Use formal academic language, third-person perspective, and extensive citations.',
            'professional': 'Use clear, structured, business-friendly language.',
            'conversational': 'Use accessible, engaging language with first/second-person perspective.',
            'technical': 'Use detailed, jargon-appropriate language with precision-focused terminology.'
        }
        instructions.append(tone_instructions.get(tone, tone_instructions['professional']))
        
        # Reading level instructions
        reading_level = self.writing_style.get('reading_level', 'intermediate')
        reading_level_instructions = {
            'expert': 'Assume domain knowledge - no need to explain basic concepts.',
            'intermediate': 'Provide some explanation for technical terms.',
            'general': 'Explain all concepts clearly for a general audience.'
        }
        instructions.append(reading_level_instructions.get(reading_level, reading_level_instructions['intermediate']))
        
        # Perspective instructions
        perspective = self.writing_style.get('perspective', 'objective')
        perspective_instructions = {
            'objective': 'Present information neutrally and balanced.',
            'critical': 'Identify weaknesses and challenge claims where appropriate.',
            'optimistic': 'Highlight potential and opportunities.'
        }
        instructions.append(perspective_instructions.get(perspective, perspective_instructions['objective']))
        
        return " ".join(instructions)
    
    def _apply_tone(self, text: str) -> str:
        """
        Apply tone to text.
        
        Args:
            text: Original text
            
        Returns:
            Text with tone applied
        """
        tone = self.writing_style.get('tone', 'professional')
        
        # Simple tone adaptation (can be enhanced with NLP)
        if tone == 'academic':
            # Replace informal phrases
            text = text.replace("we found", "the analysis revealed")
            text = text.replace("we can see", "it is evident")
        elif tone == 'conversational':
            # Make more accessible
            text = text.replace("it is evident", "we can see")
            text = text.replace("the analysis revealed", "we found")
        
        return text
    
    def _apply_reading_level(self, text: str) -> str:
        """
        Apply reading level to text.
        
        Args:
            text: Original text
            
        Returns:
            Text adapted for reading level
        """
        reading_level = self.writing_style.get('reading_level', 'intermediate')
        
        # Simple adaptation (can be enhanced)
        if reading_level == 'general':
            # Add explanations for technical terms (simplified)
            text = text.replace("API", "API (Application Programming Interface)")
        
        return text
    
    def _apply_perspective(self, text: str) -> str:
        """
        Apply perspective to text.
        
        Args:
            text: Original text
            
        Returns:
            Text with perspective applied
        """
        perspective = self.writing_style.get('perspective', 'objective')
        
        # Simple perspective adaptation (can be enhanced)
        if perspective == 'optimistic':
            # Emphasize positive aspects
            text = text.replace("challenge", "opportunity")
            text = text.replace("problem", "area for improvement")
        elif perspective == 'critical':
            # Add critical language
            if "however" not in text.lower():
                text = f"However, {text.lower()}"
        
        return text
    
    def format_section_header(self, section_name: str) -> str:
        """
        Format section header based on style.
        
        Args:
            section_name: Section name
            
        Returns:
            Formatted header
        """
        # Convert snake_case to Title Case
        formatted = section_name.replace('_', ' ').title()
        
        # Apply tone-specific formatting
        tone = self.writing_style.get('tone', 'professional')
        if tone == 'academic':
            # More formal headers
            formatted = formatted.replace('Key Findings', 'Key Findings from Literature Review')
        
        return formatted



