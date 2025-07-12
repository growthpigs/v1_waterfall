"""
Example: Human-in-Loop Workflow Patterns
Shows Slack + Email notification patterns for CIA mandatory pause points.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class NotificationType(Enum):
    DATAFORSEO_KEYWORDS = "dataforseo_keywords"
    PERPLEXITY_RESEARCH = "perplexity_research"
    TESTIMONIALS_REQUEST = "testimonials_request"
    PHASE_COMPLETION = "phase_completion"
    CONTEXT_HANDOVER = "context_handover"

@dataclass
class HumanLoopState:
    """State management for human-in-loop workflows"""
    session_id: str
    phase_id: str
    notification_type: NotificationType
    data: Dict[str, Any]
    sent_at: str
    responded_at: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    status: str = "waiting"  # waiting, completed, expired

class SlackNotifier:
    """Slack integration for human-in-loop notifications"""
    
    def __init__(self, webhook_url: str, channel: str = "#waterfall-alerts"):
        self.webhook_url = webhook_url
        self.channel = channel
    
    async def send_dataforseo_notification(self, session_id: str, keywords: List[str]) -> bool:
        """Send notification for DataForSEO keyword lookup (Phase 2A)"""
        message = {
            "channel": self.channel,
            "username": "CIA Waterfall Bot",
            "icon_emoji": ":mag:",
            "attachments": [
                {
                    "color": "warning",
                    "title": "🔍 CIA Phase 2A: DataForSEO Lookup Required",
                    "fields": [
                        {
                            "title": "Session ID",
                            "value": session_id,
                            "short": True
                        },
                        {
                            "title": "Keywords to Lookup",
                            "value": ", ".join(keywords),
                            "short": False
                        },
                        {
                            "title": "Action Required",
                            "value": "Please input these keywords into DataForSEO and paste results back",
                            "short": False
                        }
                    ],
                    "footer": "CIA Waterfall System",
                    "ts": int(time.time())
                }
            ]
        }
        
        return await self._send_slack_message(message)
    
    async def send_perplexity_notification(self, session_id: str, research_prompt: str) -> bool:
        """Send notification for Perplexity trend research (Phase 3A)"""
        message = {
            "channel": self.channel,
            "username": "CIA Waterfall Bot", 
            "icon_emoji": ":chart_with_upwards_trend:",
            "attachments": [
                {
                    "color": "good",
                    "title": "📈 CIA Phase 3A: Perplexity Research Required",
                    "fields": [
                        {
                            "title": "Session ID",
                            "value": session_id,
                            "short": True
                        },
                        {
                            "title": "Research Prompt",
                            "value": f"```{research_prompt}```",
                            "short": False
                        },
                        {
                            "title": "Action Required", 
                            "value": "Run this prompt in Perplexity with Claude 3 Beta and paste results back",
                            "short": False
                        }
                    ],
                    "footer": "CIA Waterfall System",
                    "ts": int(time.time())
                }
            ]
        }
        
        return await self._send_slack_message(message)
    
    async def send_testimonials_notification(self, session_id: str, company_name: str) -> bool:
        """Send notification for testimonials gathering (Phase 3B)"""
        message = {
            "channel": self.channel,
            "username": "CIA Waterfall Bot",
            "icon_emoji": ":speech_balloon:",
            "attachments": [
                {
                    "color": "#36a64f",
                    "title": "💬 CIA Phase 3B: Testimonials Needed",
                    "fields": [
                        {
                            "title": "Session ID",
                            "value": session_id,
                            "short": True
                        },
                        {
                            "title": "Company",
                            "value": company_name,
                            "short": True
                        },
                        {
                            "title": "Action Required",
                            "value": "Automated testimonial gathering found insufficient data. Please provide testimonials or type 'continue' to proceed with framework only.",
                            "short": False
                        }
                    ],
                    "footer": "CIA Waterfall System",
                    "ts": int(time.time())
                }
            ]
        }
        
        return await self._send_slack_message(message)

class EmailNotifier:
    """Email backup notifications for human-in-loop workflows"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
    
    async def send_dataforseo_email(self, to_email: str, session_id: str, keywords: List[str]) -> bool:
        """Send email notification for DataForSEO lookup"""
        subject = f"CIA Waterfall: DataForSEO Lookup Required - Session {session_id}"
        
        html_body = f"""
        <html>
        <body>
            <h2>🔍 CIA Phase 2A: DataForSEO Lookup Required</h2>
            <p><strong>Session ID:</strong> {session_id}</p>
            <p><strong>Keywords to Lookup:</strong></p>
            <ul>
                {''.join([f'<li>{keyword}</li>' for keyword in keywords])}
            </ul>
            <p><strong>Action Required:</strong></p>
            <ol>
                <li>Log into DataForSEO with credentials: eca1d1f1229a0603</li>
                <li>Input the keywords listed above</li>
                <li>Copy the results (search volume, competition, CPC data)</li>
                <li>Paste results back into the CIA system to continue Phase 2A</li>
            </ol>
            <p><em>This is an automated message from CIA Waterfall System</em></p>
        </body>
        </html>
        """
        
        return await self._send_email(to_email, subject, html_body)
    
    async def send_perplexity_email(self, to_email: str, session_id: str, research_prompt: str) -> bool:
        """Send email notification for Perplexity research"""
        subject = f"CIA Waterfall: Perplexity Research Required - Session {session_id}"
        
        html_body = f"""
        <html>
        <body>
            <h2>📈 CIA Phase 3A: Perplexity Research Required</h2>
            <p><strong>Session ID:</strong> {session_id}</p>
            <p><strong>Research Prompt:</strong></p>
            <div style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; font-family: monospace;">
                {research_prompt.replace('\n', '<br>')}
            </div>
            <p><strong>Action Required:</strong></p>
            <ol>
                <li>Log into Perplexity Max with Claude 3 Beta model</li>
                <li>Copy and paste the research prompt above</li>
                <li>Run the research and wait for comprehensive results</li>
                <li>Copy the complete results and paste back into CIA system</li>
            </ol>
            <p><em>This is an automated message from CIA Waterfall System</em></p>
        </body>
        </html>
        """
        
        return await self._send_email(to_email, subject, html_body)

