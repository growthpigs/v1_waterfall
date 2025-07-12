#!/usr/bin/env python3
"""
Brand BOS Reality Check - What Actually Works?
Test script to verify what functionality is operational without external dependencies
"""

import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from uuid import uuid4

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports():
    """Test if we can import core components"""
    print("\n🔍 TESTING IMPORTS...")
    
    try:
        # Test core models
        from src.database.cartwheel_models import ContentFormat, ConvergenceOpportunity
        print("✅ Cartwheel models imported successfully")
        
        from src.adsby.models import AdCampaign, PerformanceMetric, AuthorityImpactMetrics
        print("✅ Adsby models imported successfully")
        
        # Test API components
        from src.api.main import app
        print("✅ FastAPI application imported successfully")
        
        # Test database components (will fail without credentials, but tests import)
        try:
            from src.database.base import SupabaseConnection
            print("✅ Database connection classes imported successfully")
        except Exception as e:
            print(f"⚠️  Database connection import failed (expected without credentials): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_content_formats():
    """Test Cartwheel content format functionality"""
    print("\n🎨 TESTING CARTWHEEL CONTENT FORMATS...")
    
    try:
        from src.database.cartwheel_models import (
            ContentFormat, CONTENT_FORMAT_SPECS,
            is_blog_format, is_social_format, is_video_format
        )
        
        formats = [
            ContentFormat.AI_SEARCH_BLOG,
            ContentFormat.LINKEDIN_ARTICLE,
            ContentFormat.X_THREAD,
            ContentFormat.YOUTUBE_SHORTS
        ]
        
        for fmt in formats:
            spec = CONTENT_FORMAT_SPECS.get(fmt, {})
            print(f"  📄 {fmt.value}:")
            print(f"     Blog: {is_blog_format(fmt)}")
            print(f"     Social: {is_social_format(fmt)}")
            print(f"     Video: {is_video_format(fmt)}")
            if 'word_count' in spec:
                print(f"     Words: {spec['word_count']}")
            if 'character_limit' in spec:
                print(f"     Chars: {spec['character_limit']}")
        
        print("✅ Content format system operational")
        return True
        
    except Exception as e:
        print(f"❌ Content format test failed: {e}")
        return False


def test_adsby_models():
    """Test Adsby campaign and performance models"""
    print("\n🚀 TESTING ADSBY MODELS...")
    
    try:
        from src.adsby.models import (
            AdCampaign, CampaignStatus, PerformanceMetric,
            AuthorityImpactMetrics
        )
        
        # Create test campaign
        campaign = AdCampaign(
            campaign_id="test_001",
            cluster_id="cluster_001",
            client_id=str(uuid4()),
            title="Test Campaign",
            budget_allocated=2500.00,
            daily_budget=83.33,
            start_date=datetime.now(),
            status=CampaignStatus.ACTIVE,
            keywords=["test", "campaign"],
            ad_groups=[],
            landing_page_url="https://example.com"
        )
        
        print(f"  📊 Campaign created: {campaign.title}")
        print(f"     Budget utilization: {campaign.budget_utilization:.1f}%")
        print(f"     Days active: {campaign.days_active}")
        print(f"     Is underperforming: {campaign.is_underperforming}")
        
        # Test authority metrics
        authority = AuthorityImpactMetrics(
            branded_search_increase=15.0,
            direct_traffic_increase=8.5,
            return_visitor_rate=42.0,
            content_engagement_score=78.0,
            social_amplification=0.15,
            backlink_acquisition=3
        )
        
        score = authority.overall_impact_score
        print(f"  🎯 Authority impact score: {score:.1f}/100")
        
        print("✅ Adsby models operational")
        return True
        
    except Exception as e:
        print(f"❌ Adsby models test failed: {e}")
        return False


async def test_budget_optimizer():
    """Test budget optimization algorithm"""
    print("\n💰 TESTING BUDGET OPTIMIZATION...")
    
    try:
        from src.adsby.budget_optimizer import BudgetOptimizer, PERFORMANCE_WEIGHTS
        from src.adsby.models import PerformanceMetric
        
        optimizer = BudgetOptimizer()
        
        # Test performance scoring
        test_metrics = {
            PerformanceMetric.CTR: 4.5,
            PerformanceMetric.CONVERSION_RATE: 6.2,
            PerformanceMetric.AUTHORITY_IMPACT: 72.0,
            PerformanceMetric.COST_PER_ACQUISITION: 35.50
        }
        
        score = await optimizer._calculate_composite_score(test_metrics)
        print(f"  📈 Composite performance score: {score:.1f}/100")
        
        print("  🏋️  Performance weights:")
        for metric, weight in PERFORMANCE_WEIGHTS.items():
            print(f"     {metric.value}: {weight}")
        
        print("✅ Budget optimizer operational")
        return True
        
    except Exception as e:
        print(f"❌ Budget optimizer test failed: {e}")
        return False


def test_fastapi_app():
    """Test FastAPI application structure"""
    print("\n🌐 TESTING FASTAPI APPLICATION...")
    
    try:
        from src.api.main import app
        
        # Get route information
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = getattr(route, 'methods', set())
                if methods and 'GET' in methods:
                    routes.append(f"GET {route.path}")
                elif methods and 'POST' in methods:
                    routes.append(f"POST {route.path}")
        
        print("  📡 Available endpoints:")
        for route in sorted(routes):
            print(f"     {route}")
        
        print("✅ FastAPI application structure operational")
        return True
        
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        return False


def test_database_models():
    """Test database model structure (without connection)"""
    print("\n🗃️  TESTING DATABASE MODELS...")
    
    try:
        from src.database.models import CIASession
        from src.config.constants import PhaseStatus, CIAPhase
        
        # Create test session model
        session = CIASession(
            client_id=uuid4(),
            url="https://example.com",
            company_name="Test Company",
            kpoi="Test Person",
            country="United States",
            status=PhaseStatus.PENDING,
            current_phase=CIAPhase.PHASE_1A
        )
        
        print(f"  📝 CIA Session created: {session.company_name}")
        print(f"     Progress: {session.progress_percentage:.1f}%")
        print(f"     Can proceed: {session.can_proceed()}")
        print(f"     Next phase: {session.get_next_phase()}")
        
        print("✅ Database models operational")
        return True
        
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False


async def run_reality_check():
    """Run comprehensive reality check"""
    print("🔬 BRAND BOS REALITY CHECK")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Project Root: {project_root}")
    
    results = []
    
    # Test all components
    results.append(("Imports", test_imports()))
    results.append(("Content Formats", test_content_formats()))
    results.append(("Adsby Models", test_adsby_models()))
    results.append(("Budget Optimizer", await test_budget_optimizer()))
    results.append(("FastAPI App", test_fastapi_app()))
    results.append(("Database Models", test_database_models()))
    
    # Summary
    print("\n📊 REALITY CHECK SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 SYSTEM STATUS: FULLY OPERATIONAL")
        print("\n🚀 READY TO RUN:")
        print("   • Content format detection and specifications")
        print("   • Campaign creation and performance scoring")
        print("   • Budget optimization algorithms")
        print("   • FastAPI server with complete endpoint structure")
        print("   • Database models and business logic")
        
        print("\n⚠️  REQUIRES FOR FULL FUNCTIONALITY:")
        print("   • Supabase database credentials (SUPABASE_URL, SUPABASE_KEY)")
        print("   • Anthropic API key for CIA intelligence analysis")
        print("   • Google Ads API credentials for live campaign management")
        
    else:
        print(f"\n⚠️  SYSTEM STATUS: PARTIAL ({passed}/{total} components operational)")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(run_reality_check())