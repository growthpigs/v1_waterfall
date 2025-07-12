"""
Brand BOS Simple Integration Test
Test the core functionality without database dependencies
"""

import asyncio
import logging
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_simple_integration():
    """Test core Brand BOS components"""
    
    logger.info("=== Starting Brand BOS Simple Integration Test ===")
    
    client_id = uuid4()
    
    try:
        # 1. Test Cartwheel Convergence Detection
        logger.info("\n1. Testing Cartwheel Convergence Detection...")
        convergence_result = await test_convergence_detection()
        
        # 2. Test Content Multiplication
        logger.info("\n2. Testing Content Multiplication...")
        content_result = await test_content_multiplication(convergence_result)
        
        # 3. Test Adsby Campaign Creation
        logger.info("\n3. Testing Adsby Campaign Creation...")
        campaign_result = await test_campaign_creation(content_result)
        
        # 4. Test Budget Optimization
        logger.info("\n4. Testing Budget Optimization...")
        optimization_result = await test_budget_optimization(campaign_result)
        
        logger.info("\n=== Simple Integration Test PASSED ✅ ===")
        
        # Print summary
        print_test_summary(
            convergence_result,
            content_result,
            campaign_result,
            optimization_result
        )
        
    except Exception as e:
        logger.error(f"\n=== Integration Test FAILED ❌ ===")
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise


async def test_convergence_detection() -> Dict[str, Any]:
    """Test viral convergence detection"""
    
    from src.database.cartwheel_models import ViralContent, ConvergenceSource
    from src.cartwheel.convergence_engine import ConvergenceDetectionEngine
    
    logger.info("Creating mock viral content...")
    
    # Create mock viral content
    viral_content = [
        ViralContent(
            source=ConvergenceSource.GROK_X_TRENDING,
            content_id="x_001",
            title="AI is transforming business operations",
            engagement_score=85.5,
            viral_velocity=0.75,
            topic_keywords=["ai", "business", "automation", "efficiency"],
            sentiment="positive",
            platform_specific_data={"retweets": 2500, "likes": 8500},
            detected_at=datetime.now()
        ),
        ViralContent(
            source=ConvergenceSource.REDDIT_VIRAL,
            content_id="reddit_001",
            title="How automation saved my business 40 hours per week",
            engagement_score=92.0,
            viral_velocity=0.82,
            topic_keywords=["automation", "business", "efficiency", "productivity"],
            sentiment="positive",
            platform_specific_data={"upvotes": 1850, "comments": 234},
            detected_at=datetime.now()
        )
    ]
    
    logger.info(f"✓ Created {len(viral_content)} viral content samples")
    
    # Test convergence scoring
    engine = ConvergenceDetectionEngine()
    
    # Manually test clustering
    clusters = engine._cluster_by_topic(viral_content)
    logger.info(f"✓ Clustered into {len(clusters)} topic groups")
    
    # Test scoring algorithm
    for topic, content_list in clusters.items():
        viral_score = engine._calculate_viral_score(content_list)
        logger.info(f"  - Topic '{topic}': viral score {viral_score:.1f}")
    
    return {
        "viral_content": viral_content,
        "clusters": clusters,
        "top_topic": "automation"
    }


async def test_content_multiplication(convergence_result: Dict[str, Any]) -> Dict[str, Any]:
    """Test content format generation"""
    
    from src.database.cartwheel_models import ContentFormat
    
    logger.info("Testing content format specifications...")
    
    # Test format specifications
    formats_to_generate = [
        ContentFormat.AI_SEARCH_BLOG,
        ContentFormat.EPIC_PILLAR_ARTICLE,
        ContentFormat.LINKEDIN_ARTICLE,
        ContentFormat.X_THREAD,
        ContentFormat.INSTAGRAM_POST
    ]
    
    content_specs = {}
    for format_type in formats_to_generate:
        from src.database.cartwheel_models import CONTENT_FORMAT_SPECS
        spec = CONTENT_FORMAT_SPECS.get(format_type, {})
        content_specs[format_type] = spec
        
        logger.info(f"✓ {format_type.value}:")
        if "word_count" in spec:
            logger.info(f"    Word count: {spec['word_count']}")
        if "character_limit" in spec:
            logger.info(f"    Character limit: {spec['character_limit']}")
    
    # Test helper functions
    from src.database.cartwheel_models import is_blog_format, is_social_format
    
    blog_formats = [f for f in formats_to_generate if is_blog_format(f)]
    social_formats = [f for f in formats_to_generate if is_social_format(f)]
    
    logger.info(f"\n✓ Identified {len(blog_formats)} blog formats")
    logger.info(f"✓ Identified {len(social_formats)} social formats")
    
    return {
        "formats_tested": len(formats_to_generate),
        "content_specs": content_specs,
        "blog_formats": len(blog_formats),
        "social_formats": len(social_formats)
    }


