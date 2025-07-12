"""
Constants for Brand BOS CIA System.
Defines CIA phases, framework requirements, and system constants.
"""

from enum import Enum
from typing import Dict, List, Tuple


class CIAPhase(str, Enum):
    """CIA System phase identifiers."""
    # Phase 1: Foundational Intelligence
    PHASE_1A = "1A"  # Foundational Business Intelligence
    PHASE_1B = "1B"  # DNA Research & ICP Discovery
    PHASE_1C = "1C"  # Key Person of Influence Assessment
    PHASE_1D = "1D"  # Competitive Intelligence
    PHASE_1EB = "1EB"  # Master Business Intelligence Archive
    
    # Phase 2: SEO & Social Intelligence
    PHASE_2A = "2A"  # SEO Intelligence Analysis (DataForSEO)
    PHASE_2B = "2B"  # Social Intelligence Analysis
    PHASE_2EB = "2EB"  # SEO + Social Intelligence Archive
    
    # Phase 3: Strategic Synthesis
    PHASE_3A = "3A"  # X.com Trend Data Analysis (Perplexity)
    PHASE_3B = "3B"  # Testimonials Analysis
    PHASE_3C = "3C"  # Comprehensive Strategic Synthesis
    PHASE_3EB = "3EB"  # Advanced Intelligence Archive
    
    # Phase 4-6: Implementation
    PHASE_4A = "4A"  # Golden Hippo Offer Development
    PHASE_5A = "5A"  # Content Strategy Development
    PHASE_6A = "6A"  # Implementation Planning


class PhaseStatus(str, Enum):
    """Status of CIA phase execution."""
    PENDING = "pending"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    HANDOVER_REQUIRED = "handover_required"


class HumanLoopType(str, Enum):
    """Types of human-in-loop interventions."""
    DATAFORSEO_KEYWORDS = "dataforseo_keywords"
    PERPLEXITY_TRENDS = "perplexity_trends"
    TESTIMONIALS_REQUEST = "testimonials_request"
    CONTEXT_HANDOVER = "context_handover"


class NotificationType(str, Enum):
    """Types of notifications sent."""
    PHASE_STARTED = "phase_started"
    PHASE_COMPLETED = "phase_completed"
    HUMAN_INPUT_REQUIRED = "human_input_required"
    ERROR_OCCURRED = "error_occurred"
    HANDOVER_CREATED = "handover_created"


# CIA Phase Configuration
CIA_PHASE_CONFIG: Dict[CIAPhase, Dict[str, any]] = {
    CIAPhase.PHASE_1A: {
        "name": "Foundational Business Intelligence",
        "description": "Extract core business model, value propositions, and market positioning",
        "requires_human_input": False,
        "creates_archive": False,
        "estimated_tokens": 8000,
    },
    CIAPhase.PHASE_1B: {
        "name": "DNA Research & ICP Discovery",
        "description": "Deep dive into customer psychology and ideal client profiles",
        "requires_human_input": False,
        "creates_archive": False,
        "estimated_tokens": 10000,
    },
    CIAPhase.PHASE_1C: {
        "name": "Key Person of Influence Assessment",
        "description": "Analyze authority positioning using Priestley's 5 P's framework",
        "requires_human_input": False,
        "creates_archive": False,
        "estimated_tokens": 8000,
    },
    CIAPhase.PHASE_1D: {
        "name": "Competitive Intelligence",
        "description": "Analyze competitive landscape and differentiation opportunities",
        "requires_human_input": False,
        "creates_archive": False,
        "estimated_tokens": 10000,
    },
    CIAPhase.PHASE_1EB: {
        "name": "Master Business Intelligence Archive",
        "description": "Synthesize Phase 1 intelligence into comprehensive archive",
        "requires_human_input": False,
        "creates_archive": True,
        "estimated_tokens": 5000,
    },
    CIAPhase.PHASE_2A: {
        "name": "SEO Intelligence Analysis",
        "description": "Extract keywords for DataForSEO lookup and SERP analysis",
        "requires_human_input": True,
        "human_input_type": HumanLoopType.DATAFORSEO_KEYWORDS,
        "creates_archive": False,
        "estimated_tokens": 8000,
    },
    CIAPhase.PHASE_2B: {
        "name": "Social Intelligence Analysis",
        "description": "Analyze social media presence and engagement patterns",
        "requires_human_input": False,
        "creates_archive": False,
        "estimated_tokens": 10000,
    },
    CIAPhase.PHASE_2EB: {
        "name": "SEO + Social Intelligence Archive",
        "description": "Synthesize digital presence intelligence",
        "requires_human_input": False,
        "creates_archive": True,
        "estimated_tokens": 5000,
    },
    CIAPhase.PHASE_3A: {
        "name": "X.com Trend Data Analysis",
        "description": "Research trending topics and viral content patterns",
        "requires_human_input": True,
        "human_input_type": HumanLoopType.PERPLEXITY_TRENDS,
        "creates_archive": False,
        "estimated_tokens": 8000,
    },
    CIAPhase.PHASE_3B: {
        "name": "Testimonials Analysis",
        "description": "Extract and analyze customer testimonials and success stories",
        "requires_human_input": False,  # May require if insufficient data
        "creates_archive": False,
        "estimated_tokens": 8000,
    },
    CIAPhase.PHASE_3C: {
        "name": "Comprehensive Strategic Synthesis",
        "description": "Create unified strategic intelligence from all previous phases",
        "requires_human_input": False,
        "creates_archive": False,
        "estimated_tokens": 12000,
    },
    CIAPhase.PHASE_3EB: {
        "name": "Advanced Intelligence Archive",
        "description": "Final comprehensive intelligence synthesis",
        "requires_human_input": False,
        "creates_archive": True,
        "estimated_tokens": 5000,
    },
    CIAPhase.PHASE_4A: {
        "name": "Golden Hippo Offer Development",
        "description": "Develop compelling offers using Golden Hippo methodology",
        "requires_human_input": False,
        "creates_archive": True,
        "estimated_tokens": 10000,
    },
    CIAPhase.PHASE_5A: {
        "name": "Content Strategy Development",
        "description": "Create comprehensive content strategy and editorial calendar",
        "requires_human_input": False,
        "creates_archive": True,
        "estimated_tokens": 12000,
    },
    CIAPhase.PHASE_6A: {
        "name": "Implementation Planning",
        "description": "Detailed implementation roadmap with timelines and priorities",
        "requires_human_input": False,
        "creates_archive": True,
        "estimated_tokens": 10000,
    },
}

