"""
Master Archive Builder for CIA system.
Synthesizes intelligence and preserves frameworks between phases.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..config.constants import CIAPhase, ARCHIVE_PHASES, FRAMEWORK_REQUIREMENTS
from ..database.models import PhaseResponse, MasterArchive

logger = logging.getLogger(__name__)


class MasterArchiveBuilder:
    """Builds master archives from phase responses with framework preservation."""
    
    def build_archive(
        self,
        phase: CIAPhase,
        phase_responses: List[PhaseResponse],
        previous_archives: List[MasterArchive]
    ) -> Dict[str, Any]:
        """Build a master archive from phase responses.
        
        Args:
            phase: The phase triggering archive creation
            phase_responses: All phase responses to synthesize
            previous_archives: Previous archives for continuity
            
        Returns:
            Dictionary with intelligence and frameworks
        """
        logger.info(f"Building master archive for phase {phase}")
        
        # Extract intelligence from responses
        intelligence = self._synthesize_intelligence(phase, phase_responses, previous_archives)
        
        # Extract and preserve frameworks
        frameworks = self._extract_frameworks(phase_responses, previous_archives)
        
        # Validate framework preservation
        validation = self._validate_frameworks(frameworks)
        
        return {
            "intelligence": intelligence,
            "frameworks": frameworks,
            "validation": validation,
            "metadata": {
                "phase": phase.value,
                "responses_processed": len(phase_responses),
                "archives_referenced": len(previous_archives),
                "created_at": datetime.utcnow().isoformat()
            }
        }
    
    def _synthesize_intelligence(
        self,
        phase: CIAPhase,
        responses: List[PhaseResponse],
        archives: List[MasterArchive]
    ) -> Dict[str, Any]:
        """Synthesize intelligence from phase responses.
        
        Args:
            phase: Current phase
            responses: Phase responses to synthesize
            archives: Previous archives for context
            
        Returns:
            Synthesized intelligence dictionary
        """
        intelligence = {
            "phase_synthesis": {},
            "accumulated_insights": [],
            "strategic_opportunities": [],
            "implementation_priorities": []
        }
        
        # Get phase-specific synthesis
        if phase == CIAPhase.PHASE_1EB:
            intelligence["phase_synthesis"] = self._synthesize_phase_1(responses)
        elif phase == CIAPhase.PHASE_2EB:
            intelligence["phase_synthesis"] = self._synthesize_phase_2(responses)
        elif phase == CIAPhase.PHASE_3EB:
            intelligence["phase_synthesis"] = self._synthesize_phase_3(responses)
        elif phase == CIAPhase.PHASE_4A:
            intelligence["phase_synthesis"] = self._synthesize_phase_4(responses)
        elif phase == CIAPhase.PHASE_5A:
            intelligence["phase_synthesis"] = self._synthesize_phase_5(responses)
        elif phase == CIAPhase.PHASE_6A:
            intelligence["phase_synthesis"] = self._synthesize_phase_6(responses)
        
        # Accumulate insights from all responses
        for response in responses:
            if "extracted" in response.response_content:
                extracted = response.response_content["extracted"]
                if "key_insights" in extracted:
                    intelligence["accumulated_insights"].extend(extracted["key_insights"])
        
        # Accumulate from previous archives
        for archive in archives:
            if archive.intelligence_summary.get("accumulated_insights"):
                intelligence["accumulated_insights"].extend(
                    archive.intelligence_summary["accumulated_insights"]
                )
        
        # Deduplicate insights
        intelligence["accumulated_insights"] = list(set(intelligence["accumulated_insights"]))
        
        # Extract opportunities and priorities
        intelligence["strategic_opportunities"] = self._extract_opportunities(responses, archives)
        intelligence["implementation_priorities"] = self._extract_priorities(responses, archives)
        
        return intelligence
    
    def _extract_frameworks(
        self,
        responses: List[PhaseResponse],
        archives: List[MasterArchive]
    ) -> Dict[str, Any]:
        """Extract and preserve customer psychology frameworks.
        
        Args:
            responses: Phase responses
            archives: Previous archives
            
        Returns:
            Dictionary of preserved frameworks
        """
        frameworks = {
            "customer_psychology": {},
            "competitive_analysis": {},
            "authority_positioning": {},
            "content_strategy": {}
        }
        
        # Start with previous archive frameworks
        if archives:
            latest_archive = archives[-1]
            frameworks["customer_psychology"] = dict(latest_archive.customer_psychology)
            frameworks["competitive_analysis"] = dict(latest_archive.competitive_analysis)
            frameworks["authority_positioning"] = dict(latest_archive.authority_positioning)
            frameworks["content_strategy"] = dict(latest_archive.content_strategy)
        
        # Extract from phase responses
        for response in responses:
            extracted = response.extracted_frameworks
            
            # Benson customer psychology
            if "benson" in extracted:
                self._merge_benson_points(frameworks["customer_psychology"], extracted["benson"])
            
            # Frank Kern methodology
            if "frank_kern" in extracted:
                self._merge_frank_kern(frameworks["customer_psychology"], extracted["frank_kern"])
            
            # Priestley 5 P's
            if "priestley" in extracted:
                self._merge_priestley(frameworks["authority_positioning"], extracted["priestley"])
            
            # Golden Hippo
            if "golden_hippo" in extracted:
                self._merge_golden_hippo(frameworks["content_strategy"], extracted["golden_hippo"])
            
            # Competitive intelligence
            if "competitors" in extracted:
                self._merge_competitive(frameworks["competitive_analysis"], extracted["competitors"])
        
        return frameworks
    
    def _merge_benson_points(self, existing: Dict, new_data: Dict) -> None:
        """Merge Benson customer psychology points.
        
        Args:
            existing: Existing framework data
            new_data: New data to merge
        """
        # Ensure all required categories exist
        for category in ["pain_points", "desires", "beliefs", "values", "behaviors"]:
            if category not in existing:
                existing[category] = []
            
            if category in new_data:
                # Merge lists, avoiding duplicates
                existing[category].extend(new_data[category])
                existing[category] = list(set(existing[category]))
    
    def _merge_frank_kern(self, existing: Dict, new_data: Dict) -> None:
        """Merge Frank Kern methodology elements.
        
        Args:
            existing: Existing framework data
            new_data: New data to merge
        """
        kern_elements = ["narrative_structure", "customer_journey", "transformation_story", 
                        "belief_shifting", "value_ladder"]
        
        for element in kern_elements:
            if element in new_data:
                existing[f"kern_{element}"] = new_data[element]
    
    def _merge_priestley(self, existing: Dict, new_data: Dict) -> None:
        """Merge Priestley 5 P's framework.
        
        Args:
            existing: Existing framework data
            new_data: New data to merge
        """
        for p in ["pitch", "publish", "product", "profile", "partnership"]:
            if p in new_data:
                existing[p] = new_data[p]
    
    def _merge_golden_hippo(self, existing: Dict, new_data: Dict) -> None:
        """Merge Golden Hippo methodology.
        
        Args:
            existing: Existing framework data
            new_data: New data to merge
        """
        hippo_elements = ["offer_structure", "value_stacking", "urgency_creation", 
                         "risk_reversal", "social_proof"]
        
        for element in hippo_elements:
            if element in new_data:
                existing[element] = new_data[element]
    
    def _merge_competitive(self, existing: Dict, new_data: Dict) -> None:
        """Merge competitive intelligence.
        
        Args:
            existing: Existing competitive data
            new_data: New data to merge
        """
        if "competitors" not in existing:
            existing["competitors"] = []
        
        if isinstance(new_data, list):
            existing["competitors"].extend(new_data)
            existing["competitors"] = list(set(existing["competitors"]))
        elif isinstance(new_data, dict):
            for key, value in new_data.items():
                existing[key] = value
    
    def _validate_frameworks(self, frameworks: Dict[str, Any]) -> Dict[str, bool]:
        """Validate that all required frameworks are preserved.
        
        Args:
            frameworks: Extracted frameworks
            
        Returns:
            Validation results
        """
        validation = {}
        
        # Validate Benson points
        benson_valid = all(
            cat in frameworks.get("customer_psychology", {})
            for cat in ["pain_points", "desires", "beliefs", "values", "behaviors"]
        )
        validation["benson_points"] = benson_valid
        
        # Validate Frank Kern
        kern_valid = any(
            f"kern_{elem}" in frameworks.get("customer_psychology", {})
            for elem in FRAMEWORK_REQUIREMENTS["frank_kern"]
        )
        validation["frank_kern"] = kern_valid
        
        # Validate Priestley 5 P's
        priestley_valid = all(
            p in frameworks.get("authority_positioning", {})
            for p in FRAMEWORK_REQUIREMENTS["priestley_5ps"]
        )
        validation["priestley_5ps"] = priestley_valid
        
        # Validate Golden Hippo
        hippo_valid = any(
            elem in frameworks.get("content_strategy", {})
            for elem in FRAMEWORK_REQUIREMENTS["golden_hippo"]
        )
        validation["golden_hippo"] = hippo_valid
        
        return validation
    
    # Phase-specific synthesis methods
    
    def _synthesize_phase_1(self, responses: List[PhaseResponse]) -> Dict[str, Any]:
        """Synthesize Phase 1 (Business Intelligence) responses."""
        synthesis = {
            "business_model": {},
            "value_propositions": [],
            "target_market": {},
            "competitive_position": {}
        }
        
        # Extract from responses
        for response in responses:
            if response.phase_id == CIAPhase.PHASE_1A.value:
                # Foundational Business Intelligence
                content = response.response_content.get("response", "")
                synthesis["business_model"] = self._extract_section(content, "Business Model")
                synthesis["value_propositions"] = self._extract_list(content, "Value Propositions")
            
            elif response.phase_id == CIAPhase.PHASE_1B.value:
                # DNA Research & ICP
                content = response.response_content.get("response", "")
                synthesis["target_market"] = self._extract_section(content, "Ideal Client Profile")
            
            elif response.phase_id == CIAPhase.PHASE_1D.value:
                # Competitive Intelligence
                content = response.response_content.get("response", "")
                synthesis["competitive_position"] = self._extract_section(content, "Competitive Analysis")
        
        return synthesis
    
    def _synthesize_phase_2(self, responses: List[PhaseResponse]) -> Dict[str, Any]:
        """Synthesize Phase 2 (SEO & Social) responses."""
        synthesis = {
            "seo_intelligence": {},
            "social_intelligence": {},
            "digital_presence": {}
        }
        
        for response in responses:
            if response.phase_id == CIAPhase.PHASE_2A.value:
                synthesis["seo_intelligence"] = response.response_content.get("extracted", {})
            elif response.phase_id == CIAPhase.PHASE_2B.value:
                synthesis["social_intelligence"] = response.response_content.get("extracted", {})
        
        return synthesis
    
    def _synthesize_phase_3(self, responses: List[PhaseResponse]) -> Dict[str, Any]:
        """Synthesize Phase 3 (Strategic Synthesis) responses."""
        synthesis = {
            "trend_analysis": {},
            "testimonials": {},
            "strategic_synthesis": {}
        }
        
        for response in responses:
            if response.phase_id == CIAPhase.PHASE_3A.value:
                synthesis["trend_analysis"] = response.response_content.get("extracted", {})
            elif response.phase_id == CIAPhase.PHASE_3B.value:
                synthesis["testimonials"] = response.response_content.get("extracted", {})
            elif response.phase_id == CIAPhase.PHASE_3C.value:
                synthesis["strategic_synthesis"] = response.response_content.get("extracted", {})
        
        return synthesis
    
    def _synthesize_phase_4(self, responses: List[PhaseResponse]) -> Dict[str, Any]:
        """Synthesize Phase 4 (Golden Hippo Offer) responses."""
        return {
            "offer_development": responses[0].response_content.get("extracted", {})
            if responses else {}
        }
    
    def _synthesize_phase_5(self, responses: List[PhaseResponse]) -> Dict[str, Any]:
        """Synthesize Phase 5 (Content Strategy) responses."""
        return {
            "content_strategy": responses[0].response_content.get("extracted", {})
            if responses else {}
        }
    
    def _synthesize_phase_6(self, responses: List[PhaseResponse]) -> Dict[str, Any]:
        """Synthesize Phase 6 (Implementation) responses."""
        return {
            "implementation_plan": responses[0].response_content.get("extracted", {})
            if responses else {}
        }
    
    def _extract_opportunities(
        self,
        responses: List[PhaseResponse],
        archives: List[MasterArchive]
    ) -> List[Dict[str, Any]]:
        """Extract strategic opportunities from responses and archives."""
        opportunities = []
        
        # From responses
        for response in responses:
            content = response.response_content.get("response", "")
            if "opportunity" in content.lower() or "potential" in content.lower():
                # Simple extraction - could be enhanced with NLP
                opportunities.append({
                    "phase": response.phase_id,
                    "description": "Opportunity identified in " + response.phase_id
                })
        
        # From archives
        for archive in archives:
            if archive.opportunities_identified > 0:
                opportunities.extend(
                    archive.intelligence_summary.get("strategic_opportunities", [])
                )
        
        return opportunities[:10]  # Top 10 opportunities
    
    def _extract_priorities(
        self,
        responses: List[PhaseResponse],
        archives: List[MasterArchive]
    ) -> List[Dict[str, Any]]:
        """Extract implementation priorities."""
        priorities = []
        
        # From archives
        for archive in archives:
            priorities.extend(archive.implementation_priorities)
        
        # Deduplicate and prioritize
        seen = set()
        unique_priorities = []
        for priority in priorities:
            key = priority.get("title", "")
            if key and key not in seen:
                seen.add(key)
                unique_priorities.append(priority)
        
        return unique_priorities[:5]  # Top 5 priorities
    
    def _extract_section(self, content: str, section_name: str) -> Dict[str, Any]:
        """Extract a section from response content."""
        # Simple extraction - looks for section headers
        lines = content.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            if section_name.lower() in line.lower():
                in_section = True
                continue
            elif in_section and line.startswith('#'):
                break
            elif in_section:
                section_content.append(line)
        
        return {"content": '\n'.join(section_content).strip()}
    
    def _extract_list(self, content: str, list_name: str) -> List[str]:
        """Extract a list from response content."""
        items = []
        lines = content.split('\n')
        in_list = False
        
        for line in lines:
            if list_name.lower() in line.lower():
                in_list = True
                continue
            elif in_list and line.strip().startswith(('-', '*', '•', '1.', '2.', '3.')):
                item = line.strip().lstrip('-*•0123456789. ')
                if item:
                    items.append(item)
            elif in_list and not line.strip():
                continue
            elif in_list and line.strip() and not line.strip().startswith(('-', '*', '•')):
                break
        
        return items