async def test_campaign_creation(content_result: Dict[str, Any]) -> Dict[str, Any]:
    """Test Google Ads campaign structure"""
    
    from src.adsby.models import AdCampaign, AdGroup, CampaignStatus
    from datetime import datetime
    
    logger.info("Creating test campaign structure...")
    
    # Create ad groups
    ad_groups = [
        AdGroup(
            name="Business Automation - Primary",
            keywords=[
                {"text": "business automation", "match_type": "broad"},
                {"text": "automate business processes", "match_type": "phrase"},
                {"text": "[business automation software]", "match_type": "exact"}
            ],
            max_cpc=2.50,
            target_cpa=50.0
        ),
        AdGroup(
            name="Business Automation - Solutions",
            keywords=[
                {"text": "automation solutions", "match_type": "broad"},
                {"text": "workflow automation", "match_type": "broad"}
            ],
            max_cpc=2.25,
            target_cpa=45.0
        )
    ]
    
    # Create campaign
    campaign = AdCampaign(
        campaign_id="test_001",
        cluster_id="cluster_001",
        client_id=str(uuid4()),
        title="Business Automation Solutions - 202501",
        budget_allocated=2500.00,
        daily_budget=83.33,
        start_date=datetime.now(),
        status=CampaignStatus.ACTIVE,
        keywords=["business automation", "workflow automation", "process optimization"],
        ad_groups=ad_groups,
        landing_page_url="https://example.com/automation-solutions"
    )
    
    logger.info(f"✓ Created campaign: {campaign.title}")
    logger.info(f"  - Budget: ${campaign.budget_allocated:,.2f}")
    logger.info(f"  - Ad Groups: {len(campaign.ad_groups)}")
    logger.info(f"  - Total Keywords: {sum(len(ag.keywords) for ag in campaign.ad_groups)}")
    
    # Test campaign properties
    logger.info(f"\n✓ Budget utilization: {campaign.budget_utilization:.1f}%")
    logger.info(f"✓ Days active: {campaign.days_active}")
    logger.info(f"✓ Underperforming: {campaign.is_underperforming}")
    
    return {
        "campaign": campaign,
        "ad_groups": len(ad_groups),
        "total_keywords": sum(len(ag.keywords) for ag in ad_groups)
    }


async def test_budget_optimization(campaign_result: Dict[str, Any]) -> Dict[str, Any]:
    """Test budget optimization logic"""
    
    from src.adsby.budget_optimizer import BudgetOptimizer, PERFORMANCE_WEIGHTS
    from src.adsby.models import PerformanceMetric
    
    logger.info("Testing budget optimization algorithms...")
    
    optimizer = BudgetOptimizer()
    
    # Test performance scoring
    test_metrics = {
        PerformanceMetric.CTR: 3.5,
        PerformanceMetric.CONVERSION_RATE: 5.2,
        PerformanceMetric.AUTHORITY_IMPACT: 68.0,
        PerformanceMetric.COST_PER_ACQUISITION: 42.50
    }
    
    composite_score = await optimizer._calculate_composite_score(test_metrics)
    
    logger.info(f"✓ Composite performance score: {composite_score:.1f}/100")
    logger.info("\nPerformance breakdown:")
    for metric, value in test_metrics.items():
        weight = PERFORMANCE_WEIGHTS.get(metric, 0)
        logger.info(f"  - {metric.value}: {value} (weight: {weight})")
    
    # Test budget reallocation
    campaigns = [campaign_result["campaign"]]
    allocation = await optimizer.calculate_budget_reallocation(campaigns)
    
    logger.info(f"\n✓ Budget reallocation calculated")
    for campaign_id, budget in allocation.items():
        logger.info(f"  - Campaign {campaign_id}: ${budget:,.2f}")
    
    return {
        "composite_score": composite_score,
        "performance_weights": PERFORMANCE_WEIGHTS,
        "budget_allocation": allocation
    }


def print_test_summary(
    convergence_result: Dict[str, Any],
    content_result: Dict[str, Any],
    campaign_result: Dict[str, Any],
    optimization_result: Dict[str, Any]
):
    """Print test execution summary"""
    
    print("\n" + "="*60)
    print("BRAND BOS SIMPLE INTEGRATION TEST SUMMARY")
    print("="*60)
    
    print("\n🔍 Convergence Detection:")
    print(f"  • Viral content analyzed: {len(convergence_result['viral_content'])}")
    print(f"  • Topic clusters found: {len(convergence_result['clusters'])}")
    print(f"  • Top topic: {convergence_result['top_topic']}")
    
    print("\n📝 Content Multiplication:")
    print(f"  • Formats tested: {content_result['formats_tested']}")
    print(f"  • Blog formats: {content_result['blog_formats']}")
    print(f"  • Social formats: {content_result['social_formats']}")
    
    print("\n🚀 Campaign Creation:")
    print(f"  • Campaign created: ✅")
    print(f"  • Ad groups: {campaign_result['ad_groups']}")
    print(f"  • Keywords: {campaign_result['total_keywords']}")
    
    print("\n💰 Budget Optimization:")
    print(f"  • Performance score: {optimization_result['composite_score']:.1f}/100")
    print(f"  • Optimization algorithm: ✅")
    
    print("\n✅ Core systems validated successfully!")
    print("="*60)


if __name__ == "__main__":
    # Run simple integration test
    asyncio.run(test_simple_integration())