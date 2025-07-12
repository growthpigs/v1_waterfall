#!/usr/bin/env python3
"""
Brand BOS Direct Access Test
Show exactly what can be used RIGHT NOW without any external dependencies
"""

import sys
from pathlib import Path
from datetime import datetime
from uuid import uuid4

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🔧 BRAND BOS DIRECT ACCESS - WHAT WORKS RIGHT NOW")
print("=" * 60)

# 1. Content Format Analysis
print("\n1️⃣  CONTENT FORMAT ANALYSIS (100% Functional)")
print("-" * 40)

from src.database.cartwheel_models import (
    ContentFormat, CONTENT_FORMAT_SPECS,
    is_blog_format, is_social_format, is_video_format, is_long_form_format
)

def analyze_content_formats():
    """Analyze all available content formats"""
    all_formats = list(ContentFormat)
    
    blog_formats = [f for f in all_formats if is_blog_format(f)]
    social_formats = [f for f in all_formats if is_social_format(f)]
    video_formats = [f for f in all_formats if is_video_format(f)]
    long_form_formats = [f for f in all_formats if is_long_form_format(f)]
    
    print(f"📊 Total formats available: {len(all_formats)}")
    print(f"📝 Blog formats: {len(blog_formats)}")
    print(f"📱 Social formats: {len(social_formats)}")
    print(f"🎥 Video formats: {len(video_formats)}")
    print(f"📚 Long-form formats: {len(long_form_formats)}")
    
    print("\n🎯 Format Specifications:")
    for fmt in all_formats[:5]:  # Show first 5
        spec = CONTENT_FORMAT_SPECS.get(fmt, {})
        print(f"  {fmt.value}:")
        if 'word_count' in spec:
            print(f"    📏 Words: {spec['word_count']}")
        if 'character_limit' in spec:
            print(f"    🔤 Chars: {spec['character_limit']}")
        categories = []
        if is_blog_format(fmt): categories.append('Blog')
        if is_social_format(fmt): categories.append('Social')
        if is_video_format(fmt): categories.append('Video')
        if is_long_form_format(fmt): categories.append('Long-form')
        print(f"    📂 Categories: {', '.join(categories) if categories else 'None'}")

analyze_content_formats()

# 2. Campaign Performance Analysis
print("\n\n2️⃣  CAMPAIGN PERFORMANCE ANALYSIS (100% Functional)")
print("-" * 40)

from src.adsby.models import (
    AdCampaign, CampaignStatus, PerformanceMetric,
    AuthorityImpactMetrics, AdGroup
)

def create_sample_campaign():
    """Create and analyze a sample campaign"""
    
    # Create ad groups
    ad_groups = [
        AdGroup(
            name="Business Growth - Primary",
            keywords=[
                {"text": "business growth", "match_type": "broad"},
                {"text": "scale business", "match_type": "phrase"},
                {"text": "[business consulting]", "match_type": "exact"}
            ],
            max_cpc=3.50,
            target_cpa=45.0
        )
    ]
    
    campaign = AdCampaign(
        campaign_id=f"camp_{uuid4().hex[:8]}",
        cluster_id=f"cluster_{uuid4().hex[:8]}",
        client_id=str(uuid4()),
        title="AI-Powered Business Growth Solutions",
        budget_allocated=2500.00,
        daily_budget=83.33,
        start_date=datetime.now(),
        status=CampaignStatus.ACTIVE,
        keywords=["business growth", "ai consulting", "automation"],
        ad_groups=ad_groups,
        landing_page_url="https://example.com/growth-solutions"
    )
    
    print(f"🚀 Campaign: {campaign.title}")
    print(f"💰 Budget: ${campaign.budget_allocated:,.2f}")
    print(f"📅 Daily: ${campaign.daily_budget:.2f}")
    print(f"🎯 Keywords: {len(campaign.keywords)}")
    print(f"📊 Ad Groups: {len(campaign.ad_groups)}")
    print(f"📈 Budget Utilization: {campaign.budget_utilization:.1f}%")
    print(f"⏱️  Days Active: {campaign.days_active}")
    
    return campaign

campaign = create_sample_campaign()

# 3. Authority Impact Measurement
print("\n\n3️⃣  AUTHORITY IMPACT MEASUREMENT (100% Functional)")
print("-" * 40)

def analyze_authority_impact():
    """Analyze authority building impact"""
    
    authority_metrics = AuthorityImpactMetrics(
        branded_search_increase=22.5,  # 22.5% increase in branded searches
        direct_traffic_increase=15.8,   # 15.8% increase in direct traffic
        return_visitor_rate=45.2,       # 45.2% return visitor rate
        content_engagement_score=78.5,  # 78.5/100 engagement score
        social_amplification=0.18,      # 18% social amplification rate
        backlink_acquisition=7          # 7 new backlinks acquired
    )
    
    impact_score = authority_metrics.overall_impact_score
    
    print(f"🎯 Authority Impact Score: {impact_score:.1f}/100")
    print(f"🔍 Branded search increase: {authority_metrics.branded_search_increase}%")
    print(f"🌐 Direct traffic increase: {authority_metrics.direct_traffic_increase}%")
    print(f"🔄 Return visitor rate: {authority_metrics.return_visitor_rate}%")
    print(f"❤️  Content engagement: {authority_metrics.content_engagement_score}/100")
    print(f"📤 Social amplification: {authority_metrics.social_amplification*100:.0f}%")
    print(f"🔗 New backlinks: {authority_metrics.backlink_acquisition}")
    
    return authority_metrics

