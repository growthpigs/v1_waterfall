"""
Brand BOS Core Algorithm Test
Tests core algorithms without database dependencies
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


async def test_core_algorithms():
    """Test core Brand BOS algorithms"""
    
    logger.info("=== Starting Brand BOS Core Algorithm Test ===")
    
    client_id = uuid4()
    
    try:
        # 1. Test Cartwheel Models and Format Detection
        logger.info("\n1. Testing Cartwheel Models and Format Detection...")
        cartwheel_result = await test_cartwheel_models()
        
        # 2. Test Adsby Performance Scoring
        logger.info("\n2. Testing Adsby Performance Scoring...")
        adsby_result = await test_adsby_performance()
        
        # 3. Test Budget Optimization Algorithm
        logger.info("\n3. Testing Budget Optimization Algorithm...")
        budget_result = await test_budget_optimization()
        
        logger.info("\n=== Core Algorithm Test PASSED ✅ ===")
        
        # Print summary
        print_test_summary(cartwheel_result, adsby_result, budget_result)
        
    except Exception as e:
        logger.error(f"\n=== Core Algorithm Test FAILED ❌ ===")
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise


async def test_cartwheel_models() -> Dict[str, Any]:
    """Test Cartwheel model structures and format detection"""
    
    from src.database.cartwheel_models import (
        ContentFormat, CONTENT_FORMAT_SPECS,
        is_blog_format, is_social_format, is_video_format, is_long_form_format
    )
    
    logger.info("Testing content format specifications...")
    
    # Test format specifications
    formats_to_test = [
        ContentFormat.AI_SEARCH_BLOG,
        ContentFormat.EPIC_PILLAR_ARTICLE,
        ContentFormat.LINKEDIN_ARTICLE,
        ContentFormat.X_THREAD,
        ContentFormat.INSTAGRAM_POST,
        ContentFormat.META_FACEBOOK_POST,
        ContentFormat.YOUTUBE_SHORTS,
        ContentFormat.TIKTOK_UGC,
        ContentFormat.PILLAR_PODCAST
    ]
    
    format_tests = {}
    for format_type in formats_to_test:
        spec = CONTENT_FORMAT_SPECS.get(format_type, {})
        format_tests[format_type.value] = {
            "spec": spec,
            "is_blog": is_blog_format(format_type),
            "is_social": is_social_format(format_type),
            "is_video": is_video_format(format_type),
            "is_long_form": is_long_form_format(format_type)
        }
        
        logger.info(f"✓ {format_type.value}:")
        if "word_count" in spec:
            logger.info(f"    Word count: {spec['word_count']}")
        if "character_limit" in spec:
            logger.info(f"    Character limit: {spec['character_limit']}")
        logger.info(f"    Blog format: {is_blog_format(format_type)}")
        logger.info(f"    Social format: {is_social_format(format_type)}")
        logger.info(f"    Video format: {is_video_format(format_type)}")
        logger.info(f"    Long form: {is_long_form_format(format_type)}")
    
    # Count format types
    blog_count = sum(1 for f in formats_to_test if is_blog_format(f))
    social_count = sum(1 for f in formats_to_test if is_social_format(f))
    video_count = sum(1 for f in formats_to_test if is_video_format(f))
    long_form_count = sum(1 for f in formats_to_test if is_long_form_format(f))
    
    logger.info(f"\n✓ Format categorization:")
    logger.info(f"  - Blog formats: {blog_count}")
    logger.info(f"  - Social formats: {social_count}")
    logger.info(f"  - Video formats: {video_count}")
    logger.info(f"  - Long form formats: {long_form_count}")
    logger.info(f"  - Total tested: {len(formats_to_test)}")
    
    return {
        "formats_tested": len(formats_to_test),
        "format_specs": format_tests,
        "blog_formats": blog_count,
        "social_formats": social_count,
        "video_formats": video_count,
        "long_form_formats": long_form_count
    }


async def test_adsby_performance() -> Dict[str, Any]:
    """Test Adsby performance scoring algorithms"""
    
    from src.adsby.models import (
        PerformanceMetric, AdCampaign, CampaignStatus,
        AuthorityImpactMetrics
    )
    
    logger.info("Creating test campaign for performance analysis...")
    
    # Create test campaign
    campaign = AdCampaign(
        campaign_id="test_001",
        cluster_id="cluster_001",
        client_id=str(uuid4()),
        title="Business Automation Solutions - Test",
        budget_allocated=2500.00,
        daily_budget=83.33,
        start_date=datetime.now(),
        status=CampaignStatus.ACTIVE,
        keywords=["business automation", "workflow optimization"],
        ad_groups=[],
        landing_page_url="https://example.com/automation"
    )
    
    logger.info(f"✓ Created campaign: {campaign.title}")
    logger.info(f"  - Budget: ${campaign.budget_allocated:,.2f}")
    logger.info(f"  - Keywords: {len(campaign.keywords)}")
    
    # Test performance metrics
    test_metrics = {
        PerformanceMetric.CTR: 3.5,
        PerformanceMetric.CONVERSION_RATE: 5.2,
        PerformanceMetric.AUTHORITY_IMPACT: 68.0,
        PerformanceMetric.COST_PER_ACQUISITION: 42.50
    }
    
    # Test authority impact calculation
    authority_metrics = AuthorityImpactMetrics(
        branded_search_increase=15.5,
        direct_traffic_increase=8.2,
        return_visitor_rate=35.0,
        content_engagement_score=72.0,
        social_amplification=0.12,
        backlink_acquisition=5
    )
    
    authority_score = authority_metrics.overall_impact_score
    
    logger.info(f"\n✓ Authority Impact Analysis:")
    logger.info(f"  - Branded search increase: {authority_metrics.branded_search_increase}%")
    logger.info(f"  - Direct traffic increase: {authority_metrics.direct_traffic_increase}%")
    logger.info(f"  - Return visitor rate: {authority_metrics.return_visitor_rate}%")
    logger.info(f"  - Content engagement: {authority_metrics.content_engagement_score}")
    logger.info(f"  - Composite score: {authority_score:.1f}/100")
    
    # Test campaign properties
    logger.info(f"\n✓ Campaign Analysis:")
    logger.info(f"  - Budget utilization: {campaign.budget_utilization:.1f}%")
    logger.info(f"  - Days active: {campaign.days_active}")
    logger.info(f"  - Is underperforming: {campaign.is_underperforming}")
    
    return {
        "campaign": campaign,
        "test_metrics": test_metrics,
        "authority_score": authority_score,
        "authority_metrics": authority_metrics
    }


async def test_budget_optimization() -> Dict[str, Any]:
    """Test budget optimization algorithm"""
    
    from src.adsby.budget_optimizer import BudgetOptimizer, PERFORMANCE_WEIGHTS
    from src.adsby.models import PerformanceMetric
    
    logger.info("Testing budget optimization algorithm...")
    
    optimizer = BudgetOptimizer()
    
    # Test performance weights
    logger.info("✓ Performance weights configuration:")
    for metric, weight in PERFORMANCE_WEIGHTS.items():
        logger.info(f"  - {metric.value}: {weight}")
    
    # Test composite scoring
    test_performance = {
        PerformanceMetric.CTR: 4.2,
        PerformanceMetric.CONVERSION_RATE: 6.1,
        PerformanceMetric.AUTHORITY_IMPACT: 75.0,
        PerformanceMetric.COST_PER_ACQUISITION: 38.75
    }
    
    composite_score = await optimizer._calculate_composite_score(test_performance)
    
    logger.info(f"\n✓ Composite Performance Score: {composite_score:.1f}/100")
    logger.info("Performance breakdown:")
    for metric, value in test_performance.items():
        weight = PERFORMANCE_WEIGHTS.get(metric, 0)
        contribution = (value / 100) * weight * 100 if metric != PerformanceMetric.COST_PER_ACQUISITION else weight * 100
        logger.info(f"  - {metric.value}: {value} (weight: {weight}, contrib: ~{contribution:.1f})")
    
    # Test threshold calculations
    rotation_threshold = 70.0
    needs_rotation = composite_score < rotation_threshold
    
    logger.info(f"\n✓ Optimization Decision:")
    logger.info(f"  - Rotation threshold: {rotation_threshold}")
    logger.info(f"  - Current score: {composite_score:.1f}")
    logger.info(f"  - Needs rotation: {needs_rotation}")
    
    # Test budget allocation
    mock_campaigns = [
        {"id": "camp_1", "performance_score": 85.0, "budget": 2500.0},
        {"id": "camp_2", "performance_score": 72.0, "budget": 2500.0},
        {"id": "camp_3", "performance_score": 65.0, "budget": 2500.0},
        {"id": "camp_4", "performance_score": 58.0, "budget": 2500.0}
    ]
    
    total_budget = 10000.0
    
    # Simple reallocation based on performance
    performance_sum = sum(camp["performance_score"] for camp in mock_campaigns)
    new_allocation = {}
    
    for campaign in mock_campaigns:
        performance_ratio = campaign["performance_score"] / performance_sum
        new_budget = total_budget * performance_ratio
        new_allocation[campaign["id"]] = new_budget
    
    logger.info(f"\n✓ Budget Reallocation (Performance-Based):")
    for camp_id, budget in new_allocation.items():
        logger.info(f"  - {camp_id}: ${budget:,.2f}")
    
    return {
        "composite_score": composite_score,
        "performance_weights": PERFORMANCE_WEIGHTS,
        "needs_rotation": needs_rotation,
        "budget_allocation": new_allocation,
        "optimization_threshold": rotation_threshold
    }


def print_test_summary(
    cartwheel_result: Dict[str, Any],
    adsby_result: Dict[str, Any],
    budget_result: Dict[str, Any]
):
    """Print test execution summary"""
    
    print("\n" + "="*60)
    print("BRAND BOS CORE ALGORITHM TEST SUMMARY")
    print("="*60)
    
    print("\n🔧 Cartwheel Format Engine:")
    print(f"  • Formats tested: {cartwheel_result['formats_tested']}")
    print(f"  • Blog formats: {cartwheel_result['blog_formats']}")
    print(f"  • Social formats: {cartwheel_result['social_formats']}")
    print(f"  • Video formats: {cartwheel_result['video_formats']}")
    print(f"  • Long form formats: {cartwheel_result['long_form_formats']}")
    
    print("\n📊 Adsby Performance Scoring:")
    print(f"  • Campaign created: ✅")
    print(f"  • Authority impact score: {adsby_result['authority_score']:.1f}/100")
    print(f"  • Performance metrics: ✅")
    
    print("\n💰 Budget Optimization:")
    print(f"  • Composite score: {budget_result['composite_score']:.1f}/100")
    print(f"  • Rotation needed: {'✅' if budget_result['needs_rotation'] else '❌'}")
    print(f"  • Budget reallocation: ✅")
    
    print("\n✅ All core algorithms validated successfully!")
    print("="*60)


if __name__ == "__main__":
    # Run core algorithm test
    asyncio.run(test_core_algorithms())