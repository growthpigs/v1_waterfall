"""
Analytics API Routes for Brand BOS
Handles Google Analytics, Search Console integration and cross-platform attribution
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from pydantic import BaseModel, Field

from ...integrations.google_oauth import GoogleOAuthManager, is_client_connected
from ...integrations.google_analytics import GoogleAnalyticsClient, get_client_ga4_summary
from ...integrations.google_search_console import GoogleSearchConsoleClient, get_site_search_summary
from ...integrations.utm_automation import UTMGenerator, UTMAnalyzer, create_social_promotion_urls
from ...database.cartwheel_models import ContentPiece

router = APIRouter()

# Dependency injection
async def get_oauth_manager() -> GoogleOAuthManager:
    """Get Google OAuth manager instance"""
    # In production, this would come from app state or configuration
    return GoogleOAuthManager(
        client_secrets_file="config/google_oauth_secrets.json",
        token_storage_dir="tokens"
    )


# Request/Response Models
class OAuthInitRequest(BaseModel):
    """Request to initialize OAuth flow"""
    client_id: UUID
    redirect_uri: Optional[str] = "http://localhost:8080/oauth/callback"


class OAuthCallbackRequest(BaseModel):
    """Request to handle OAuth callback"""
    client_id: UUID
    authorization_code: str


class UTMGenerationRequest(BaseModel):
    """Request to generate UTM parameters"""
    content_id: str
    content_title: str
    content_format: str
    base_url: str
    source: str
    medium: str
    variation: str = "A"
    version: str = "v1"
    custom_term: Optional[str] = None


class AnalyticsReportRequest(BaseModel):
    """Request for analytics report"""
    client_id: UUID
    property_id: Optional[str] = None
    site_url: Optional[str] = None
    start_date: str = Field(default_factory=lambda: (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
    end_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    campaign_filter: Optional[str] = None


# OAuth Management Endpoints
@router.post("/oauth/init")
async def initialize_oauth(
    request: OAuthInitRequest,
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """Initialize Google OAuth flow for a client"""
    try:
        auth_url = await oauth_manager.get_authorization_url(str(request.client_id))
        
        return {
            "authorization_url": auth_url,
            "client_id": str(request.client_id),
            "scopes": [
                "Google Analytics 4",
                "Google Search Console", 
                "Google Tag Manager",
                "YouTube Analytics"
            ],
            "instructions": "Visit the authorization URL to grant permissions, then return with the authorization code"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize OAuth: {str(e)}")


@router.post("/oauth/callback")
async def handle_oauth_callback(
    request: OAuthCallbackRequest,
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """Handle OAuth callback and store credentials"""
    try:
        success = await oauth_manager.handle_oauth_callback(
            authorization_code=request.authorization_code,
            client_id=str(request.client_id)
        )
        
        if success:
            return {
                "status": "success",
                "message": "Google Analytics integration completed successfully",
                "client_id": str(request.client_id),
                "connected_services": [
                    "Google Analytics 4",
                    "Google Search Console",
                    "Google Tag Manager"
                ]
            }
        else:
            raise HTTPException(status_code=400, detail="OAuth callback failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback error: {str(e)}")


@router.get("/oauth/status/{client_id}")
async def get_oauth_status(
    client_id: UUID,
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """Get OAuth connection status for a client"""
    try:
        is_connected = await is_client_connected(oauth_manager, str(client_id))
        
        if is_connected:
            # Get connected accounts info
            accounts = await oauth_manager.list_connected_accounts()
            client_account = next((acc for acc in accounts if acc.get("client_id") == str(client_id)), None)
            
            return {
                "connected": True,
                "client_id": str(client_id),
                "account_info": client_account,
                "services_available": [
                    "Google Analytics 4",
                    "Google Search Console", 
                    "Google Tag Manager"
                ]
            }
        else:
            return {
                "connected": False,
                "client_id": str(client_id),
                "message": "No valid Google credentials found"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check OAuth status: {str(e)}")


@router.delete("/oauth/revoke/{client_id}")
async def revoke_oauth(
    client_id: UUID,
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """Revoke OAuth credentials for a client"""
    try:
        success = await oauth_manager.revoke_credentials(str(client_id))
        
        if success:
            return {
                "status": "revoked",
                "client_id": str(client_id),
                "message": "Google Analytics integration has been disconnected"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to revoke credentials")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke OAuth: {str(e)}")


# UTM Generation Endpoints
@router.post("/utm/generate")
async def generate_utm_parameters(request: UTMGenerationRequest):
    """Generate UTM parameters for content tracking"""
    try:
        from ...integrations.utm_automation import UTMSource, UTMMedium, BBOSTask
        from ...database.cartwheel_models import ContentFormat
        
        # Create mock content piece for UTM generation
        content_piece = ContentPiece(
            id=request.content_id,
            title=request.content_title,
            format=ContentFormat(request.content_format),
            cluster_id="test",
            client_id=UUID("00000000-0000-0000-0000-000000000000"),
            content_brief="Mock content for UTM generation",
            target_word_count=1000,
            seo_keywords=[request.custom_term] if request.custom_term else [],
            content_status="published"
        )
        
        generator = UTMGenerator()
        
        utm_params = generator.generate_content_utm(
            content_piece=content_piece,
            source=UTMSource(request.source),
            medium=UTMMedium(request.medium),
            variation=request.variation,
            version=request.version,
            custom_term=request.custom_term
        )
        
        # Add UTM to URL
        utm_url = generator.add_utm_to_url(request.base_url, utm_params)
        
        return {
            "utm_parameters": utm_params.to_dict(),
            "utm_url": utm_url,
            "campaign_name": utm_params.campaign,
            "content_id": utm_params.content,
            "tracking_info": {
                "variation": request.variation,
                "version": request.version,
                "task_type": generator._get_task_from_format(content_piece.format).value
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"UTM generation failed: {str(e)}")


@router.post("/utm/social-set")
async def generate_social_utm_set(
    content_id: str,
    content_title: str,
    content_format: str,
    base_url: str,
    variation: str = "A"
):
    """Generate complete UTM set for social promotion"""
    try:
        from ...database.cartwheel_models import ContentFormat
        
        # Create mock content piece
        content_piece = ContentPiece(
            id=content_id,
            title=content_title,
            format=ContentFormat(content_format),
            cluster_id="test",
            client_id=UUID("00000000-0000-0000-0000-000000000000"),
            content_brief="Mock content for social UTMs",
            target_word_count=1000,
            content_status="published"
        )
        
        utm_urls = create_social_promotion_urls(content_piece, base_url, variation)
        
        return {
            "content_id": content_id,
            "variation": variation,
            "social_urls": utm_urls,
            "platforms": list(utm_urls.keys()),
            "ready_for_posting": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Social UTM generation failed: {str(e)}")


# Analytics Data Endpoints
@router.get("/ga4/properties/{client_id}")
async def get_ga4_properties(
    client_id: UUID,
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """Get available GA4 properties for a client"""
    try:
        ga_client = GoogleAnalyticsClient(oauth_manager)
        properties = await ga_client.get_ga4_properties(str(client_id))
        
        return {
            "client_id": str(client_id),
            "properties": properties,
            "count": len(properties)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get GA4 properties: {str(e)}")


@router.post("/ga4/utm-performance")
async def get_utm_performance(
    request: AnalyticsReportRequest,
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """Get UTM campaign performance from GA4"""
    try:
        ga_client = GoogleAnalyticsClient(oauth_manager)
        
        utm_data = await ga_client.get_utm_performance(
            client_id=str(request.client_id),
            property_id=request.property_id,
            start_date=request.start_date,
            end_date=request.end_date,
            utm_campaign_filter=request.campaign_filter
        )
        
        # Analyze BBOS campaigns
        analyzer = UTMAnalyzer()
        performance_by_variation = analyzer.analyze_performance_by_variation(
            [{"utm_campaign": utm.utm_campaign, "sessions": utm.metrics.sessions, 
              "conversions": utm.metrics.conversions, "revenue": utm.metrics.revenue} 
             for utm in utm_data]
        )
        
        return {
            "client_id": str(request.client_id),
            "date_range": {"start": request.start_date, "end": request.end_date},
            "utm_campaigns": [
                {
                    "source": utm.utm_source,
                    "medium": utm.utm_medium,
                    "campaign": utm.utm_campaign,
                    "term": utm.utm_term,
                    "content": utm.utm_content,
                    "metrics": utm.metrics.to_dict()
                }
                for utm in utm_data
            ],
            "performance_by_variation": performance_by_variation,
            "total_campaigns": len(utm_data),
            "bbos_campaigns": len([utm for utm in utm_data if "BBOS" in utm.utm_campaign])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"UTM performance analysis failed: {str(e)}")


@router.post("/ga4/content-performance")
async def get_content_performance(
    request: AnalyticsReportRequest,
    page_path: str = Query(..., description="Page path to analyze"),
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """Get performance data for specific content"""
    try:
        ga_client = GoogleAnalyticsClient(oauth_manager)
        
        content_perf = await ga_client.get_content_performance(
            client_id=str(request.client_id),
            page_path=page_path,
            property_id=request.property_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return {
            "content_id": content_perf.content_id,
            "page_path": page_path,
            "date_range": content_perf.date_range,
            "total_metrics": content_perf.total_metrics.to_dict(),
            "utm_breakdown": [
                {
                    "source": utm.utm_source,
                    "medium": utm.utm_medium,
                    "campaign": utm.utm_campaign,
                    "metrics": utm.metrics.to_dict()
                }
                for utm in content_perf.utm_breakdown
            ],
            "top_sources": content_perf.top_sources
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content performance analysis failed: {str(e)}")


@router.post("/ga4/authority-metrics")
async def get_authority_metrics(
    request: AnalyticsReportRequest,
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """Calculate authority impact metrics from GA4 data"""
    try:
        ga_client = GoogleAnalyticsClient(oauth_manager)
        
        authority_metrics = await ga_client.get_authority_impact_metrics(
            client_id=str(request.client_id),
            property_id=request.property_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # Calculate composite authority score
        composite_score = (
            authority_metrics.get("direct_traffic_increase", 0) * 0.3 +
            authority_metrics.get("branded_search_increase", 0) * 0.3 +
            authority_metrics.get("content_engagement_score", 0) * 0.4
        )
        
        return {
            "client_id": str(request.client_id),
            "date_range": {"start": request.start_date, "end": request.end_date},
            "authority_metrics": authority_metrics,
            "composite_authority_score": min(max(composite_score, 0), 100),
            "score_breakdown": {
                "direct_traffic_weight": 0.3,
                "branded_search_weight": 0.3,
                "content_engagement_weight": 0.4
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authority metrics calculation failed: {str(e)}")


# Search Console Endpoints
@router.get("/gsc/properties/{client_id}")
async def get_search_console_properties(
    client_id: UUID,
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """Get available Search Console properties"""
    try:
        gsc_client = GoogleSearchConsoleClient(oauth_manager)
        properties = await gsc_client.get_search_console_properties(str(client_id))
        
        return {
            "client_id": str(client_id),
            "properties": properties,
            "count": len(properties)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Search Console properties: {str(e)}")


@router.post("/gsc/keyword-performance")
async def get_keyword_performance(
    request: AnalyticsReportRequest,
    min_impressions: int = Query(10, description="Minimum impressions filter"),
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """Get keyword performance from Search Console"""
    try:
        gsc_client = GoogleSearchConsoleClient(oauth_manager)
        
        keyword_data = await gsc_client.get_keyword_performance(
            client_id=str(request.client_id),
            site_url=request.site_url,
            start_date=request.start_date,
            end_date=request.end_date,
            min_impressions=min_impressions
        )
        
        return {
            "client_id": str(request.client_id),
            "site_url": request.site_url,
            "date_range": {"start": request.start_date, "end": request.end_date},
            "keywords": [
                {
                    "query": kw.query,
                    "page": kw.page,
                    "metrics": kw.metrics.to_dict(),
                    "click_value": kw.click_value
                }
                for kw in keyword_data[:50]  # Top 50 keywords
            ],
            "total_keywords": len(keyword_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword performance analysis failed: {str(e)}")


# Summary Dashboard Endpoints
@router.get("/dashboard/{client_id}")
async def get_analytics_dashboard(
    client_id: UUID,
    days: int = Query(30, description="Number of days for analysis"),
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """Get comprehensive analytics dashboard data"""
    try:
        # Check OAuth status
        is_connected = await is_client_connected(oauth_manager, str(client_id))
        
        if not is_connected:
            return {
                "client_id": str(client_id),
                "connected": False,
                "message": "Google Analytics not connected. Please complete OAuth setup."
            }
        
        # Get GA4 summary
        ga4_summary = await get_client_ga4_summary(oauth_manager, str(client_id), days)
        
        return {
            "client_id": str(client_id),
            "connected": True,
            "period_days": days,
            "ga4_summary": ga4_summary,
            "last_updated": datetime.now().isoformat(),
            "available_reports": [
                "utm_performance",
                "content_performance", 
                "authority_metrics",
                "keyword_performance"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data retrieval failed: {str(e)}")


@router.get("/test/utm-analysis")
async def test_utm_analysis():
    """Test UTM analysis without requiring OAuth"""
    try:
        analyzer = UTMAnalyzer()
        
        # Mock UTM data for testing
        test_data = [
            {"utm_campaign": "A-A_BBOS_pillar_article_v1", "sessions": 150, "conversions": 12, "revenue": 1200.0},
            {"utm_campaign": "A-B_BBOS_pillar_article_v1", "sessions": 120, "conversions": 8, "revenue": 800.0},
            {"utm_campaign": "A-A_BBOS_social_promotion_v2", "sessions": 89, "conversions": 15, "revenue": 1500.0},
            {"utm_campaign": "regular_campaign", "sessions": 200, "conversions": 10, "revenue": 1000.0}
        ]
        
        performance_by_variation = analyzer.analyze_performance_by_variation(test_data)
        best_variation = analyzer.get_best_performing_variation(test_data, "conversions")
        
        return {
            "test_data": test_data,
            "performance_by_variation": performance_by_variation,
            "best_performing_variation": best_variation,
            "bbos_campaigns_detected": len([d for d in test_data if "BBOS" in d["utm_campaign"]]),
            "utm_analysis_functional": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"UTM analysis test failed: {str(e)}")