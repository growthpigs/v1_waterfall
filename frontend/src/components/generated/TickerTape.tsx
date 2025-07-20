import React from "react";
import {
  TrendingUp,
  Zap,
  Target,
  Users,
  BarChart3,
  CheckCircle,
  Lightbulb,
  Globe,
  DollarSign,
  Calendar,
  Activity,
  Award,
  Video,
} from "lucide-react";
import { useTickerFeed, useTrackEngagement } from "../../services/tickerService";

interface TickerItem {
  icon: React.ComponentType<{ className?: string }>;
  text: string;
  type: "success" | "info" | "warning" | "update";
  id?: string;
}

const TickerTape: React.FC = () => {
  // Use ticker service with automatic fallback to mock data
  const { data: tickerData, isLoading, error } = useTickerFeed({ limit: 10 });
  const trackEngagement = useTrackEngagement();

  // Icon mapping for backend data
  const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
    TrendingUp,
    DollarSign,
    Lightbulb,
    Globe,
    Activity,
    BarChart3,
    Calendar,
    Target,
    Users,
    Zap,
    Award,
    Video,
    CheckCircle,
  };

  // Fallback static data (matches original implementation)
  const fallbackItems: TickerItem[] = [
    {
      icon: TrendingUp,
      text: "Campaign Performance Alert: Your 'Authority Building' campaign CTR increased by 25%",
      type: "success",
    },
    {
      icon: Lightbulb,
      text: "Content Opportunity Detected: Video testimonials show 3x higher engagement this week",
      type: "info",
    },
    {
      icon: Globe,
      text: "SEO Trend Update: New Google algorithm prioritizes authority-based content",
      type: "info",
    },
    {
      icon: DollarSign,
      text: "Google Ads Performance: Generated 47 new qualified leads in the past 2 hours",
      type: "success",
    },
    {
      icon: Target,
      text: "Optimization Opportunity: Post testimonials between 2-4 PM for 35% better reach",
      type: "info",
    },
    {
      icon: Zap,
      text: "Industry News: AI-powered content personalization shows 40% improvement",
      type: "update",
    },
    {
      icon: Calendar,
      text: "Content Calendar Update: This week's content reached 89% of target engagement",
      type: "success",
    },
    {
      icon: BarChart3,
      text: "Audience Insight: Your audience engages most with case study content on Tuesdays",
      type: "info",
    },
    {
      icon: CheckCircle,
      text: "Weekly Publishing Success: Content calendar achieved 94% on-time delivery",
      type: "success",
    },
    {
      icon: Users,
      text: "Lead Generation Update: 3 new high-value prospects identified from content engagement",
      type: "success",
    },
  ];

  // Transform backend data to component format
  const tickerItems: TickerItem[] = React.useMemo(() => {
    if (isLoading || error || !tickerData?.items?.length) {
      return fallbackItems;
    }

    return tickerData.items.map((item) => ({
      id: item.id,
      icon: iconMap[item.icon_name] || Lightbulb,
      text: `${item.title}: ${item.description}`,
      type: item.type,
    }));
  }, [tickerData, isLoading, error]);

  const handleItemClick = (item: TickerItem, index: number) => {
    console.log(`Ticker item clicked: ${item.text}`);
    
    // Track engagement if we have an item ID (backend data)
    if (item.id) {
      trackEngagement.mutate({
        ticker_item_id: item.id,
        action: "click",
        metadata: { position: index },
      });
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "success":
        return "text-green-400";
      case "warning":
        return "text-orange-400";
      case "update":
        return "text-white/70";
      default:
        return "text-blue-400";
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 bg-black/20 backdrop-blur-lg border-t border-white/20 overflow-hidden">
      <div className="h-8 flex items-center">
        <style>{`
          @keyframes ticker-scroll {
            0% {
              transform: translateX(0%);
            }
            100% {
              transform: translateX(-100%);
            }
          }
          
          .ticker-content {
            animation: ticker-scroll 380s linear infinite;
            will-change: transform;
          }
        `}</style>
        <div className="ticker-content flex items-center space-x-8 whitespace-nowrap">
          {/* Repeat items multiple times to ensure seamless loop */}
          {[...tickerItems, ...tickerItems, ...tickerItems, ...tickerItems].map(
            (item, index) => (
              <div
                key={`ticker-${index}`}
                className="flex items-center space-x-3 px-4 cursor-pointer hover:opacity-80 transition-opacity"
                onClick={() => handleItemClick(item, index)}
              >
                <div
                  className={`p-1.5 rounded-full bg-black/20 ${getTypeColor(item.type)}`}
                >
                  <item.icon className="w-3 h-3" />
                </div>
                <span className="text-white/80 text-sm font-medium font-mono">
                  {item.text}
                </span>
                {index < tickerItems.length * 4 - 1 && (
                  <div className="w-1 h-1 bg-white/30 rounded-full ml-8" />
                )}
              </div>
            ),
          )}
        </div>
      </div>
      
      {/* Debug info (only in development) */}
      {import.meta.env.DEV && (
        <div className="absolute top-0 right-4 text-xs text-white/50">
          {isLoading ? "Loading..." : error ? "Using fallback data" : `Live data (${tickerData?.items?.length || 0} items)`}
        </div>
      )}
    </div>
  );
};

export default TickerTape;
