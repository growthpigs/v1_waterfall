"""
Example: Client Configuration Management
Shows patterns for managing client preferences and checkbox controls across all systems.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

class ContentFormat(Enum):
    AI_SEARCH_BLOG = "ai_search_blog"
    EPIC_PILLAR_ARTICLE = "epic_pillar_article"
    PILLAR_PODCAST = "pillar_podcast"
    ADVERTORIAL = "advertorial"
    INSTAGRAM_POST = "instagram_post"
    X_THREAD = "x_thread"
    LINKEDIN_ARTICLE = "linkedin_article"
    META_FACEBOOK_POST = "meta_facebook_post"
    TIKTOK_UGC = "tiktok_ugc"
    BLOG_SUPPORTING_1 = "blog_supporting_1"
    BLOG_SUPPORTING_2 = "blog_supporting_2"
    BLOG_SUPPORTING_3 = "blog_supporting_3"
    YOUTUBE_SHORTS = "youtube_shorts"
    TIKTOK_SHORTS = "tiktok_shorts"

class PublishingPlatform(Enum):
    BLOG = "blog"
    INSTAGRAM = "instagram"
    X_TWITTER = "x_twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"

@dataclass
class ClientConfiguration:
    """Complete client configuration for Project Waterfall"""
    client_id: str
    client_name: str
    
    # Content Generation Preferences
    enabled_content_formats: Dict[ContentFormat, bool]
    content_scheduling: Dict[str, Any]
    brand_voice: Dict[str, str]
    visual_style: Dict[str, Any]
    
    # Publishing Platform Settings
    platform_accounts: Dict[PublishingPlatform, Dict[str, Any]]
    posting_schedules: Dict[PublishingPlatform, Dict[str, Any]]
    
    # CIA Intelligence Preferences
    target_audience: Dict[str, Any]
    competitive_focus: List[str]
    authority_goals: Dict[str, Any]
    
    # Adsby Campaign Settings
    ad_budget_allocation: Dict[str, float]
    target_locations: List[str]
    campaign_preferences: Dict[str, Any]
    
    # Notification Settings
    slack_webhook: Optional[str]
    email_notifications: List[str]
    notification_preferences: Dict[str, bool]

class ClientConfigurationManager:
    """Manager for client configuration and preference handling"""
    
    def __init__(self, database_connection):
        self.db = database_connection
        self.default_config = self._get_default_configuration()
    
    def _get_default_configuration(self) -> Dict[str, Any]:
        """Get default configuration template for new clients"""
        return {
            "enabled_content_formats": {
                ContentFormat.AI_SEARCH_BLOG: True,
                ContentFormat.EPIC_PILLAR_ARTICLE: True,
                ContentFormat.PILLAR_PODCAST: False,
                ContentFormat.ADVERTORIAL: False,
                ContentFormat.INSTAGRAM_POST: True,
                ContentFormat.X_THREAD: True,
                ContentFormat.LINKEDIN_ARTICLE: True,
                ContentFormat.META_FACEBOOK_POST: True,
                ContentFormat.TIKTOK_UGC: False,
                ContentFormat.BLOG_SUPPORTING_1: True,
                ContentFormat.BLOG_SUPPORTING_2: False,
                ContentFormat.BLOG_SUPPORTING_3: False,
                ContentFormat.YOUTUBE_SHORTS: False,
                ContentFormat.TIKTOK_SHORTS: False,
            },
            "content_scheduling": {
                "content_per_week": 3,
                "publishing_days": ["Tuesday", "Thursday", "Saturday"],
                "timezone": "America/New_York",
                "advance_scheduling_days": 7
            },
            "brand_voice": {
                "tone": "professional_friendly",
                "personality": "authoritative_helpful",
                "formality_level": "business_casual",
                "target_reading_level": "grade_10"
            },
            "visual_style": {
                "color_palette": "professional_blue_white",
                "image_style": "clean_modern",
                "logo_usage": "brand_consistent",
                "visual_mood": "trustworthy_authoritative"
            },
            "platform_accounts": {
                PublishingPlatform.BLOG: {"enabled": True, "auto_publish": True},
                PublishingPlatform.INSTAGRAM: {"enabled": True, "auto_publish": False},
                PublishingPlatform.X_TWITTER: {"enabled": True, "auto_publish": False},
                PublishingPlatform.LINKEDIN: {"enabled": True, "auto_publish": False},
                PublishingPlatform.FACEBOOK: {"enabled": True, "auto_publish": False},
                PublishingPlatform.TIKTOK: {"enabled": False, "auto_publish": False},
                PublishingPlatform.YOUTUBE: {"enabled": False, "auto_publish": False},
            },
            "posting_schedules": {
                PublishingPlatform.INSTAGRAM: {"optimal_time": "18:00", "frequency": "daily"},
                PublishingPlatform.X_TWITTER: {"optimal_time": "09:00", "frequency": "3x_daily"},
                PublishingPlatform.LINKEDIN: {"optimal_time": "08:00", "frequency": "daily"},
                PublishingPlatform.FACEBOOK: {"optimal_time": "19:00", "frequency": "daily"},
            },
            "target_audience": {
                "primary_demographic": "business_professionals",
                "age_range": "30-55",
                "industry_focus": ["professional_services", "finance", "consulting"],
                "pain_points": ["scaling_business", "client_acquisition", "authority_building"]
            },
            "competitive_focus": [],  # To be filled during CIA analysis
            "authority_goals": {
                "thought_leadership_areas": [],
                "target_recognition_level": "industry_expert",
                "content_authority_score_target": 85
            },
            "ad_budget_allocation": {
                "monthly_total": 10000.0,
                "max_active_campaigns": 4,
                "campaign_budget": 2500.0,
                "performance_threshold": 70.0
            },
            "target_locations": ["United States"],
            "campaign_preferences": {
                "bid_strategy": "target_cpa",
                "campaign_type": "search",
                "ad_rotation": "optimize_for_conversions"
            },
            "notification_preferences": {
                "convergence_alerts": True,
                "content_approval_required": True,
                "performance_alerts": True,
                "budget_rotation_approval": True,
                "weekly_reports": True
            }
        }
    
    async def create_client_configuration(
        self, 
        client_id: str, 
        client_name: str,
        custom_preferences: Dict[str, Any] = None
    ) -> ClientConfiguration:
        """Create new client configuration with defaults and custom preferences"""
        
        # Start with default configuration
        config_dict = self.default_config.copy()
        
        # Apply custom preferences if provided
        if custom_preferences:
            config_dict = self._merge_configurations(config_dict, custom_preferences)
        
        # Create configuration object
        config = ClientConfiguration(
            client_id=client_id,
            client_name=client_name,
            enabled_content_formats=config_dict["enabled_content_formats"],
            content_scheduling=config_dict["content_scheduling"],
            brand_voice=config_dict["brand_voice"],
            visual_style=config_dict["visual_style"],
            platform_accounts=config_dict["platform_accounts"],
            posting_schedules=config_dict["posting_schedules"],
            target_audience=config_dict["target_audience"],
            competitive_focus=config_dict["competitive_focus"],
            authority_goals=config_dict["authority_goals"],
            ad_budget_allocation=config_dict["ad_budget_allocation"],
            target_locations=config_dict["target_locations"],
            campaign_preferences=config_dict["campaign_preferences"],
            slack_webhook=custom_preferences.get("slack_webhook") if custom_preferences else None,
            email_notifications=custom_preferences.get("email_notifications", []) if custom_preferences else [],
            notification_preferences=config_dict["notification_preferences"]
        )
        
        # Save to database
        await self._save_configuration(config)
        
        return config
    
    async def update_client_configuration(
        self, 
        client_id: str, 
        updates: Dict[str, Any]
    ) -> ClientConfiguration:
        """Update existing client configuration"""
        
        # Load existing configuration
        existing_config = await self._load_configuration(client_id)
        
        # Apply updates
        updated_config_dict = self._apply_configuration_updates(existing_config, updates)
        
        # Create updated configuration object
        updated_config = ClientConfiguration(**updated_config_dict)
        
        # Save to database
        await self._save_configuration(updated_config)
        
        return updated_config
    
    def _merge_configurations(
        self, 
        base_config: Dict[str, Any], 
        custom_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge custom configuration with base configuration"""
        
        merged = base_config.copy()
        
        for key, value in custom_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Deep merge for dictionary values
                merged[key] = {**merged[key], **value}
            else:
                # Direct replacement for other types
                merged[key] = value
        
        return merged
    
    async def get_enabled_content_formats(self, client_id: str) -> List[ContentFormat]:
        """Get list of enabled content formats for client"""
        
        config = await self._load_configuration(client_id)
        
        enabled_formats = [
            format_type for format_type, enabled in config.enabled_content_formats.items()
            if enabled
        ]
        
        return enabled_formats
    
    async def get_platform_posting_schedule(
        self, 
        client_id: str, 
        platform: PublishingPlatform
    ) -> Dict[str, Any]:
        """Get posting schedule for specific platform"""
        
        config = await self._load_configuration(client_id)
        
        if platform not in config.platform_accounts or not config.platform_accounts[platform]["enabled"]:
            return {"enabled": False}
        
        schedule = config.posting_schedules.get(platform, {})
        schedule["enabled"] = True
        schedule["auto_publish"] = config.platform_accounts[platform]["auto_publish"]
        
        return schedule
    
    async def get_content_generation_preferences(self, client_id: str) -> Dict[str, Any]:
        """Get content generation preferences for Cartwheel system"""
        
        config = await self._load_configuration(client_id)
        
        return {
            "enabled_formats": [
                format_type.value for format_type, enabled in config.enabled_content_formats.items()
                if enabled
            ],
            "brand_voice": config.brand_voice,
            "visual_style": config.visual_style,
            "target_audience": config.target_audience,
            "scheduling": config.content_scheduling
        }
    
    async def get_adsby_campaign_settings(self, client_id: str) -> Dict[str, Any]:
        """Get Adsby campaign settings for ad automation"""
        
        config = await self._load_configuration(client_id)
        
        return {
            "budget_allocation": config.ad_budget_allocation,
            "target_locations": config.target_locations,
            "campaign_preferences": config.campaign_preferences,
            "target_audience": config.target_audience,
            "authority_goals": config.authority_goals
        }
    
    async def validate_configuration(self, config: ClientConfiguration) -> Dict[str, Any]:
        """Validate client configuration for completeness and correctness"""
        
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check content format selection
        enabled_formats = [f for f, enabled in config.enabled_content_formats.items() if enabled]
        if len(enabled_formats) < 3:
            validation_results["warnings"].append(
                "Less than 3 content formats enabled. Consider enabling more for better content variety."
            )
        
        # Check platform account setup
        enabled_platforms = [p for p, settings in config.platform_accounts.items() if settings["enabled"]]
        if len(enabled_platforms) < 2:
            validation_results["warnings"].append(
                "Less than 2 platforms enabled. Consider expanding reach across more platforms."
            )
        
        # Check notification setup
        if not config.slack_webhook and not config.email_notifications:
            validation_results["errors"].append(
                "No notification methods configured. At least one notification method required."
            )
            validation_results["valid"] = False
        
        # Check budget allocation
        if config.ad_budget_allocation["monthly_total"] > 15000:
            validation_results["warnings"].append(
                "Monthly ad budget exceeds typical allocation. Verify budget limits."
            )
        
        # Check target audience definition
        if not config.target_audience.get("pain_points"):
            validation_results["recommendations"].append(
                "Define target audience pain points for better content targeting."
            )
        
        # Check brand voice definition
        if not all(config.brand_voice.values()):
            validation_results["recommendations"].append(
                "Complete brand voice definition for consistent content generation."
            )
        
        return validation_results
    
    async def export_configuration(self, client_id: str, format: str = "json") -> str:
        """Export client configuration in specified format"""
        
        config = await self._load_configuration(client_id)
        
        if format == "json":
            # Convert to JSON-serializable format
            config_dict = {
                "client_id": config.client_id,
                "client_name": config.client_name,
                "enabled_content_formats": {f.value: enabled for f, enabled in config.enabled_content_formats.items()},
                "content_scheduling": config.content_scheduling,
                "brand_voice": config.brand_voice,
                "visual_style": config.visual_style,
                "platform_accounts": {p.value: settings for p, settings in config.platform_accounts.items()},
                "posting_schedules": {p.value: schedule for p, schedule in config.posting_schedules.items()},
                "target_audience": config.target_audience,
                "competitive_focus": config.competitive_focus,
                "authority_goals": config.authority_goals,
                "ad_budget_allocation": config.ad_budget_allocation,
                "target_locations": config.target_locations,
                "campaign_preferences": config.campaign_preferences,
                "notification_preferences": config.notification_preferences
            }
            
            return json.dumps(config_dict, indent=2)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def import_configuration(
        self, 
        client_id: str, 
        config_data: str, 
        format: str = "json"
    ) -> ClientConfiguration:
        """Import client configuration from external source"""
        
        if format == "json":
            config_dict = json.loads(config_data)
            
            # Convert back to enum types
            enabled_formats = {
                ContentFormat(f): enabled 
                for f, enabled in config_dict["enabled_content_formats"].items()
            }
            
            platform_accounts = {
                PublishingPlatform(p): settings 
                for p, settings in config_dict["platform_accounts"].items()
            }
            
            posting_schedules = {
                PublishingPlatform(p): schedule 
                for p, schedule in config_dict["posting_schedules"].items()
            }
            
            config = ClientConfiguration(
                client_id=client_id,
                client_name=config_dict["client_name"],
                enabled_content_formats=enabled_formats,
                content_scheduling=config_dict["content_scheduling"],
                brand_voice=config_dict["brand_voice"],
                visual_style=config_dict["visual_style"],
                platform_accounts=platform_accounts,
                posting_schedules=posting_schedules,
                target_audience=config_dict["target_audience"],
                competitive_focus=config_dict["competitive_focus"],
                authority_goals=config_dict["authority_goals"],
                ad_budget_allocation=config_dict["ad_budget_allocation"],
                target_locations=config_dict["target_locations"],
                campaign_preferences=config_dict["campaign_preferences"],
                slack_webhook=config_dict.get("slack_webhook"),
                email_notifications=config_dict.get("email_notifications", []),
                notification_preferences=config_dict["notification_preferences"]
            )
            
            await self._save_configuration(config)
            return config
        
        else:
            raise ValueError(f"Unsupported import format: {format}")
    
    async def _load_configuration(self, client_id: str) -> ClientConfiguration:
        """Load configuration from database"""
        # Mock implementation - replace with actual database query
        pass
    
    async def _save_configuration(self, config: ClientConfiguration):
        """Save configuration to database"""
        # Mock implementation - replace with actual database save
        pass

# Example usage pattern:
async def setup_new_client_workflow(client_name: str, initial_preferences: Dict[str, Any]):
    """Example of complete client configuration setup workflow"""
    
    config_manager = ClientConfigurationManager(database_connection=None)
    
    # Create client configuration
    client_id = f"client_{client_name.lower().replace(' ', '_')}"
    config = await config_manager.create_client_configuration(
        client_id, client_name, initial_preferences
    )
    
    # Validate configuration
    validation = await config_manager.validate_configuration(config)
    
    if not validation["valid"]:
        print(f"Configuration errors: {validation['errors']}")
        return None
    
    if validation["warnings"]:
        print(f"Configuration warnings: {validation['warnings']}")
    
    # Get specific settings for different systems
    content_prefs = await config_manager.get_content_generation_preferences(client_id)
    adsby_settings = await config_manager.get_adsby_campaign_settings(client_id)
    enabled_formats = await config_manager.get_enabled_content_formats(client_id)
    
    return {
        "config": config,
        "content_preferences": content_prefs,
        "adsby_settings": adsby_settings,
        "enabled_formats": enabled_formats,
        "validation": validation
    }
