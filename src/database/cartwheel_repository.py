"""
Cartwheel Repository for database operations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
import logging

from supabase import Client
from .base import SupabaseConnection
from .cartwheel_models import (
    ConvergenceOpportunity, ContentCluster, ContentPiece,
    ContentApproval, PublishingJob, ContentPerformance,
    ApprovalStatus, PublishingStatus
)

logger = logging.getLogger(__name__)


class CartwheelRepository:
    """Repository for Cartwheel content engine database operations"""
    
    def __init__(self, supabase_client: Optional[Client] = None):
        self.client = supabase_client or SupabaseConnection().get_client()
    
    # Convergence Opportunities
    async def save_convergence_opportunity(
        self, opportunity: ConvergenceOpportunity
    ) -> ConvergenceOpportunity:
        """Save a convergence opportunity to database"""
        try:
            data = opportunity.dict()
            result = self.client.table("convergence_opportunities").insert(data).execute()
            
            if result.data:
                logger.info(f"Saved convergence opportunity: {opportunity.topic}")
                return ConvergenceOpportunity(**result.data[0])
            else:
                raise Exception("Failed to save convergence opportunity")
                
        except Exception as e:
            logger.error(f"Error saving convergence opportunity: {str(e)}")
            raise
    
    async def get_weekly_opportunities(
        self, client_id: UUID, week_date: str
    ) -> List[ConvergenceOpportunity]:
        """Get convergence opportunities for a specific week"""
        try:
            result = self.client.table("convergence_opportunities") \
                .select("*") \
                .eq("client_id", str(client_id)) \
                .eq("week_date", week_date) \
                .order("convergence_score", desc=True) \
                .execute()
            
            return [ConvergenceOpportunity(**opp) for opp in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching weekly opportunities: {str(e)}")
            return []
    
    async def get_latest_opportunities(
        self, client_id: UUID, limit: int = 5
    ) -> List[ConvergenceOpportunity]:
        """Get latest convergence opportunities for a client"""
        try:
            result = self.client.table("convergence_opportunities") \
                .select("*") \
                .eq("client_id", str(client_id)) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            return [ConvergenceOpportunity(**opp) for opp in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching latest opportunities: {str(e)}")
            return []
    
    # Content Clusters
    async def create_content_cluster(
        self, cluster: ContentCluster
    ) -> ContentCluster:
        """Create a new content cluster"""
        try:
            data = cluster.dict()
            result = self.client.table("content_clusters").insert(data).execute()
            
            if result.data:
                logger.info(f"Created content cluster: {cluster.cluster_topic}")
                return ContentCluster(**result.data[0])
            else:
                raise Exception("Failed to create content cluster")
                
        except Exception as e:
            logger.error(f"Error creating content cluster: {str(e)}")
            raise
    
    async def update_content_cluster(
        self, cluster: ContentCluster
    ) -> ContentCluster:
        """Update an existing content cluster"""
        try:
            data = cluster.dict(exclude={"id", "created_at"})
            result = self.client.table("content_clusters") \
                .update(data) \
                .eq("id", cluster.id) \
                .execute()
            
            if result.data:
                return ContentCluster(**result.data[0])
            else:
                raise Exception("Failed to update content cluster")
                
        except Exception as e:
            logger.error(f"Error updating content cluster: {str(e)}")
            raise
    
    async def get_content_cluster(self, cluster_id: str) -> Optional[ContentCluster]:
        """Get a content cluster by ID"""
        try:
            result = self.client.table("content_clusters") \
                .select("*") \
                .eq("id", cluster_id) \
                .single() \
                .execute()
            
            if result.data:
                return ContentCluster(**result.data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching content cluster: {str(e)}")
            return None
    
    async def get_pending_clusters(
        self, client_id: UUID
    ) -> List[ContentCluster]:
        """Get content clusters pending approval"""
        try:
            result = self.client.table("content_clusters") \
                .select("*") \
                .eq("client_id", str(client_id)) \
                .eq("approval_status", "pending") \
                .order("created_at", desc=True) \
                .execute()
            
            return [ContentCluster(**cluster) for cluster in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching pending clusters: {str(e)}")
            return []
    
    # Content Pieces
    async def save_content_piece(
        self, piece: ContentPiece
    ) -> ContentPiece:
        """Save a content piece to database"""
        try:
            data = piece.dict()
            result = self.client.table("content_pieces").insert(data).execute()
            
            if result.data:
                logger.info(f"Saved content piece: {piece.title}")
                return ContentPiece(**result.data[0])
            else:
                raise Exception("Failed to save content piece")
                
        except Exception as e:
            logger.error(f"Error saving content piece: {str(e)}")
            raise
    
    async def save_content_pieces(
        self, pieces: List[ContentPiece]
    ) -> List[ContentPiece]:
        """Save multiple content pieces"""
        try:
            data = [piece.dict() for piece in pieces]
            result = self.client.table("content_pieces").insert(data).execute()
            
            if result.data:
                logger.info(f"Saved {len(pieces)} content pieces")
                return [ContentPiece(**p) for p in result.data]
            else:
                raise Exception("Failed to save content pieces")
                
        except Exception as e:
            logger.error(f"Error saving content pieces: {str(e)}")
            raise
    
    async def update_content_piece(
        self, piece: ContentPiece
    ) -> ContentPiece:
        """Update an existing content piece"""
        try:
            data = piece.dict(exclude={"id", "created_at"})
            result = self.client.table("content_pieces") \
                .update(data) \
                .eq("id", piece.id) \
                .execute()
            
            if result.data:
                return ContentPiece(**result.data[0])
            else:
                raise Exception("Failed to update content piece")
                
        except Exception as e:
            logger.error(f"Error updating content piece: {str(e)}")
            raise
    
    async def get_cluster_content(
        self, cluster_id: str
    ) -> List[ContentPiece]:
        """Get all content pieces for a cluster"""
        try:
            result = self.client.table("content_pieces") \
                .select("*") \
                .eq("cluster_id", cluster_id) \
                .order("created_at") \
                .execute()
            
            return [ContentPiece(**piece) for piece in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching cluster content: {str(e)}")
            return []
    
    async def get_pending_content(
        self, client_id: UUID
    ) -> List[ContentPiece]:
        """Get content pieces pending approval"""
        try:
            result = self.client.table("content_pieces") \
                .select("*") \
                .eq("client_id", str(client_id)) \
                .eq("approval_status", ApprovalStatus.PENDING.value) \
                .order("created_at", desc=True) \
                .execute()
            
            return [ContentPiece(**piece) for piece in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching pending content: {str(e)}")
            return []
    
    # Content Approval
    async def create_approval(
        self, approval: ContentApproval
    ) -> ContentApproval:
        """Create a content approval record"""
        try:
            data = approval.dict()
            result = self.client.table("content_approvals").insert(data).execute()
            
            if result.data:
                return ContentApproval(**result.data[0])
            else:
                raise Exception("Failed to create approval")
                
        except Exception as e:
            logger.error(f"Error creating approval: {str(e)}")
            raise
    
    async def update_approval(
        self, approval: ContentApproval
    ) -> ContentApproval:
        """Update an approval record"""
        try:
            data = approval.dict(exclude={"id", "created_at"})
            result = self.client.table("content_approvals") \
                .update(data) \
                .eq("id", approval.id) \
                .execute()
            
            if result.data:
                return ContentApproval(**result.data[0])
            else:
                raise Exception("Failed to update approval")
                
        except Exception as e:
            logger.error(f"Error updating approval: {str(e)}")
            raise
    
    async def get_content_approvals(
        self, content_piece_id: str
    ) -> List[ContentApproval]:
        """Get approval history for a content piece"""
        try:
            result = self.client.table("content_approvals") \
                .select("*") \
                .eq("content_piece_id", content_piece_id) \
                .order("created_at", desc=True) \
                .execute()
            
            return [ContentApproval(**approval) for approval in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching content approvals: {str(e)}")
            return []
    
    # Publishing Jobs
    async def create_publishing_job(
        self, job: PublishingJob
    ) -> PublishingJob:
        """Create a publishing job"""
        try:
            data = job.dict()
            result = self.client.table("publishing_jobs").insert(data).execute()
            
            if result.data:
                return PublishingJob(**result.data[0])
            else:
                raise Exception("Failed to create publishing job")
                
        except Exception as e:
            logger.error(f"Error creating publishing job: {str(e)}")
            raise
    
    async def update_publishing_job(
        self, job: PublishingJob
    ) -> PublishingJob:
        """Update a publishing job"""
        try:
            data = job.dict(exclude={"id", "created_at"})
            result = self.client.table("publishing_jobs") \
                .update(data) \
                .eq("id", job.id) \
                .execute()
            
            if result.data:
                return PublishingJob(**result.data[0])
            else:
                raise Exception("Failed to update publishing job")
                
        except Exception as e:
            logger.error(f"Error updating publishing job: {str(e)}")
            raise
    
    async def get_pending_jobs(
        self, platform: Optional[str] = None
    ) -> List[PublishingJob]:
        """Get pending publishing jobs"""
        try:
            query = self.client.table("publishing_jobs") \
                .select("*") \
                .in_("status", ["queued", "processing"])
            
            if platform:
                query = query.eq("platform", platform)
            
            result = query.order("scheduled_for").execute()
            
            return [PublishingJob(**job) for job in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching pending jobs: {str(e)}")
            return []
    
    async def get_failed_jobs(
        self, client_id: UUID, retry_limit: int = 3
    ) -> List[PublishingJob]:
        """Get failed publishing jobs that can be retried"""
        try:
            result = self.client.table("publishing_jobs") \
                .select("*") \
                .eq("client_id", str(client_id)) \
                .eq("status", "failed") \
                .lt("retry_count", retry_limit) \
                .order("created_at", desc=True) \
                .execute()
            
            return [PublishingJob(**job) for job in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching failed jobs: {str(e)}")
            return []
    
    # Performance Tracking
    async def save_performance_metric(
        self, metric: ContentPerformance
    ) -> ContentPerformance:
        """Save a content performance metric"""
        try:
            data = metric.dict()
            result = self.client.table("content_performance").insert(data).execute()
            
            if result.data:
                return ContentPerformance(**result.data[0])
            else:
                raise Exception("Failed to save performance metric")
                
        except Exception as e:
            logger.error(f"Error saving performance metric: {str(e)}")
            raise
    
    async def get_content_performance(
        self, content_piece_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ContentPerformance]:
        """Get performance metrics for a content piece"""
        try:
            query = self.client.table("content_performance") \
                .select("*") \
                .eq("content_piece_id", content_piece_id)
            
            if start_date:
                query = query.gte("measured_at", start_date.isoformat())
            if end_date:
                query = query.lte("measured_at", end_date.isoformat())
            
            result = query.order("measured_at", desc=True).execute()
            
            return [ContentPerformance(**metric) for metric in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching performance metrics: {str(e)}")
            return []
    
    # Analytics and Reporting
    async def get_content_stats(
        self, client_id: UUID, days: int = 30
    ) -> Dict[str, Any]:
        """Get content generation statistics for a client"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get content counts by status
            content_result = self.client.table("content_pieces") \
                .select("publishing_status", count="exact") \
                .eq("client_id", str(client_id)) \
                .gte("created_at", cutoff_date) \
                .execute()
            
            # Get convergence opportunities count
            convergence_result = self.client.table("convergence_opportunities") \
                .select("*", count="exact") \
                .eq("client_id", str(client_id)) \
                .gte("created_at", cutoff_date) \
                .execute()
            
            # Get publishing job stats
            jobs_result = self.client.table("publishing_jobs") \
                .select("status", count="exact") \
                .eq("client_id", str(client_id)) \
                .gte("created_at", cutoff_date) \
                .execute()
            
            return {
                "period_days": days,
                "content_pieces": {
                    "total": content_result.count if hasattr(content_result, 'count') else 0,
                    "by_status": self._group_by_status(content_result.data)
                },
                "convergence_opportunities": convergence_result.count if hasattr(convergence_result, 'count') else 0,
                "publishing_jobs": {
                    "total": jobs_result.count if hasattr(jobs_result, 'count') else 0,
                    "by_status": self._group_by_status(jobs_result.data)
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching content stats: {str(e)}")
            return {
                "error": str(e),
                "period_days": days
            }
    
    def _group_by_status(self, data: List[Dict]) -> Dict[str, int]:
        """Group data by status field"""
        status_counts = {}
        for item in data:
            status = item.get("status") or item.get("publishing_status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts