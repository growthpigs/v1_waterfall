"""
Example: CIA Phase Structure and Context Management
Shows patterns for executing CIA phases with context monitoring and Master Archive synthesis.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import time

class PhaseStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing" 
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class MasterArchive:
    """Synthesized intelligence from completed phases"""
    phase_number: str
    intelligence_summary: Dict[str, Any]
    customer_psychology: Dict[str, Any]  # Benson points 1-77+
    competitive_analysis: Dict[str, Any]
    authority_positioning: Dict[str, Any]  # Priestley 5 P's
    content_strategy: Dict[str, Any]
    created_at: str
    context_tokens_used: int

@dataclass
class PhaseResult:
    """Result from individual phase execution"""
    phase_id: str
    status: PhaseStatus
    response: Dict[str, Any]
    master_archive: Optional[MasterArchive]
    context_usage: float  # Percentage of context window used
    requires_human_input: bool = False
    human_input_type: Optional[str] = None

class ContextMonitor:
    """Monitor context window usage and create handovers"""
    
    def __init__(self, limit_threshold: float = 0.70):
        self.limit_threshold = limit_threshold
        self.current_usage = 0.0
    
    def check_usage(self) -> float:
        """Check current context window usage"""
        # Implementation would integrate with actual token counting
        return self.current_usage
    
    def needs_handover(self) -> bool:
        """Check if handover is needed"""
        return self.check_usage() > self.limit_threshold
    
    async def create_handover(self, session_id: str, current_phase: str) -> Dict[str, Any]:
        """Create handover document for session continuity"""
        return {
            "session_id": session_id,
            "current_phase": current_phase,
            "context_usage": self.current_usage,
            "completed_phases": await self.get_completed_phases(session_id),
            "next_action": f"Resume from {current_phase}",
            "critical_state": await self.serialize_session_state(session_id),
            "created_at": time.time()
        }

class CIAPhaseEngine:
    """Core engine for executing CIA 6-phase analysis"""
    
    def __init__(self):
        self.context_monitor = ContextMonitor()
        self.phases = {
            "1A": "Foundational Business Intelligence",
            "1B": "DNA Research & ICP Discovery", 
            "1C": "Key Person of Influence Assessment",
            "1D": "Competitive Intelligence",
            "1EB": "Master Business Intelligence Archive",
            "2A": "SEO Intelligence Analysis",
            "2B": "Social Intelligence Analysis", 
            "2EB": "SEO + Social Intelligence Archive",
            "3A": "X.com Trend Data Analysis",
            "3B": "Testimonials Analysis",
            "3C": "Comprehensive Strategic Synthesis",
            "3EB": "Advanced Intelligence Archive",
            "4A": "Golden Hippo Offer Development",
            "5A": "Content Strategy Development", 
            "6A": "Implementation Planning"
        }
    
    async def execute_phase(
        self, 
        phase_id: str, 
        session_id: str, 
        previous_archives: List[MasterArchive],
        url: str,
        company_name: str
    ) -> PhaseResult:
        """Execute a single CIA phase with context management"""
        
        # Check context usage before starting
        if self.context_monitor.needs_handover():
            handover = await self.context_monitor.create_handover(session_id, phase_id)
            raise ContextLimitReached(f"Context limit reached. Handover created: {handover}")
        
        # Load compressed prompt for this phase
        prompt = await self.load_compressed_prompt(phase_id)
        
        # Build context with all previous intelligence
        analysis_context = self.build_phase_context(
            prompt=prompt,
            previous_archives=previous_archives,
            url=url,
            company_name=company_name
        )
        
        # Handle human-in-loop workflows
        if phase_id == "2A":  # SEO Intelligence requires DataForSEO
            return await self.handle_dataforseo_workflow(session_id, analysis_context)
        elif phase_id == "3A":  # Trend analysis requires Perplexity
            return await self.handle_perplexity_workflow(session_id, analysis_context)
        elif phase_id == "3B":  # Testimonials may require human input
            return await self.handle_testimonials_workflow(session_id, analysis_context)
        
        # Execute standard phase analysis
        response = await self.execute_claude_analysis(analysis_context)
        
        # Create Master Archive if this is a phase boundary
        master_archive = None
        if self.is_phase_boundary(phase_id):
            master_archive = await self.synthesize_master_archive(
                session_id, phase_id, response, previous_archives
            )
        
        return PhaseResult(
            phase_id=phase_id,
            status=PhaseStatus.COMPLETED,
            response=response,
            master_archive=master_archive,
            context_usage=self.context_monitor.check_usage()
        )
    
    async def handle_dataforseo_workflow(self, session_id: str, context: Dict) -> PhaseResult:
        """Handle Phase 2A with DataForSEO integration"""
        # Extract keywords for DataForSEO lookup
        keywords = await self.extract_keywords_for_dataforseo(context)
        
        # Send human-in-loop notification
        await self.send_human_notification(
            session_id=session_id,
            notification_type="dataforseo_keywords",
            data={"keywords": keywords},
            message=f"Phase 2A requires DataForSEO lookup for keywords: {', '.join(keywords)}"
        )
        
        return PhaseResult(
            phase_id="2A",
            status=PhaseStatus.PAUSED,
            response={"keywords_extracted": keywords},
            master_archive=None,
            context_usage=self.context_monitor.check_usage(),
            requires_human_input=True,
            human_input_type="dataforseo_results"
        )
    
    async def synthesize_master_archive(
        self, 
        session_id: str, 
        phase_id: str, 
        current_response: Dict,
        previous_archives: List[MasterArchive]
    ) -> MasterArchive:
        """Synthesize Master Archive preserving all intelligence frameworks"""
        
        # Extract customer psychology (Benson points 1-77+)
        customer_psychology = self.extract_customer_psychology(current_response, previous_archives)
        
        # Extract competitive intelligence
        competitive_analysis = self.extract_competitive_intelligence(current_response, previous_archives)
        
        # Extract authority positioning (Priestley 5 P's)
        authority_positioning = self.extract_authority_positioning(current_response, previous_archives)
        
        # Create comprehensive intelligence summary
        intelligence_summary = {
            "phase_synthesis": current_response,
            "accumulated_insights": self.accumulate_insights(previous_archives),
            "strategic_opportunities": self.identify_opportunities(current_response, previous_archives),
            "implementation_priorities": self.prioritize_actions(current_response, previous_archives)
        }
        
        return MasterArchive(
            phase_number=phase_id,
            intelligence_summary=intelligence_summary,
            customer_psychology=customer_psychology,
            competitive_analysis=competitive_analysis,
            authority_positioning=authority_positioning,
            content_strategy=self.extract_content_strategy(current_response, previous_archives),
            created_at=time.time(),
            context_tokens_used=int(self.context_monitor.check_usage() * 1000)  # Approximate
        )
    
    def build_phase_context(
        self, 
        prompt: str, 
        previous_archives: List[MasterArchive],
        url: str,
        company_name: str
    ) -> Dict[str, Any]:
        """Build comprehensive context for phase execution"""
        return {
            "prompt": prompt,
            "company_url": url,
            "company_name": company_name,
            "previous_intelligence": [archive.intelligence_summary for archive in previous_archives],
            "customer_psychology_chain": [archive.customer_psychology for archive in previous_archives],
            "competitive_intelligence_chain": [archive.competitive_analysis for archive in previous_archives],
            "authority_framework_chain": [archive.authority_positioning for archive in previous_archives],
            "execution_timestamp": time.time()
        }
    
    def is_phase_boundary(self, phase_id: str) -> bool:
        """Check if phase requires Master Archive creation"""
        boundary_phases = ["1EB", "2EB", "3EB", "4A", "5A", "6A"]
        return phase_id in boundary_phases

class ContextLimitReached(Exception):
    """Raised when context window approaches limit"""
    pass

# Example usage pattern:
async def run_cia_analysis(url: str, company_name: str, session_id: str):
    """Example of complete CIA analysis execution"""
    engine = CIAPhaseEngine()
    previous_archives = []
    
    # Phase 1: Foundational Intelligence
    phase_1_phases = ["1A", "1B", "1C", "1D", "1EB"]
    for phase_id in phase_1_phases:
        try:
            result = await engine.execute_phase(phase_id, session_id, previous_archives, url, company_name)
            if result.master_archive:
                previous_archives.append(result.master_archive)
                
            if result.requires_human_input:
                # Handle human-in-loop workflow
                await handle_human_input_workflow(session_id, result.human_input_type)
                
        except ContextLimitReached as e:
            # Create handover and pause execution
            print(f"Context limit reached: {e}")
            break
    
    return previous_archives