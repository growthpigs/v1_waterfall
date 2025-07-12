"""
Cartwheel Convergence Detection Engine
Detects weekly viral opportunities through multi-source analysis
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import logging
from uuid import UUID, uuid4

from ..integrations.grok_api import GrokIntegration
from ..integrations.reddit_mcp import RedditMCP  
from ..integrations.google_trends import GoogleTrendsAnalyzer
from ..database.cartwheel_models import ConvergenceOpportunity, ConvergenceSource, ViralContent
from ..database.cartwheel_repository import CartwheelRepository

logger = logging.getLogger(__name__)

# Convergence detection parameters
CONVERGENCE_THRESHOLD = 60.0  # Minimum score for valid convergence
MAX_OPPORTUNITIES_PER_WEEK = 5  # Maximum opportunities to track
VIRAL_VELOCITY_THRESHOLD = 0.5  # Minimum viral velocity score
ENGAGEMENT_THRESHOLD = 50.0  # Minimum engagement score


@dataclass
class ConvergenceCluster:
    """Detected convergence opportunity across multiple sources"""
    cluster_id: str
    topic: str
    convergence_score: float  # 0-100 score based on cross-platform alignment
    viral_sources: List[ViralContent]
    seo_keywords: List[str]
    trend_momentum: str  # "rising", "peak", "declining"
    content_opportunity: Dict[str, Any]
    recommended_formats: List[str]
    urgency_level: str  # "immediate", "this_week", "planned"


class ConvergenceDetectionEngine:
    """Main engine for detecting viral convergence opportunities"""
    
    def __init__(
        self,
        grok_api_key: Optional[str] = None,
        repository: Optional[CartwheelRepository] = None
    ):
        self.grok = GrokIntegration(grok_api_key) if grok_api_key else None
        self.reddit = RedditMCP()
        self.trends = GoogleTrendsAnalyzer()
        self.repository = repository
        self.convergence_threshold = CONVERGENCE_THRESHOLD
    
    async def detect_weekly_convergence(
        self,
        client_id: UUID,
        cia_intelligence: Dict[str, Any]
    ) -> List[ConvergenceOpportunity]:
        """
        Detect convergence opportunities for the week
        
        Args:
            client_id: Client identifier
            cia_intelligence: CIA analysis data for context
            
        Returns:
            List of top convergence opportunities
        """
        try:
            # Gather viral content from all sources
            viral_content = await self._gather_viral_content()
            
            if not viral_content:
                logger.warning("No viral content found across sources")
                return []
            
            # Extract keywords for trend analysis
            all_keywords = self._extract_all_keywords(viral_content)
            trend_data = await self.trends.analyze_trend_momentum(all_keywords)
            
            # Cluster related content by topic
            topic_clusters = self._cluster_by_topic(viral_content)
            
            # Score convergence opportunities
            convergence_clusters = []
            for topic, content_list in topic_clusters.items():
                cluster = await self._analyze_convergence_cluster(
                    topic, content_list, trend_data, cia_intelligence
                )
                
                if cluster.convergence_score >= self.convergence_threshold:
                    convergence_clusters.append(cluster)
            
            # Convert to opportunities and sort by score
            opportunities = self._clusters_to_opportunities(
                convergence_clusters, client_id
            )
            
            # Save to database if repository available
            if self.repository:
                for opportunity in opportunities[:MAX_OPPORTUNITIES_PER_WEEK]:
                    await self.repository.save_convergence_opportunity(opportunity)
            
            return opportunities[:MAX_OPPORTUNITIES_PER_WEEK]
            
        except Exception as e:
            logger.error(f"Error detecting convergence: {str(e)}")
            raise
    
    async def _gather_viral_content(self) -> List[ViralContent]:
        """Gather viral content from all configured sources"""
        viral_content = []
        
        # Gather from Grok if available
        if self.grok:
            try:
                grok_content = await self.grok.get_trending_posts(
                    hours=24, media_only=True
                )
                viral_content.extend(grok_content)
                logger.info(f"Found {len(grok_content)} trending posts from X")
            except Exception as e:
                logger.error(f"Error fetching Grok data: {str(e)}")
        
        # Gather from Reddit
        try:
            reddit_content = await self.reddit.get_viral_posts(hours=24)
            viral_content.extend(reddit_content)
            logger.info(f"Found {len(reddit_content)} viral posts from Reddit")
        except Exception as e:
            logger.error(f"Error fetching Reddit data: {str(e)}")
        
        return viral_content
    
    def _extract_all_keywords(self, viral_content: List[ViralContent]) -> List[str]:
        """Extract unique keywords from all viral content"""
        keywords = set()
        
        for content in viral_content:
            keywords.update(content.topic_keywords)
        
        return list(keywords)
    
    def _cluster_by_topic(
        self, viral_content: List[ViralContent]
    ) -> Dict[str, List[ViralContent]]:
        """Cluster viral content by related topics"""
        clusters = {}
        
        for content in viral_content:
            # Simple clustering by keyword overlap
            # In production, use more sophisticated NLP clustering
            assigned = False
            
            for topic, cluster_content in clusters.items():
                # Check keyword overlap with existing clusters
                existing_keywords = set()
                for c in cluster_content:
                    existing_keywords.update(c.topic_keywords)
                
                overlap = len(set(content.topic_keywords) & existing_keywords)
                if overlap >= 2:  # At least 2 keywords in common
                    clusters[topic].append(content)
                    assigned = True
                    break
            
            if not assigned:
                # Create new cluster with primary keyword as topic
                primary_topic = content.topic_keywords[0] if content.topic_keywords else "general"
                clusters[primary_topic] = [content]
        
        return clusters
    
    async def _analyze_convergence_cluster(
        self,
        topic: str,
        content_list: List[ViralContent],
        trend_data: Dict[str, Any],
        cia_intelligence: Dict[str, Any]
    ) -> ConvergenceCluster:
        """Analyze single convergence cluster for opportunity scoring"""
        
        # Calculate convergence score based on multiple factors
        viral_score = self._calculate_viral_score(content_list)
        trend_score = self._calculate_trend_score(topic, trend_data)
        relevance_score = self._calculate_client_relevance(topic, cia_intelligence)
        timing_score = self._calculate_timing_score(content_list)
        
        convergence_score = (
            viral_score * 0.3 +
            trend_score * 0.25 +
            relevance_score * 0.25 +
            timing_score * 0.2
        )
        
        # Determine recommended content formats
        recommended_formats = self._recommend_content_formats(
            content_list, convergence_score, cia_intelligence
        )
        
        # Determine urgency level
        urgency = self._determine_urgency(convergence_score, trend_data.get(topic, {}))
        
        # Extract SEO keywords
        seo_keywords = self._extract_seo_keywords(content_list, trend_data)
        
        return ConvergenceCluster(
            cluster_id=f"conv_{topic.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}",
            topic=topic,
            convergence_score=convergence_score,
            viral_sources=content_list,
            seo_keywords=seo_keywords,
            trend_momentum=trend_data.get(topic, {}).get("momentum", "stable"),
            content_opportunity={
                "hook_opportunities": self._identify_hooks(content_list),
                "angle_variations": self._generate_angles(topic, content_list),
                "target_emotions": self._analyze_emotional_drivers(content_list)
            },
            recommended_formats=recommended_formats,
            urgency_level=urgency
        )
    
    def _calculate_viral_score(self, content_list: List[ViralContent]) -> float:
        """Calculate viral potential score (0-100)"""
        if not content_list:
            return 0.0
        
        avg_engagement = sum(c.engagement_score for c in content_list) / len(content_list)
        source_diversity = len(set(c.source for c in content_list))
        velocity_factor = sum(c.viral_velocity for c in content_list) / len(content_list)
        
        # Bonus for multi-source convergence
        diversity_bonus = min(source_diversity * 10, 30)
        
        return min(
            avg_engagement * 0.5 + velocity_factor * 30 + diversity_bonus,
            100.0
        )
    
    def _calculate_trend_score(self, topic: str, trend_data: Dict[str, Any]) -> float:
        """Calculate trend momentum score"""
        topic_trend = trend_data.get(topic, {})
        
        current_interest = topic_trend.get("current_interest", 0)
        momentum = topic_trend.get("momentum", "stable")
        
        # Base score from current interest level
        base_score = min(current_interest, 100)
        
        # Momentum multiplier
        momentum_multipliers = {
            "rising": 1.3,
            "peak": 1.0,
            "stable": 0.8,
            "declining": 0.5
        }
        
        multiplier = momentum_multipliers.get(momentum, 0.8)
        
        return min(base_score * multiplier, 100.0)
    
    def _calculate_client_relevance(
        self, topic: str, cia_intelligence: Dict[str, Any]
    ) -> float:
        """Calculate relevance to client's business and audience"""
        if not cia_intelligence:
            return 50.0  # Default moderate relevance
        
        # Extract client context
        target_audience = cia_intelligence.get("target_audience", {})
        pain_points = cia_intelligence.get("pain_points", [])
        service_offerings = cia_intelligence.get("service_offerings", [])
        
        relevance_score = 0.0
        
        # Check topic alignment with pain points
        for pain_point in pain_points:
            if any(keyword in topic.lower() for keyword in pain_point.lower().split()):
                relevance_score += 30
                break
        
        # Check alignment with service offerings
        for service in service_offerings:
            if any(keyword in topic.lower() for keyword in service.lower().split()):
                relevance_score += 30
                break
        
        # Check audience interest alignment
        audience_interests = target_audience.get("interests", [])
        for interest in audience_interests:
            if any(keyword in topic.lower() for keyword in interest.lower().split()):
                relevance_score += 20
                break
        
        # Base relevance for any business topic
        if any(term in topic.lower() for term in ["business", "marketing", "growth", "success"]):
            relevance_score += 20
        
        return min(relevance_score, 100.0)
    
    def _calculate_timing_score(self, content_list: List[ViralContent]) -> float:
        """Calculate timing opportunity score"""
        if not content_list:
            return 0.0
        
        # Check recency - how fresh is the viral content
        now = datetime.now()
        recency_scores = []
        
        for content in content_list:
            hours_ago = (now - content.detected_at).total_seconds() / 3600
            if hours_ago <= 6:
                recency_scores.append(100)
            elif hours_ago <= 12:
                recency_scores.append(80)
            elif hours_ago <= 24:
                recency_scores.append(60)
            else:
                recency_scores.append(40)
        
        avg_recency = sum(recency_scores) / len(recency_scores)
        
        # Check velocity - is engagement accelerating?
        high_velocity_count = sum(1 for c in content_list if c.viral_velocity > VIRAL_VELOCITY_THRESHOLD)
        velocity_ratio = high_velocity_count / len(content_list)
        
        return avg_recency * 0.7 + (velocity_ratio * 100 * 0.3)
    
    def _recommend_content_formats(
        self,
        content_list: List[ViralContent],
        convergence_score: float,
        cia_intelligence: Dict[str, Any]
    ) -> List[str]:
        """Recommend optimal content formats for this convergence"""
        
        base_formats = ["ai_search_blog", "epic_pillar_article"]
        
        if convergence_score > 80:
            base_formats.extend(["pillar_podcast", "instagram_post", "tiktok_ugc"])
        
        if convergence_score > 90:
            base_formats.extend(["youtube_shorts", "linkedin_article", "x_thread"])
        
        # Add supporting blog posts for comprehensive coverage
        if convergence_score > 70:
            base_formats.extend(["blog_supporting_1", "blog_supporting_2"])
        
        # Filter based on client preferences from intelligence
        client_formats = cia_intelligence.get("preferred_formats", [])
        if client_formats:
            base_formats = [f for f in base_formats if f in client_formats or not client_formats]
        
        return base_formats
    
    def _determine_urgency(
        self, convergence_score: float, trend_data: Dict[str, Any]
    ) -> str:
        """Determine content creation urgency level"""
        momentum = trend_data.get("momentum", "stable")
        
        if convergence_score > 85 and momentum == "rising":
            return "immediate"
        elif convergence_score > 70 or momentum == "peak":
            return "this_week"
        else:
            return "planned"
    
    def _extract_seo_keywords(
        self, content_list: List[ViralContent], trend_data: Dict[str, Any]
    ) -> List[str]:
        """Extract SEO keywords from viral content and trends"""
        keywords = set()
        
        # Get keywords from viral content
        for content in content_list:
            keywords.update(content.topic_keywords[:3])  # Top 3 from each
        
        # Add related queries from trends
        for topic, data in trend_data.items():
            related = data.get("related_queries", [])
            keywords.update(related[:2])  # Top 2 related queries
        
        # Sort by frequency and return top keywords
        keyword_list = list(keywords)
        return keyword_list[:10]  # Return top 10 keywords
    
    def _identify_hooks(self, content_list: List[ViralContent]) -> List[str]:
        """Identify viral hooks from content patterns"""
        hooks = []
        
        for content in content_list:
            # Extract hook patterns from high-performing content
            if content.engagement_score > ENGAGEMENT_THRESHOLD:
                # Simple hook extraction - in production use NLP
                title_words = content.title.split()[:10]
                hook = " ".join(title_words)
                if hook not in hooks:
                    hooks.append(hook)
        
        return hooks[:5]  # Top 5 hooks
    
    def _generate_angles(
        self, topic: str, content_list: List[ViralContent]
    ) -> List[str]:
        """Generate content angle variations"""
        angles = [
            f"How {topic} is transforming the industry",
            f"The hidden truth about {topic}",
            f"Why experts are wrong about {topic}",
            f"{topic}: What nobody is talking about",
            f"The {topic} revolution: 5 things to know"
        ]
        
        # Add sentiment-based angles
        positive_count = sum(1 for c in content_list if c.sentiment == "positive")
        negative_count = sum(1 for c in content_list if c.sentiment == "negative")
        
        if positive_count > negative_count:
            angles.append(f"The surprising benefits of {topic}")
        else:
            angles.append(f"The {topic} problem nobody wants to address")
        
        return angles[:5]
    
    def _analyze_emotional_drivers(self, content_list: List[ViralContent]) -> List[str]:
        """Analyze emotional drivers in viral content"""
        emotions = {
            "curiosity": 0,
            "fear": 0,
            "excitement": 0,
            "anger": 0,
            "hope": 0
        }
        
        # Simple emotion detection based on sentiment
        for content in content_list:
            if content.sentiment == "positive":
                emotions["excitement"] += 1
                emotions["hope"] += 1
            elif content.sentiment == "negative":
                emotions["fear"] += 1
                emotions["anger"] += 1
            
            # High engagement often indicates curiosity
            if content.engagement_score > 70:
                emotions["curiosity"] += 1
        
        # Return top emotional drivers
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        return [emotion for emotion, _ in sorted_emotions[:3]]
    
    def _clusters_to_opportunities(
        self, clusters: List[ConvergenceCluster], client_id: UUID
    ) -> List[ConvergenceOpportunity]:
        """Convert convergence clusters to opportunity models"""
        opportunities = []
        week_date = datetime.now().strftime("%Y-W%U")
        
        for cluster in clusters:
            opportunity = ConvergenceOpportunity(
                id=str(uuid4()),
                client_id=str(client_id),
                week_date=week_date,
                topic=cluster.topic,
                convergence_score=cluster.convergence_score,
                viral_sources=[self._viral_content_to_dict(vc) for vc in cluster.viral_sources],
                seo_keywords=cluster.seo_keywords,
                trend_momentum=cluster.trend_momentum,
                content_opportunity=cluster.content_opportunity,
                recommended_formats=cluster.recommended_formats,
                urgency_level=cluster.urgency_level,
                created_at=datetime.now()
            )
            opportunities.append(opportunity)
        
        # Sort by convergence score descending
        opportunities.sort(key=lambda x: x.convergence_score, reverse=True)
        
        return opportunities
    
    def _viral_content_to_dict(self, viral_content: ViralContent) -> Dict[str, Any]:
        """Convert ViralContent to dictionary for storage"""
        return {
            "source": viral_content.source.value,
            "content_id": viral_content.content_id,
            "title": viral_content.title,
            "engagement_score": viral_content.engagement_score,
            "viral_velocity": viral_content.viral_velocity,
            "topic_keywords": viral_content.topic_keywords,
            "sentiment": viral_content.sentiment,
            "platform_specific_data": viral_content.platform_specific_data,
            "detected_at": viral_content.detected_at.isoformat()
        }


