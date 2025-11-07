"""
Research Modes - Tiered research configurations.
Defines Quick, Standard, and Deep modes with different parameters.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ResearchModeConfig:
    """Configuration for a research mode."""
    name: str
    max_searches: int
    max_sources_to_process: int
    max_sources_to_analyze: int
    enable_reasoning: bool
    reasoning_iterations: int
    enable_plan_refinement: bool
    plan_refinement_interval: int  # Every N searches
    estimated_cost_min: float
    estimated_cost_max: float
    estimated_time_min: int  # minutes
    estimated_time_max: int  # minutes
    target_report_length_min: int  # words
    target_report_length_max: int  # words
    description: str


class ResearchModes:
    """
    Defines tiered research modes with different configurations.
    """
    
    QUICK = ResearchModeConfig(
        name="quick",
        max_searches=10,
        max_sources_to_process=20,
        max_sources_to_analyze=10,
        enable_reasoning=False,
        reasoning_iterations=0,
        enable_plan_refinement=False,
        plan_refinement_interval=0,
        estimated_cost_min=0.10,
        estimated_cost_max=0.25,
        estimated_time_min=2,
        estimated_time_max=3,
        target_report_length_min=500,
        target_report_length_max=1000,
        description="Quick fact-checking and simple queries. Fast results with basic analysis."
    )
    
    STANDARD = ResearchModeConfig(
        name="standard",
        max_searches=30,
        max_sources_to_process=50,
        max_sources_to_analyze=30,
        enable_reasoning=True,
        reasoning_iterations=3,
        enable_plan_refinement=True,
        plan_refinement_interval=10,
        estimated_cost_min=0.50,
        estimated_cost_max=1.00,
        estimated_time_min=5,
        estimated_time_max=10,
        target_report_length_min=1500,
        target_report_length_max=3000,
        description="General research and competitive analysis. Balanced depth and speed."
    )
    
    DEEP = ResearchModeConfig(
        name="deep",
        max_searches=100,
        max_sources_to_process=200,
        max_sources_to_analyze=100,
        enable_reasoning=True,
        reasoning_iterations=10,
        enable_plan_refinement=True,
        plan_refinement_interval=5,
        estimated_cost_min=2.00,
        estimated_cost_max=5.00,
        estimated_time_min=15,
        estimated_time_max=30,
        target_report_length_min=3000,
        target_report_length_max=8000,
        description="Comprehensive research for academic or strategic purposes. Maximum depth and analysis."
    )
    
    @classmethod
    def get_mode(cls, mode_name: str) -> Optional[ResearchModeConfig]:
        """
        Get research mode configuration by name.
        
        Args:
            mode_name: Mode name (quick, standard, deep)
            
        Returns:
            ResearchModeConfig or None if not found
        """
        mode_name = mode_name.lower()
        if mode_name == "quick":
            return cls.QUICK
        elif mode_name == "standard":
            return cls.STANDARD
        elif mode_name == "deep":
            return cls.DEEP
        else:
            return None
    
    @classmethod
    def get_all_modes(cls) -> Dict[str, ResearchModeConfig]:
        """Get all available modes."""
        return {
            "quick": cls.QUICK,
            "standard": cls.STANDARD,
            "deep": cls.DEEP
        }
    
    @classmethod
    def apply_mode_to_input(cls, mode_name: str, input_data: Dict) -> Dict:
        """
        Apply mode configuration to input data.
        
        Args:
            mode_name: Mode name
            input_data: Input data dictionary
            
        Returns:
            Updated input data with mode-specific settings
        """
        mode = cls.get_mode(mode_name)
        if not mode:
            return input_data
        
        updated = input_data.copy()
        updated['max_searches'] = mode.max_searches
        updated['research_mode'] = mode_name
        
        return updated


def get_mode_config(mode_name: str) -> Optional[ResearchModeConfig]:
    """
    Convenience function to get mode configuration.
    
    Args:
        mode_name: Mode name
        
    Returns:
        ResearchModeConfig or None
    """
    return ResearchModes.get_mode(mode_name)



