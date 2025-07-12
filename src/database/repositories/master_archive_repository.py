"""
Repository for Master Archive operations.
Manages intelligence synthesis and framework preservation between phases.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import logging

from .base import BaseRepository
from ..models import (
    MasterArchive,
    MasterArchiveCreate,
    MasterArchiveUpdate,
    MasterArchiveSummary
)
from ...config.constants import CIAPhase, TABLE_MASTER_ARCHIVES, ARCHIVE_PHASES

logger = logging.getLogger(__name__)


class MasterArchiveRepository(BaseRepository[MasterArchive, MasterArchiveCreate, MasterArchiveUpdate]):
    """Repository for master archive database operations."""
    
    def __init__(self):
        """Initialize master archive repository."""
        super().__init__(
            model=MasterArchive,
            table_name=TABLE_MASTER_ARCHIVES
        )
    
    async def create_archive(
        self,
        session_id: UUID,
        phase_number: CIAPhase,
        intelligence_data: Dict[str, Any],
        frameworks: Dict[str, Any],
        tokens_used: int,
        phases_included: List[CIAPhase],
        client_id: UUID,
        previous_archive_id: Optional[UUID] = None
    ) -> MasterArchive:
        """Create a new master archive."""
        try:
            # Determine archive version
            version = 1
            if previous_archive_id:
                previous = await self.get_by_id(previous_archive_id, client_id)
                if previous:
                    version = previous.archive_version + 1
            
            archive_data = MasterArchiveCreate(
                session_id=session_id,
                phase_number=phase_number,
                intelligence_summary=intelligence_data.get("intelligence_summary", {}),
                customer_psychology=frameworks.get("customer_psychology", {}),
                competitive_analysis=frameworks.get("competitive_analysis", {}),
                authority_positioning=frameworks.get("authority_positioning", {}),
                content_strategy=frameworks.get("content_strategy", {}),
                context_tokens_used=tokens_used,
                phases_included=phases_included,
                previous_archive_id=previous_archive_id,
                archive_version=version
            )
            
            archive = await self.create(archive_data, client_id)
            
            logger.info(f"Created master archive v{version} for session {session_id}, phase {phase_number}")
            return archive
            
        except Exception as e:
            logger.error(f"Failed to create master archive: {e}")
            raise
    
    async def get_latest_archive(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> Optional[MasterArchive]:
        """Get the latest master archive for a session."""
        try:
            result = self.table.select("*") \
                .eq("session_id", str(session_id)) \
                .eq("client_id", str(client_id)) \
                .order("archive_version", desc=True) \
                .limit(1) \
                .execute()
            
            if result.data:
                return MasterArchive(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest archive: {e}")
            return None
    
    async def get_session_archives(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> List[MasterArchive]:
        """Get all master archives for a session in order."""
        try:
            result = self.table.select("*") \
                .eq("session_id", str(session_id)) \
                .eq("client_id", str(client_id)) \
                .order("archive_version", asc=True) \
                .execute()
            
            return [MasterArchive(**record) for record in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get session archives: {e}")
            return []
    
    async def get_archive_chain(
        self,
        archive_id: UUID,
        client_id: UUID
    ) -> List[MasterArchive]:
        """Get the complete archive chain leading to this archive."""
        try:
            chain = []
            current_id = archive_id
            
            while current_id:
                archive = await self.get_by_id(current_id, client_id)
                if not archive:
                    break
                
                chain.insert(0, archive)  # Insert at beginning to maintain order
                current_id = archive.previous_archive_id
            
            return chain
            
        except Exception as e:
            logger.error(f"Failed to get archive chain: {e}")
            return []
    
    async def validate_archive(
        self,
        archive_id: UUID,
        validation_notes: str,
        client_id: UUID
    ) -> Optional[MasterArchive]:
        """Mark an archive as validated with notes."""
        try:
            # Get the archive first
            archive = await self.get_by_id(archive_id, client_id)
            if not archive:
                return None
            
            # Perform framework validation
            framework_validation = archive.validate_framework_integrity()
            
            # Calculate synthesis quality score based on validation
            quality_score = sum(1 for v in framework_validation.values() if v) / len(framework_validation)
            
            # Update archive
            update_data = MasterArchiveUpdate(
                validated_at=datetime.utcnow(),
                validation_notes=validation_notes,
                synthesis_quality_score=quality_score,
                framework_integrity_scores={k: 1.0 if v else 0.0 for k, v in framework_validation.items()}
            )
            
            return await self.update(archive_id, update_data, client_id)
            
        except Exception as e:
            logger.error(f"Failed to validate archive: {e}")
            return None
    
    async def get_archives_by_phase(
        self,
        phase: CIAPhase,
        client_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[MasterArchive]:
        """Get all archives created at a specific phase."""
        try:
            query = self.table.select("*").eq("phase_number", phase.value)
            
            if client_id:
                query = query.eq("client_id", str(client_id))
            
            result = query.order("created_at", desc=True).limit(limit).execute()
            
            return [MasterArchive(**record) for record in result.data]
            
        except Exception as e:
            logger.error(f"Failed to get archives by phase: {e}")
            return []
    
    async def calculate_intelligence_metrics(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> Dict[str, Any]:
        """Calculate intelligence metrics across all archives for a session."""
        try:
            archives = await self.get_session_archives(session_id, client_id)
            
            if not archives:
                return {
                    "total_archives": 0,
                    "total_insights": 0,
                    "total_opportunities": 0,
                    "average_quality_score": 0.0,
                    "framework_coverage": {}
                }
            
            total_insights = sum(a.insights_count for a in archives)
            total_opportunities = sum(a.opportunities_identified for a in archives)
            
            # Calculate average quality score
            scored_archives = [a for a in archives if a.synthesis_quality_score > 0]
            avg_quality = sum(a.synthesis_quality_score for a in scored_archives) / len(scored_archives) if scored_archives else 0.0
            
            # Calculate framework coverage
            framework_coverage = {
                "benson_points": any(a.customer_psychology for a in archives),
                "priestley_5ps": any(a.authority_positioning for a in archives),
                "competitive_intel": any(a.competitive_analysis for a in archives),
                "content_strategy": any(a.content_strategy for a in archives),
            }
            
            return {
                "total_archives": len(archives),
                "total_insights": total_insights,
                "total_opportunities": total_opportunities,
                "average_quality_score": avg_quality,
                "framework_coverage": framework_coverage,
                "phases_with_archives": list(set(a.phase_number for a in archives))
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate intelligence metrics: {e}")
            return {}
    
    async def get_implementation_priorities(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get all implementation priorities from session archives."""
        try:
            archives = await self.get_session_archives(session_id, client_id)
            
            all_priorities = []
            for archive in archives:
                all_priorities.extend(archive.implementation_priorities)
            
            # Deduplicate and sort by priority
            seen = set()
            unique_priorities = []
            for priority in all_priorities:
                priority_key = priority.get("title", "")
                if priority_key and priority_key not in seen:
                    seen.add(priority_key)
                    unique_priorities.append(priority)
            
            return unique_priorities
            
        except Exception as e:
            logger.error(f"Failed to get implementation priorities: {e}")
            return []
    
    async def get_archive_summaries(
        self,
        session_id: UUID,
        client_id: UUID
    ) -> List[MasterArchiveSummary]:
        """Get summary view of all archives for a session."""
        try:
            archives = await self.get_session_archives(session_id, client_id)
            
            summaries = []
            for archive in archives:
                summary = MasterArchiveSummary(
                    id=archive.id,
                    session_id=archive.session_id,
                    phase_number=archive.phase_number,
                    archive_version=archive.archive_version,
                    phases_included=archive.phases_included,
                    context_tokens_used=archive.context_tokens_used,
                    insights_count=archive.insights_count,
                    opportunities_identified=archive.opportunities_identified,
                    synthesis_quality_score=archive.synthesis_quality_score,
                    created_at=archive.created_at
                )
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to get archive summaries: {e}")
            return []