class HumanLoopManager:
    """Manager for coordinating human-in-loop workflows"""
    
    def __init__(self, slack_notifier: SlackNotifier, email_notifier: EmailNotifier):
        self.slack = slack_notifier
        self.email = email_notifier
        self.active_loops: Dict[str, HumanLoopState] = {}
    
    async def initiate_dataforseo_workflow(
        self, 
        session_id: str, 
        keywords: List[str],
        email: str = "team@badaboostadgrants.org"
    ) -> HumanLoopState:
        """Initiate DataForSEO lookup workflow (Phase 2A)"""
        
        # Create human loop state
        loop_state = HumanLoopState(
            session_id=session_id,
            phase_id="2A",
            notification_type=NotificationType.DATAFORSEO_KEYWORDS,
            data={"keywords": keywords},
            sent_at=time.time()
        )
        
        # Send both Slack and Email notifications
        slack_success = await self.slack.send_dataforseo_notification(session_id, keywords)
        email_success = await self.email.send_dataforseo_email(email, session_id, keywords)
        
        if not (slack_success or email_success):
            raise NotificationDeliveryError("Failed to deliver notifications via both Slack and Email")
        
        # Store active loop state
        self.active_loops[session_id] = loop_state
        
        return loop_state
    
    async def initiate_perplexity_workflow(
        self,
        session_id: str,
        research_prompt: str,
        email: str = "team@badaboostadgrants.org"
    ) -> HumanLoopState:
        """Initiate Perplexity research workflow (Phase 3A)"""
        
        loop_state = HumanLoopState(
            session_id=session_id,
            phase_id="3A", 
            notification_type=NotificationType.PERPLEXITY_RESEARCH,
            data={"research_prompt": research_prompt},
            sent_at=time.time()
        )
        
        # Send notifications
        slack_success = await self.slack.send_perplexity_notification(session_id, research_prompt)
        email_success = await self.email.send_perplexity_email(email, session_id, research_prompt)
        
        if not (slack_success or email_success):
            raise NotificationDeliveryError("Failed to deliver notifications via both Slack and Email")
        
        self.active_loops[session_id] = loop_state
        return loop_state
    
    async def receive_human_input(self, session_id: str, response_data: Dict[str, Any]) -> bool:
        """Process human input for active loop"""
        if session_id not in self.active_loops:
            return False
        
        loop_state = self.active_loops[session_id]
        loop_state.response_data = response_data
        loop_state.responded_at = time.time()
        loop_state.status = "completed"
        
        # Validate response based on notification type
        if loop_state.notification_type == NotificationType.DATAFORSEO_KEYWORDS:
            return self._validate_dataforseo_response(response_data)
        elif loop_state.notification_type == NotificationType.PERPLEXITY_RESEARCH:
            return self._validate_perplexity_response(response_data)
        
        return True
    
    def _validate_dataforseo_response(self, response_data: Dict[str, Any]) -> bool:
        """Validate DataForSEO response contains required data"""
        required_fields = ["search_volume", "competition", "cpc"]
        return all(field in response_data for field in required_fields)
    
    def _validate_perplexity_response(self, response_data: Dict[str, Any]) -> bool:
        """Validate Perplexity response contains trend data"""
        required_fields = ["trending_topics", "viral_content", "engagement_patterns"]
        return any(field in response_data for field in required_fields)
    
    async def wait_for_human_input(self, session_id: str, timeout_seconds: int = 3600) -> Optional[Dict[str, Any]]:
        """Wait for human input with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            if session_id in self.active_loops:
                loop_state = self.active_loops[session_id]
                if loop_state.status == "completed":
                    return loop_state.response_data
            
            await asyncio.sleep(10)  # Check every 10 seconds
        
        # Timeout reached
        if session_id in self.active_loops:
            self.active_loops[session_id].status = "expired"
        
        return None

class NotificationDeliveryError(Exception):
    """Raised when both Slack and Email notifications fail"""
    pass

# Example usage pattern:
async def example_human_loop_workflow():
    """Example of how to implement human-in-loop workflows"""
    
    # Initialize notifiers
    slack = SlackNotifier(webhook_url="https://hooks.slack.com/services/...", channel="#waterfall")
    email = EmailNotifier(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="notifications@modernfoundry.com",
        password="app_password",
        from_email="notifications@modernfoundry.com"
    )
    
    # Initialize human loop manager
    manager = HumanLoopManager(slack, email)
    
    # Example: Phase 2A DataForSEO workflow
    session_id = "session_123"
    keywords = ["marketing automation", "business intelligence", "lead generation"]
    
    # Initiate workflow
    loop_state = await manager.initiate_dataforseo_workflow(session_id, keywords)
    
    # Wait for human input
    response_data = await manager.wait_for_human_input(session_id, timeout_seconds=1800)  # 30 min timeout
    
    if response_data:
        print(f"Received DataForSEO data: {response_data}")
        # Continue with Phase 2A analysis using real keyword data
    else:
        print("Timeout waiting for human input")
        # Handle timeout scenario