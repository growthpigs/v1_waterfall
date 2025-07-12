"""
Anthropic Claude API client for CIA system.
Handles API calls with retry logic and token tracking.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json

import anthropic
from anthropic import AsyncAnthropic, APIError, APITimeoutError, RateLimitError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from ...config.settings import settings
from ...config.constants import (
    MAX_RETRY_ATTEMPTS,
    RETRY_BACKOFF_FACTOR,
    INITIAL_RETRY_DELAY,
    API_TIMEOUT_SECONDS
)

logger = logging.getLogger(__name__)


class ClaudeAPIError(Exception):
    """Custom exception for Claude API errors."""
    pass


class TokenUsage:
    """Track token usage from API responses."""
    
    def __init__(self, input_tokens: int = 0, output_tokens: int = 0):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = input_tokens + output_tokens
    
    def __add__(self, other: 'TokenUsage') -> 'TokenUsage':
        """Add two TokenUsage instances."""
        return TokenUsage(
            self.input_tokens + other.input_tokens,
            self.output_tokens + other.output_tokens
        )
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {
            "prompt_tokens": self.input_tokens,
            "response_tokens": self.output_tokens,
            "total_tokens": self.total_tokens
        }


class ClaudeClient:
    """Anthropic Claude API client with retry logic and token tracking."""
    
    # Model selection based on requirements
    MODEL_CLAUDE_3_OPUS = "claude-3-opus-20240229"
    MODEL_CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    MODEL_CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    
    # Default to Opus for highest quality intelligence analysis
    DEFAULT_MODEL = MODEL_CLAUDE_3_OPUS
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = MAX_RETRY_ATTEMPTS
    ):
        """Initialize Claude client.
        
        Args:
            api_key: Anthropic API key. If None, uses settings.
            model: Model to use. If None, uses DEFAULT_MODEL.
            max_retries: Maximum retry attempts
        """
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or self.DEFAULT_MODEL
        self.max_retries = max_retries
        
        # Initialize async client
        self.client = AsyncAnthropic(
            api_key=self.api_key,
            timeout=API_TIMEOUT_SECONDS,
            max_retries=0  # We handle retries ourselves
        )
        
        # Track usage statistics
        self._total_usage = TokenUsage()
        self._call_count = 0
        self._error_count = 0
    
    @retry(
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=RETRY_BACKOFF_FACTOR,
            min=INITIAL_RETRY_DELAY,
            max=60
        ),
        retry=retry_if_exception_type((APITimeoutError, RateLimitError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def complete(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        stop_sequences: Optional[List[str]] = None
    ) -> Tuple[str, TokenUsage]:
        """Send a completion request to Claude.
        
        Args:
            prompt: The prompt text
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            system_prompt: Optional system prompt
            stop_sequences: Optional stop sequences
            
        Returns:
            Tuple of (response text, token usage)
            
        Raises:
            ClaudeAPIError: On API errors
        """
        try:
            self._call_count += 1
            
            # Build messages
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Make API call
            start_time = datetime.utcnow()
            
            response = await self.client.messages.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                stop_sequences=stop_sequences
            )
            
            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Extract response text
            response_text = ""
            if response.content:
                for content in response.content:
                    if hasattr(content, 'text'):
                        response_text += content.text
            
            # Track token usage
            usage = TokenUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens
            )
            self._total_usage += usage
            
            logger.info(
                f"Claude API call completed in {duration:.2f}s "
                f"(model: {self.model}, tokens: {usage.total_tokens})"
            )
            
            return response_text, usage
            
        except RateLimitError as e:
            self._error_count += 1
            logger.error(f"Rate limit error: {e}")
            raise
            
        except APITimeoutError as e:
            self._error_count += 1
            logger.error(f"API timeout error: {e}")
            raise
            
        except APIError as e:
            self._error_count += 1
            logger.error(f"API error: {e}")
            raise ClaudeAPIError(f"Claude API error: {str(e)}") from e
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"Unexpected error: {e}")
            raise ClaudeAPIError(f"Unexpected error: {str(e)}") from e
    
    async def complete_with_context(
        self,
        prompt: str,
        context: Dict[str, Any],
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> Tuple[str, TokenUsage, Dict[str, Any]]:
        """Complete with additional context for CIA analysis.
        
        Args:
            prompt: The prompt text
            context: CIA context (previous archives, frameworks, etc.)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Tuple of (response text, token usage, extracted data)
        """
        # Build system prompt with context
        system_prompt = self._build_system_prompt(context)
        
        # Add context to user prompt if needed
        enhanced_prompt = self._enhance_prompt_with_context(prompt, context)
        
        # Get completion
        response_text, usage = await self.complete(
            prompt=enhanced_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt
        )
        
        # Extract structured data from response
        extracted_data = self._extract_structured_data(response_text, context)
        
        return response_text, usage, extracted_data
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt with CIA context.
        
        Args:
            context: CIA context dictionary
            
        Returns:
            System prompt string
        """
        system_parts = [
            "You are an expert business intelligence analyst conducting CIA (Central Intelligence Arsenal) analysis.",
            "You must preserve and build upon all customer psychology frameworks including:",
            "- Benson Points 1-77+ for comprehensive customer psychology",
            "- Frank Kern methodology for narrative-driven customer journey",
            "- Daniel Priestley's 5 P's (Pitch, Publish, Product, Profile, Partnership)",
            "- Golden Hippo methodology for offer development"
        ]
        
        # Add phase-specific instructions
        if "current_phase" in context:
            phase = context["current_phase"]
            system_parts.append(f"\nCurrently executing: {phase}")
        
        # Add framework preservation reminders
        if "previous_archives" in context and context["previous_archives"]:
            system_parts.append(
                "\nBuild upon the intelligence from previous phases. "
                "Do not lose any insights - accumulate and synthesize."
            )
        
        return "\n".join(system_parts)
    
    def _enhance_prompt_with_context(self, prompt: str, context: Dict[str, Any]) -> str:
        """Enhance prompt with relevant context.
        
        Args:
            prompt: Original prompt
            context: CIA context
            
        Returns:
            Enhanced prompt
        """
        # If we have previous archives, add a summary
        if "previous_archives" in context and context["previous_archives"]:
            archives_summary = "\n\nPREVIOUS INTELLIGENCE SUMMARY:\n"
            for archive in context["previous_archives"][-3:]:  # Last 3 archives
                if isinstance(archive, dict):
                    archives_summary += f"- {archive.get('phase', 'Unknown')}: "
                    archives_summary += f"{archive.get('summary', 'No summary')}\n"
            
            prompt = prompt + archives_summary
        
        return prompt
    
    def _extract_structured_data(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from response.
        
        Args:
            response: Claude's response text
            context: CIA context
            
        Returns:
            Dictionary of extracted data
        """
        extracted = {
            "raw_response": response,
            "frameworks_mentioned": [],
            "key_insights": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check for framework mentions
        framework_keywords = {
            "benson": ["Benson", "customer psychology", "pain points", "desires"],
            "kern": ["Frank Kern", "customer journey", "narrative", "transformation"],
            "priestley": ["Priestley", "5 P's", "5 Ps", "Pitch", "Publish", "Product", "Profile", "Partnership"],
            "golden_hippo": ["Golden Hippo", "offer", "value stack", "urgency"]
        }
        
        response_lower = response.lower()
        for framework, keywords in framework_keywords.items():
            if any(keyword.lower() in response_lower for keyword in keywords):
                extracted["frameworks_mentioned"].append(framework)
        
        # Extract sections if response is structured
        sections = self._extract_sections(response)
        if sections:
            extracted["sections"] = sections
        
        return extracted
    
    def _extract_sections(self, response: str) -> Dict[str, str]:
        """Extract sections from a structured response.
        
        Args:
            response: Response text
            
        Returns:
            Dictionary of section_name -> content
        """
        sections = {}
        current_section = None
        current_content = []
        
        for line in response.split('\n'):
            # Check if line is a section header (e.g., "## Section Name" or "**Section Name:**")
            if line.startswith('##') or (line.startswith('**') and line.endswith(':**')):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.strip('#* :')
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics.
        
        Returns:
            Dictionary of usage stats
        """
        return {
            "total_calls": self._call_count,
            "total_errors": self._error_count,
            "total_tokens": self._total_usage.total_tokens,
            "input_tokens": self._total_usage.input_tokens,
            "output_tokens": self._total_usage.output_tokens,
            "error_rate": self._error_count / self._call_count if self._call_count > 0 else 0,
            "model": self.model
        }
    
    def reset_stats(self) -> None:
        """Reset usage statistics."""
        self._total_usage = TokenUsage()
        self._call_count = 0
        self._error_count = 0
    
    async def close(self) -> None:
        """Close the client connection."""
        await self.client.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Singleton instance
_claude_client: Optional[ClaudeClient] = None


def get_claude_client(model: Optional[str] = None) -> ClaudeClient:
    """Get or create Claude client singleton.
    
    Args:
        model: Optional model override
        
    Returns:
        ClaudeClient instance
    """
    global _claude_client
    if _claude_client is None or (model and model != _claude_client.model):
        _claude_client = ClaudeClient(model=model)
    return _claude_client