authority_data = analyze_authority_impact()

# 4. Budget Optimization Algorithm
print("\n\n4️⃣  BUDGET OPTIMIZATION ALGORITHM (100% Functional)")
print("-" * 40)

import asyncio
from src.adsby.budget_optimizer import BudgetOptimizer, PERFORMANCE_WEIGHTS

async def run_budget_optimization():
    """Test budget optimization algorithm"""
    
    optimizer = BudgetOptimizer()
    
    # Test different performance scenarios
    scenarios = [
        {
            "name": "High Performer",
            "metrics": {
                PerformanceMetric.CTR: 5.2,
                PerformanceMetric.CONVERSION_RATE: 8.1,
                PerformanceMetric.AUTHORITY_IMPACT: 85.0,
                PerformanceMetric.COST_PER_ACQUISITION: 28.50
            }
        },
        {
            "name": "Average Performer", 
            "metrics": {
                PerformanceMetric.CTR: 3.1,
                PerformanceMetric.CONVERSION_RATE: 4.5,
                PerformanceMetric.AUTHORITY_IMPACT: 62.0,
                PerformanceMetric.COST_PER_ACQUISITION: 45.75
            }
        },
        {
            "name": "Underperformer",
            "metrics": {
                PerformanceMetric.CTR: 1.8,
                PerformanceMetric.CONVERSION_RATE: 2.1,
                PerformanceMetric.AUTHORITY_IMPACT: 35.0,
                PerformanceMetric.COST_PER_ACQUISITION: 75.25
            }
        }
    ]
    
    print("🏆 Performance Weight Configuration:")
    for metric, weight in PERFORMANCE_WEIGHTS.items():
        print(f"  {metric.value}: {weight*100:.0f}%")
    
    print("\n📊 Campaign Performance Analysis:")
    for scenario in scenarios:
        score = await optimizer._calculate_composite_score(scenario["metrics"])
        needs_rotation = score < 70.0
        
        print(f"\n  {scenario['name']}:")
        print(f"    🎯 Composite Score: {score:.1f}/100")
        print(f"    🔄 Needs Rotation: {'YES' if needs_rotation else 'NO'}")
        for metric, value in scenario["metrics"].items():
            print(f"    📈 {metric.value}: {value}")

# Run async budget optimization
asyncio.run(run_budget_optimization())

# 5. CIA Session Management
print("\n\n5️⃣  CIA SESSION MANAGEMENT (Models Only - No Database)")
print("-" * 40)

from src.database.models import CIASession
from src.config.constants import PhaseStatus, CIAPhase

def demonstrate_cia_session():
    """Demonstrate CIA session model functionality"""
    
    session = CIASession(
        client_id=uuid4(),
        url="https://modernfoundry.com",
        company_name="Modern Foundry",
        kpoi="Roderick Andrews",
        country="United States",
        testimonials_url="https://modernfoundry.com/testimonials",
        status=PhaseStatus.EXECUTING,
        current_phase=CIAPhase.PHASE_1A,
        completed_phases=[],
        total_phases=15,
        total_tokens_used=0,
        handover_count=0
    )
    
    print(f"🏢 Company: {session.company_name}")
    print(f"👤 KPOI: {session.kpoi}")
    print(f"🌍 Country: {session.country}")
    print(f"🔄 Status: {session.status.value}")
    print(f"📊 Current Phase: {session.current_phase.value if session.current_phase else 'None'}")
    print(f"📈 Progress: {session.progress_percentage:.1f}%")
    print(f"✅ Can Proceed: {session.can_proceed()}")
    print(f"➡️  Next Phase: {session.get_next_phase().value if session.get_next_phase() else 'Complete'}")
    print(f"🎯 Total Phases: {session.total_phases}")

demonstrate_cia_session()

# Summary
print("\n\n🎉 SUMMARY: WHAT'S IMMEDIATELY USABLE")
print("=" * 60)
print("✅ Content format analysis and categorization")
print("✅ Campaign creation with performance modeling")
print("✅ Authority impact scoring algorithm")
print("✅ Budget optimization with composite scoring")
print("✅ CIA session state management")
print("✅ All business logic and data models")
print()
print("⚠️  MISSING FOR FULL OPERATION:")
print("❌ Database connection (needs Supabase credentials)")
print("❌ AI integration (needs Anthropic API key)")
print("❌ Live Google Ads API (needs Google credentials)")
print()
print("🚀 IMMEDIATE USAGE:")
print("   • Run algorithms and test business logic")
print("   • Prototype campaign strategies")
print("   • Test content format specifications")
print("   • Model authority impact scenarios")
print("   • Validate budget optimization logic")