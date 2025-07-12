"""
Compressed prompts loader for CIA system.
Reads prompts from MD files in the CIA Process Prompts directory.
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional, List
import logging
from dataclasses import dataclass

from ..config.constants import CIAPhase

logger = logging.getLogger(__name__)


@dataclass
class PromptMetadata:
    """Metadata extracted from prompt files."""
    phase: str
    title: str
    file_path: Path
    is_archive: bool
    content: str


class CompressedPromptsLoader:
    """Loads and manages CIA prompts from MD files."""
    
    # Phase mapping to directory names
    PHASE_DIRECTORY_MAP = {
        CIAPhase.PHASE_1A: ("Phase 1", "Foundational Business Intelligence"),
        CIAPhase.PHASE_1B: ("Phase 1", "DNA Research & ICP Discovery"),
        CIAPhase.PHASE_1C: ("Phase 1", "Key Person of Influence Assessment"),
        CIAPhase.PHASE_1D: ("Phase 1", "Competitive Intelligence"),
        CIAPhase.PHASE_1EB: ("Phase 1", "Business Intelligence Archive"),
        CIAPhase.PHASE_2A: ("Phase 2", "SEO Intelligence Analysis"),
        CIAPhase.PHASE_2B: ("Phase 2", "Social Intelligence Analysis"),
        CIAPhase.PHASE_2EB: ("Phase 2", "SEO + Social Intelligence Archive"),
        CIAPhase.PHASE_3A: ("Phase 3", "X com Trend Data Analysis"),
        CIAPhase.PHASE_3B: ("Phase 3", "Testimonials Analysis"),
        CIAPhase.PHASE_3C: ("Phase 3", "Comprehensive Strategic Synthesis"),
        CIAPhase.PHASE_3EB: ("Phase 3", "Advanced Intelligence Synthesis Archive"),
        CIAPhase.PHASE_4A: ("Phase 4", "Golden Hippo Offer Development"),
        CIAPhase.PHASE_5A: ("Phase 5", "Silo Convergence Blender"),
        CIAPhase.PHASE_6A: ("Phase 6", "Content Strategy Archive"),
    }
    
    def __init__(self, prompts_base_dir: Optional[str] = None):
        """Initialize the prompts loader.
        
        Args:
            prompts_base_dir: Base directory for CIA Process Prompts.
                            Defaults to 'CIA Process Prompts' in project root.
        """
        if prompts_base_dir is None:
            # Get project root (assuming we're in src/cia/)
            project_root = Path(__file__).parent.parent.parent
            prompts_base_dir = project_root / "CIA Process Prompts"
        
        self.prompts_base_dir = Path(prompts_base_dir)
        self._prompts_cache: Dict[CIAPhase, PromptMetadata] = {}
        self._loaded = False
        
        if not self.prompts_base_dir.exists():
            raise ValueError(f"CIA Process Prompts directory not found: {self.prompts_base_dir}")
    
    def load_all_prompts(self) -> None:
        """Load all prompts from the file system into cache."""
        if self._loaded:
            return
        
        logger.info(f"Loading CIA prompts from: {self.prompts_base_dir}")
        
        for phase, (phase_dir, title_pattern) in self.PHASE_DIRECTORY_MAP.items():
            try:
                prompt_metadata = self._load_phase_prompt(phase, phase_dir, title_pattern)
                if prompt_metadata:
                    self._prompts_cache[phase] = prompt_metadata
                    logger.info(f"Loaded prompt for {phase}: {prompt_metadata.title}")
                else:
                    logger.warning(f"No prompt found for {phase}")
            except Exception as e:
                logger.error(f"Failed to load prompt for {phase}: {e}")
        
        self._loaded = True
        logger.info(f"Loaded {len(self._prompts_cache)} prompts total")
    
    def _load_phase_prompt(self, phase: CIAPhase, phase_dir: str, title_pattern: str) -> Optional[PromptMetadata]:
        """Load a specific phase prompt from its directory.
        
        Args:
            phase: The CIA phase identifier
            phase_dir: The directory name (e.g., "Phase 1")
            title_pattern: Pattern to match in the filename
            
        Returns:
            PromptMetadata if found, None otherwise
        """
        phase_path = self.prompts_base_dir / phase_dir
        if not phase_path.exists():
            return None
        
        # Find the matching file
        for file_path in phase_path.glob("*.md"):
            filename = file_path.stem  # Remove .md extension
            
            # Check if filename contains the title pattern
            if title_pattern.lower() in filename.lower():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Determine if it's an archive phase
                    is_archive = "Archive" in filename or phase.value.endswith("EB")
                    
                    return PromptMetadata(
                        phase=phase.value,
                        title=filename,
                        file_path=file_path,
                        is_archive=is_archive,
                        content=content
                    )
                except Exception as e:
                    logger.error(f"Failed to read {file_path}: {e}")
        
        return None
    
    def get_prompt(self, phase: CIAPhase) -> Optional[str]:
        """Get the prompt content for a specific phase.
        
        Args:
            phase: The CIA phase to get prompt for
            
        Returns:
            The prompt content, or None if not found
        """
        if not self._loaded:
            self.load_all_prompts()
        
        metadata = self._prompts_cache.get(phase)
        if metadata:
            return metadata.content
        return None
    
    def get_prompt_with_substitutions(
        self, 
        phase: CIAPhase,
        company_name: str,
        company_url: str,
        kpoi: str,
        country: str,
        testimonials_url: Optional[str] = None,
        **additional_vars
    ) -> Optional[str]:
        """Get prompt with variable substitutions applied.
        
        Args:
            phase: The CIA phase
            company_name: Company name to substitute
            company_url: Company URL to substitute
            kpoi: Key Person of Influence name
            country: Country name
            testimonials_url: Optional testimonials URL
            **additional_vars: Any additional variables to substitute
            
        Returns:
            The prompt with substitutions applied, or None if not found
        """
        prompt = self.get_prompt(phase)
        if not prompt:
            return None
        
        # Common substitutions
        substitutions = {
            "{COMPANY_NAME}": company_name,
            "{COMPANY_URL}": company_url,
            "{URL}": company_url,  # Some prompts use {URL}
            "{KPOI}": kpoi,
            "{COUNTRY}": country,
            "{TESTIMONIALS_URL}": testimonials_url or company_url + "/testimonials",
        }
        
        # Add any additional variables
        for key, value in additional_vars.items():
            substitutions[f"{{{key.upper()}}}"] = str(value)
        
        # Apply substitutions
        for placeholder, value in substitutions.items():
            prompt = prompt.replace(placeholder, value)
        
        return prompt
    
    def get_all_phases(self) -> List[CIAPhase]:
        """Get all phases that have prompts loaded.
        
        Returns:
            List of CIA phases with available prompts
        """
        if not self._loaded:
            self.load_all_prompts()
        
        return list(self._prompts_cache.keys())
    
    def get_prompt_metadata(self, phase: CIAPhase) -> Optional[PromptMetadata]:
        """Get metadata about a prompt.
        
        Args:
            phase: The CIA phase
            
        Returns:
            PromptMetadata or None if not found
        """
        if not self._loaded:
            self.load_all_prompts()
        
        return self._prompts_cache.get(phase)
    
    def estimate_tokens(self, prompt: str) -> int:
        """Estimate token count for a prompt.
        
        This is a rough estimate - actual token count may vary.
        
        Args:
            prompt: The prompt text
            
        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token
        return len(prompt) // 4
    
    def compress_prompt(self, prompt: str) -> str:
        """Apply compression techniques to reduce prompt size.
        
        This implements the 70-85% compression mentioned in requirements.
        
        Args:
            prompt: Original prompt text
            
        Returns:
            Compressed prompt
        """
        # Remove excessive whitespace
        compressed = re.sub(r'\n\s*\n\s*\n', '\n\n', prompt)
        compressed = re.sub(r'[ \t]+', ' ', compressed)
        
        # Remove markdown formatting that doesn't affect meaning
        compressed = re.sub(r'\*\*(.*?)\*\*', r'\1', compressed)  # Bold
        compressed = re.sub(r'__(.*?)__', r'\1', compressed)      # Underline
        
        # Compress common phrases
        replacements = {
            "Please analyze": "Analyze",
            "Please provide": "Provide",
            "Please ensure": "Ensure",
            "Make sure to": "Must",
            "It is important to": "Must",
            "You should": "Must",
            "in order to": "to",
            "as well as": "and",
            "in addition to": "plus",
        }
        
        for old, new in replacements.items():
            compressed = compressed.replace(old, new)
            compressed = compressed.replace(old.lower(), new.lower())
        
        # Log compression ratio
        original_len = len(prompt)
        compressed_len = len(compressed)
        ratio = (1 - compressed_len / original_len) * 100
        logger.debug(f"Compressed prompt by {ratio:.1f}% ({original_len} -> {compressed_len} chars)")
        
        return compressed
    
    def reload_prompts(self) -> None:
        """Force reload all prompts from disk."""
        self._prompts_cache.clear()
        self._loaded = False
        self.load_all_prompts()


# Global loader instance
_loader: Optional[CompressedPromptsLoader] = None


def get_prompts_loader() -> CompressedPromptsLoader:
    """Get the global prompts loader instance.
    
    Returns:
        The CompressedPromptsLoader singleton
    """
    global _loader
    if _loader is None:
        _loader = CompressedPromptsLoader()
    return _loader