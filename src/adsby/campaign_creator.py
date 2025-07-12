"""
Campaign Creator
Transforms content clusters into Google Ads campaigns
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
import logging

from ..database.cartwheel_models import ContentCluster, ContentPiece
from ..database.cartwheel_models import ContentFormat
from .models import AdCampaign, AdGroup, CampaignStatus
from ..integrations.google_ads_api import GoogleAdsClient

logger = logging.getLogger(__name__)

# Campaign configuration
DEFAULT_MAX_CPC = 2.50
DEFAULT_TARGET_CPA = 50.0
KEYWORD_MATCH_TYPES = ["broad", "phrase", "exact"]
MAX_KEYWORDS_PER_GROUP = 20
MAX_AD_GROUPS = 5


class CampaignCreator:
    """
    Creates Google Ads campaigns from content clusters
    using CIA intelligence for targeting optimization
    """
    
    def __init__(self, google_ads_client: Optional[GoogleAdsClient] = None):
        self.google_ads = google_ads_client
    
    async def create_from_cluster(
        self,
        content_cluster: ContentCluster,
        cia_intelligence: Dict[str, Any],
        client_id: UUID,
        budget: float
    ) -> AdCampaign:
        """
        Create a Google Ads campaign from content cluster
        
        Args:
            content_cluster: Content cluster with topic and keywords
            cia_intelligence: CIA analysis for targeting
            client_id: Client identifier
            budget: Campaign budget allocation
            
        Returns:
            Created AdCampaign instance
        """
        try:
            logger.info(f"Creating campaign from cluster: {content_cluster.cluster_topic}")
            
            # Extract campaign components
            campaign_data = await self._build_campaign_structure(
                content_cluster, cia_intelligence
            )
            
            # Create ad groups based on keyword themes
            ad_groups = await self._create_ad_groups(
                campaign_data["keywords"],
                content_cluster.cluster_topic,
                cia_intelligence
            )
            
            # Generate ad copy from content pieces
            await self._generate_ad_copy_for_groups(
                ad_groups, content_cluster, cia_intelligence
            )
            
            # Determine landing page
            landing_page = await self._select_landing_page(
                content_cluster, cia_intelligence
            )
            
            # Create campaign object
            campaign = AdCampaign(
                campaign_id=str(uuid4()),
                cluster_id=content_cluster.id,
                client_id=str(client_id),
                title=campaign_data["name"],
                budget_allocated=budget,
                daily_budget=budget / 30,  # Monthly to daily
                start_date=datetime.now(),
                status=CampaignStatus.DRAFT,
                keywords=campaign_data["keywords"],
                negative_keywords=campaign_data["negative_keywords"],
                ad_groups=ad_groups,
                landing_page_url=landing_page,
                tracking_parameters=self._build_tracking_parameters(content_cluster)
            )
            
            # Create in Google Ads if client available
            if self.google_ads:
                google_campaign_id = await self._create_google_campaign(campaign)
                campaign.campaign_id = google_campaign_id
            
            logger.info(f"Campaign created: {campaign.title}")
            return campaign
            
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            raise
    
    async def _build_campaign_structure(
        self,
        content_cluster: ContentCluster,
        cia_intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build campaign structure from cluster and intelligence"""
        
        # Extract SEO keywords from cluster
        cluster_keywords = self._extract_cluster_keywords(content_cluster)
        
        # Enhance with CIA intelligence
        enhanced_keywords = await self._enhance_keywords_with_cia(
            cluster_keywords, cia_intelligence
        )
        
        # Generate negative keywords
        negative_keywords = await self._generate_negative_keywords(
            cia_intelligence
        )
        
        # Build campaign name
        campaign_name = self._generate_campaign_name(
            content_cluster.cluster_topic,
            cia_intelligence.get("client_name", "Client")
        )
        
        return {
            "name": campaign_name,
            "keywords": enhanced_keywords[:50],  # Limit total keywords
            "negative_keywords": negative_keywords,
            "target_locations": cia_intelligence.get("target_locations", ["United States"]),
            "target_languages": ["en"],
            "campaign_type": "search",
            "bidding_strategy": "target_cpa",
            "target_cpa": DEFAULT_TARGET_CPA
        }
    
    async def _create_ad_groups(
        self,
        keywords: List[str],
        topic: str,
        cia_intelligence: Dict[str, Any]
    ) -> List[AdGroup]:
        """Create ad groups by clustering related keywords"""
        
        # Cluster keywords by theme
        keyword_clusters = await self._cluster_keywords_by_theme(
            keywords, cia_intelligence
        )
        
        ad_groups = []
        for theme, theme_keywords in keyword_clusters.items():
            # Create keyword variations with match types
            keyword_variations = self._create_keyword_variations(
                theme_keywords[:MAX_KEYWORDS_PER_GROUP]
            )
            
            ad_group = AdGroup(
                name=f"{topic} - {theme}",
                keywords=keyword_variations,
                max_cpc=DEFAULT_MAX_CPC,
                target_cpa=DEFAULT_TARGET_CPA
            )
            
            ad_groups.append(ad_group)
            
            if len(ad_groups) >= MAX_AD_GROUPS:
                break
        
        return ad_groups
    
    async def _generate_ad_copy_for_groups(
        self,
        ad_groups: List[AdGroup],
        content_cluster: ContentCluster,
        cia_intelligence: Dict[str, Any]
    ):
        """Generate ad copy for each ad group"""
        
        # Get authority positioning
        authority = cia_intelligence.get("authority_positioning", {})
        pain_points = cia_intelligence.get("pain_points", [])
        value_props = cia_intelligence.get("unique_value_propositions", [])
        
        for ad_group in ad_groups:
            # Generate responsive search ads
            ads = []
            
            # Create 2-3 ad variations per group
            for i in range(3):
                ad = await self._create_responsive_search_ad(
                    ad_group_name=ad_group.name,
                    topic=content_cluster.cluster_topic,
                    authority=authority,
                    pain_points=pain_points,
                    value_props=value_props,
                    keywords=ad_group.keywords
                )
                ads.append(ad)
            
            ad_group.ads = ads
    
    async def _create_responsive_search_ad(
        self,
        ad_group_name: str,
        topic: str,
        authority: Dict[str, Any],
        pain_points: List[str],
        value_props: List[str],
        keywords: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a responsive search ad"""
        
        # Extract primary keyword
        primary_keyword = keywords[0]["text"] if keywords else topic
        
        # Generate headlines (15 max, need at least 3)
        headlines = [
            f"{primary_keyword} Solutions",
            f"Expert {topic} Services",
            authority.get("tagline", f"Leading {topic} Experts"),
            f"Solve {pain_points[0]}" if pain_points else f"Master {topic}",
            f"{value_props[0]}" if value_props else "Get Results Today",
            "Free Consultation Available",
            "Trusted by 500+ Businesses",
            f"Transform Your {topic}",
            "Start Today - See Results",
            f"Professional {topic} Help",
            "Schedule Your Strategy Call",
            f"Proven {topic} Solutions",
            "Risk-Free Trial Available",
            "Expert Guidance & Support",
            "Join Industry Leaders"
        ][:15]
        
        # Generate descriptions (4 max, need at least 2)
        descriptions = [
            f"Discover how our {topic} solutions help businesses {value_props[0].lower() if value_props else 'achieve their goals'}. Expert guidance tailored to your needs.",
            f"Stop struggling with {pain_points[0].lower() if pain_points else 'common challenges'}. Our proven approach delivers measurable results. Get started today.",
            f"{authority.get('credentials', 'Industry-leading expertise')} with personalized strategies for your business. Free consultation available.",
            f"Join 500+ successful clients who transformed their {topic}. Risk-free trial. Expert support. Real results. Schedule your call now."
        ][:4]
        
        return {
            "type": "responsive_search_ad",
            "headlines": headlines,
            "descriptions": descriptions,
            "path1": topic.lower().replace(" ", "-")[:15],
            "path2": "solutions"[:15],
            "final_url": "{landing_page_url}",  # Placeholder
            "tracking_template": "{tracking_url}"  # Placeholder
        }
    
    async def _select_landing_page(
        self,
        content_cluster: ContentCluster,
        cia_intelligence: Dict[str, Any]
    ) -> str:
        """Select optimal landing page for campaign"""
        
        # In production, this would select from published content URLs
        # For now, construct a placeholder URL
        base_url = cia_intelligence.get("website_url", "https://example.com")
        
        # Clean topic for URL
        url_slug = content_cluster.cluster_topic.lower().replace(" ", "-")
        
        return f"{base_url}/solutions/{url_slug}"
    
    def _extract_cluster_keywords(self, content_cluster: ContentCluster) -> List[str]:
        """Extract keywords from content cluster"""
        keywords = []
        
        # Get keywords from cluster metadata
        if hasattr(content_cluster, 'seo_keywords'):
            keywords.extend(content_cluster.seo_keywords)
        
        # Extract from topic
        topic_words = content_cluster.cluster_topic.split()
        keywords.extend(topic_words)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw.lower() not in seen:
                seen.add(kw.lower())
                unique_keywords.append(kw)
        
        return unique_keywords
    
    async def _enhance_keywords_with_cia(
        self,
        keywords: List[str],
        cia_intelligence: Dict[str, Any]
    ) -> List[str]:
        """Enhance keywords using CIA intelligence"""
        enhanced = keywords.copy()
        
        # Add service-specific keywords
        services = cia_intelligence.get("service_offerings", [])
        for service in services[:3]:
            service_keywords = service.lower().split()
            enhanced.extend(service_keywords)
        
        # Add pain point keywords
        pain_points = cia_intelligence.get("pain_points", [])
        for pain_point in pain_points[:2]:
            # Extract key terms
            pain_keywords = [
                word.lower() for word in pain_point.split()
                if len(word) > 4  # Skip short words
            ]
            enhanced.extend(pain_keywords)
        
        # Add location modifiers if local business
        locations = cia_intelligence.get("target_locations", [])
        if locations and len(locations) <= 3:  # Local focus
            location_keywords = []
            for kw in keywords[:5]:
                for location in locations:
                    location_keywords.append(f"{kw} {location}")
            enhanced.extend(location_keywords)
        
        # Remove duplicates
        return list(dict.fromkeys(enhanced))
    
    async def _generate_negative_keywords(
        self, cia_intelligence: Dict[str, Any]
    ) -> List[str]:
        """Generate negative keywords to prevent wasted spend"""
        negative_keywords = [
            "free", "cheap", "diy", "tutorial", "how to",
            "jobs", "careers", "salary", "employment"
        ]
        
        # Add competitor names as negatives
        competitors = cia_intelligence.get("competitors", [])
        negative_keywords.extend([c.lower() for c in competitors])
        
        # Add industry-specific negatives
        industry = cia_intelligence.get("industry", "").lower()
        if "b2b" in industry:
            negative_keywords.extend(["consumer", "personal", "home"])
        elif "enterprise" in industry:
            negative_keywords.extend(["small business", "startup", "smb"])
        
        return negative_keywords
    
    async def _cluster_keywords_by_theme(
        self,
        keywords: List[str],
        cia_intelligence: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Cluster keywords into thematic groups"""
        
        # Simple clustering based on common terms
        # In production, use NLP for semantic clustering
        clusters = {
            "Primary": [],
            "Services": [],
            "Solutions": [],
            "Local": [],
            "Industry": []
        }
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            if any(term in keyword_lower for term in ["service", "help", "support"]):
                clusters["Services"].append(keyword)
            elif any(term in keyword_lower for term in ["solution", "software", "platform"]):
                clusters["Solutions"].append(keyword)
            elif any(loc.lower() in keyword_lower for loc in cia_intelligence.get("target_locations", [])):
                clusters["Local"].append(keyword)
            elif any(term in keyword_lower for term in cia_intelligence.get("industry_terms", [])):
                clusters["Industry"].append(keyword)
            else:
                clusters["Primary"].append(keyword)
        
        # Remove empty clusters
        return {k: v for k, v in clusters.items() if v}
    
    def _create_keyword_variations(
        self, keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Create keyword variations with match types"""
        variations = []
        
        for keyword in keywords:
            # Add broad match
            variations.append({
                "text": keyword,
                "match_type": "broad"
            })
            
            # Add phrase match for multi-word keywords
            if " " in keyword:
                variations.append({
                    "text": keyword,
                    "match_type": "phrase"
                })
            
            # Add exact match for high-value keywords
            if len(keyword.split()) <= 3:
                variations.append({
                    "text": keyword,
                    "match_type": "exact"
                })
        
        return variations
    
    def _generate_campaign_name(self, topic: str, client_name: str) -> str:
        """Generate descriptive campaign name"""
        date_str = datetime.now().strftime("%Y%m")
        clean_topic = topic[:30].title()
        return f"{client_name} - {clean_topic} - {date_str}"
    
    def _build_tracking_parameters(self, content_cluster: ContentCluster) -> Dict[str, str]:
        """Build UTM tracking parameters"""
        return {
            "utm_source": "google_ads",
            "utm_medium": "cpc",
            "utm_campaign": f"waterfall_{content_cluster.id}",
            "utm_content": "{adgroup}",
            "utm_term": "{keyword}"
        }
    
    async def _create_google_campaign(self, campaign: AdCampaign) -> str:
        """Create campaign in Google Ads and return campaign ID"""
        if not self.google_ads:
            # Return mock ID if no client
            return f"google_{campaign.campaign_id}"
        
        # Create campaign via API
        google_campaign = await self.google_ads.create_campaign(
            name=campaign.title,
            budget=campaign.daily_budget,
            campaign_type="SEARCH",
            bidding_strategy="TARGET_CPA",
            target_cpa=DEFAULT_TARGET_CPA,
            target_locations=["United States"],
            target_languages=["en"]
        )
        
        # Create ad groups
        for ad_group in campaign.ad_groups:
            await self.google_ads.create_ad_group(
                campaign_id=google_campaign["id"],
                name=ad_group.name,
                keywords=ad_group.keywords,
                max_cpc=ad_group.max_cpc
            )
        
        return google_campaign["id"]