# Phase execution order
CIA_PHASE_ORDER: List[CIAPhase] = [
    CIAPhase.PHASE_1A,
    CIAPhase.PHASE_1B,
    CIAPhase.PHASE_1C,
    CIAPhase.PHASE_1D,
    CIAPhase.PHASE_1EB,
    CIAPhase.PHASE_2A,
    CIAPhase.PHASE_2B,
    CIAPhase.PHASE_2EB,
    CIAPhase.PHASE_3A,
    CIAPhase.PHASE_3B,
    CIAPhase.PHASE_3C,
    CIAPhase.PHASE_3EB,
    CIAPhase.PHASE_4A,
    CIAPhase.PHASE_5A,
    CIAPhase.PHASE_6A,
]

# Phases that create Master Archives
ARCHIVE_PHASES: List[CIAPhase] = [
    CIAPhase.PHASE_1EB,
    CIAPhase.PHASE_2EB,
    CIAPhase.PHASE_3EB,
    CIAPhase.PHASE_4A,
    CIAPhase.PHASE_5A,
    CIAPhase.PHASE_6A,
]

# Phases requiring human input
HUMAN_INPUT_PHASES: List[CIAPhase] = [
    CIAPhase.PHASE_2A,  # DataForSEO
    CIAPhase.PHASE_3A,  # Perplexity
]

# Framework preservation requirements
FRAMEWORK_REQUIREMENTS = {
    "benson_points": list(range(1, 78)),  # Points 1-77+
    "frank_kern": [
        "narrative_structure",
        "customer_journey",
        "transformation_story",
        "belief_shifting",
        "value_ladder",
    ],
    "priestley_5ps": [
        "pitch",
        "publish",
        "product",
        "profile",
        "partnership",
    ],
    "golden_hippo": [
        "offer_structure",
        "value_stacking",
        "urgency_creation",
        "risk_reversal",
        "social_proof",
    ],
}

# Token estimation factors
TOKEN_COMPRESSION_RATIO = 0.75  # Target 70-85% compression
CONTEXT_WINDOW_SIZE = 200000  # Claude's context window
HANDOVER_THRESHOLD = 0.70  # Create handover at 70% usage

# Retry configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2
INITIAL_RETRY_DELAY = 5  # seconds

# Performance thresholds
MAX_PHASE_DURATION_SECONDS = 180  # 3 minutes
HUMAN_LOOP_TIMEOUT_SECONDS = 1800  # 30 minutes
API_TIMEOUT_SECONDS = 30

# Database table names
TABLE_CIA_SESSIONS = "cia_sessions"
TABLE_PHASE_RESPONSES = "phase_responses"
TABLE_MASTER_ARCHIVES = "master_archives"
TABLE_HUMAN_LOOP_STATES = "human_loop_states"
TABLE_CONTEXT_HANDOVERS = "context_handovers"

# Notification templates
NOTIFICATION_TEMPLATES = {
    "dataforseo_required": {
        "title": "🔍 CIA Phase 2A: DataForSEO Lookup Required",
        "color": "warning",
        "icon": ":mag:",
    },
    "perplexity_required": {
        "title": "📈 CIA Phase 3A: Perplexity Research Required",
        "color": "good",
        "icon": ":chart_with_upwards_trend:",
    },
    "testimonials_required": {
        "title": "💬 CIA Phase 3B: Testimonials Needed",
        "color": "#36a64f",
        "icon": ":speech_balloon:",
    },
    "handover_created": {
        "title": "🔄 Context Handover Created",
        "color": "danger",
        "icon": ":arrows_counterclockwise:",
    },
}