async def run_weekly_convergence_analysis(
    client_id: UUID,
    cia_intelligence: Dict[str, Any],
    grok_api_key: Optional[str] = None,
    repository: Optional[CartwheelRepository] = None
) -> Optional[Dict[str, Any]]:
    """
    Execute weekly convergence detection workflow
    
    Args:
        client_id: Client identifier
        cia_intelligence: CIA analysis data
        grok_api_key: Optional Grok API key
        repository: Optional database repository
        
    Returns:
        Content brief for top opportunity or None
    """
    try:
        engine = ConvergenceDetectionEngine(grok_api_key, repository)
        
        # Detect convergence opportunities
        opportunities = await engine.detect_weekly_convergence(client_id, cia_intelligence)
        
        if not opportunities:
            logger.info("No convergence opportunities detected this week")
            return None
        
        # Select top opportunity
        selected_opportunity = opportunities[0]
        
        # Generate content recommendation brief
        content_brief = {
            "opportunity_id": selected_opportunity.id,
            "client_id": str(client_id),
            "topic": selected_opportunity.topic,
            "formats": selected_opportunity.recommended_formats,
            "urgency": selected_opportunity.urgency_level,
            "viral_hooks": selected_opportunity.content_opportunity["hook_opportunities"],
            "content_angles": selected_opportunity.content_opportunity["angle_variations"],
            "emotional_drivers": selected_opportunity.content_opportunity["target_emotions"],
            "seo_keywords": selected_opportunity.seo_keywords,
            "convergence_score": selected_opportunity.convergence_score,
            "intelligence_context": cia_intelligence
        }
        
        logger.info(
            f"Generated content brief for top opportunity: {selected_opportunity.topic} "
            f"(score: {selected_opportunity.convergence_score:.1f})"
        )
        
        return content_brief
        
    except Exception as e:
        logger.error(f"Error in weekly convergence analysis: {str(e)}")
        raise