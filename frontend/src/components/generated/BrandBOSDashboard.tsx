import React from "react";
import { motion } from "framer-motion";
import { Brain, TrendingUp, MessageSquare, Target } from "lucide-react";
import { useNavigate } from "react-router-dom";
import QuickActions from "./QuickActions";
import { glassCardStyles, perfectCardShadow } from "../../lib/utils";
import PageLayout from "../shared/PageLayout";
import PageHeader from "../shared/PageHeader";

interface DashboardCardProps {
  title: string;
  number: string | number;
  subtitle: string;
  icon: React.ComponentType<{
    className?: string;
  }>;
  delay?: number;
  onClick?: () => void;
  navigateTo?: string;
}

interface ContentCluster {
  title: string;
  status: string;
  timeline: string;
  statusColor: string;
}

interface ContentTemplate {
  name: string;
  type: string;
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  number,
  subtitle,
  icon: Icon,
  delay = 0,
  onClick,
  navigateTo,
}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    console.log(`🔍 Dashboard card clicked: ${title}`);
    if (onClick) {
      onClick();
    } else if (navigateTo) {
      console.log(`🧭 Navigating to: ${navigateTo}`);
      navigate(navigateTo);
    }
  };

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.6,
        delay,
      }}
      whileHover={{
        y: -4,
        scale: 1.02,
        transition: {
          duration: 0.2,
        },
      }}
      whileTap={{
        scale: 0.98,
        transition: {
          duration: 0.1,
        },
      }}
      onClick={handleClick}
      className={`${glassCardStyles} p-4 lg:p-6 group cursor-pointer hover:border-orange-400/50 hover:bg-black/25 transition-all duration-300`}
      style={{
        boxShadow: perfectCardShadow,
      }}
    >
      <div className="flex items-start justify-between mb-3 lg:mb-4">
        <div className="p-2 lg:p-3 bg-black/20 backdrop-blur-sm rounded-xl border border-purple-400/20 group-hover:border-orange-400/50 group-hover:bg-orange-400/10 transition-all duration-300">
          <Icon className="w-5 h-5 lg:w-6 lg:h-6 text-white/95 group-hover:text-orange-300 transition-colors duration-300" />
        </div>
        <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="text-xs text-orange-300 font-medium">
            Click to explore →
          </div>
        </div>
      </div>

      <div className="space-y-1 lg:space-y-2">
        <div className="text-2xl lg:text-3xl font-bold text-white/95">
          {number}
        </div>
        <h3 className="text-base lg:text-lg font-semibold text-white/90">
          {title}
        </h3>
        <p className="text-xs lg:text-sm text-white/75 leading-relaxed">
          {subtitle}
        </p>
      </div>
    </motion.div>
  );
};

const IntelligenceDashboard: React.FC = () => {
  const navigate = useNavigate();

  const handleDashboardClick = () => {
    console.log(
      "🧭 Intelligence Dashboard clicked - navigating to /performance",
    );
    navigate("/performance");
  };

  const handleMetricClick = (metricLabel: string) => {
    console.log(
      `🧭 Metric clicked: ${metricLabel} - navigating to /performance`,
    );
    navigate("/performance");
  };

  const metrics = [
    {
      label: "Content Performance",
      value: "94%",
      trend: "+12%",
    },
    {
      label: "Engagement Rate",
      value: "8.7%",
      trend: "+24%",
    },
    {
      label: "Authority Score",
      value: "87",
      trend: "+5%",
    },
    {
      label: "System Health",
      value: "99.9%",
      trend: "Stable",
    },
  ];

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.6,
        delay: 0.4,
      }}
      whileHover={{
        y: -2,
        transition: {
          duration: 0.2,
        },
      }}
      whileTap={{
        scale: 0.98,
        transition: {
          duration: 0.1,
        },
      }}
      onClick={handleDashboardClick}
      className={`${glassCardStyles} p-4 lg:p-6 group cursor-pointer hover:border-orange-400/50 hover:bg-black/25 transition-all duration-300`}
      style={{
        boxShadow: perfectCardShadow,
      }}
    >
      <div className="flex items-start justify-between mb-4 lg:mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 lg:p-3 bg-black/20 backdrop-blur-sm rounded-xl border border-purple-400/20 group-hover:border-orange-400/30 transition-all duration-300">
            <Target className="w-5 h-5 lg:w-6 lg:h-6 text-white/95" />
          </div>
          <h3 className="text-lg lg:text-xl font-semibold text-white/95">
            Intelligence Dashboard
          </h3>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-4">
        {metrics.map((metric, index) => (
          <motion.div
            key={index}
            onClick={(e) => {
              e.stopPropagation();
              handleMetricClick(metric.label);
            }}
            whileHover={{
              scale: 1.02,
              transition: {
                duration: 0.2,
              },
            }}
            whileTap={{
              scale: 0.98,
              transition: {
                duration: 0.1,
              },
            }}
            className="bg-black/20 backdrop-blur-sm rounded-xl p-3 lg:p-4 border border-purple-400/20 hover:border-orange-400/30 hover:bg-black/25 transition-all duration-300 cursor-pointer"
          >
            <div className="text-xl lg:text-2xl font-bold text-white/95 mb-1">
              {metric.value}
            </div>
            <div className="text-xs lg:text-sm text-white/75 mb-2">
              {metric.label}
            </div>
            <div className="text-xs text-green-400 font-medium">
              {metric.trend}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-4 lg:mt-6 pt-4 border-t border-purple-400/20">
        <div className="flex items-center justify-between text-sm">
          <span className="text-white/75">Last updated</span>
          <span className="text-white/90">2 minutes ago</span>
        </div>
      </div>
    </motion.div>
  );
};

const ContentCreationHub: React.FC = () => {
  const navigate = useNavigate();

  const handleProjectClick = (projectTitle: string) => {
    console.log(
      `🧭 Project clicked: ${projectTitle} - navigating to /content-engine`,
    );
    navigate("/content-engine");
  };

  const handleTemplateClick = (templateName: string) => {
    console.log(
      `🧭 Template clicked: ${templateName} - navigating to /content-engine`,
    );
    navigate("/content-engine");
  };

  const activeProjects: ContentCluster[] = [
    {
      title: "AI Productivity Blog Series",
      status: "In Progress",
      timeline: "Tomorrow",
      statusColor: "bg-blue-500",
    },
    {
      title: "LinkedIn Thought Leadership",
      status: "Review",
      timeline: "Today",
      statusColor: "bg-orange-500",
    },
    {
      title: "Customer Success Stories",
      status: "Draft",
      timeline: "Next Week",
      statusColor: "bg-green-500",
    },
  ];

  const contentTemplates: ContentTemplate[] = [
    {
      name: "Blog Post",
      type: "Long-form",
    },
    {
      name: "Social Media",
      type: "Short-form",
    },
    {
      name: "Email Campaign",
      type: "Newsletter",
    },
    {
      name: "Case Study",
      type: "Authority",
    },
  ];

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.6,
        delay: 0.3,
      }}
      whileHover={{
        y: -2,
        transition: {
          duration: 0.2,
        },
      }}
      className={`${glassCardStyles} p-4 lg:p-6 group`}
      style={{
        boxShadow: perfectCardShadow,
      }}
    >
      <div className="flex items-start justify-between mb-4 lg:mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 lg:p-3 bg-black/20 backdrop-blur-sm rounded-xl border border-purple-400/20 group-hover:border-orange-400/30 transition-all duration-300">
            <Target className="w-5 h-5 lg:w-6 lg:h-6 text-white/95" />
          </div>
          <h3 className="text-lg lg:text-xl font-semibold text-white/95">
            Content Creation Hub
          </h3>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
        {/* Active Projects */}
        <div className="space-y-3 lg:space-y-4">
          <h4 className="text-base lg:text-lg font-medium text-white/90 mb-3">
            Active Projects
          </h4>
          <div className="space-y-2 lg:space-y-3">
            {activeProjects.map((cluster, index) => (
              <motion.div
                key={index}
                onClick={() => handleProjectClick(cluster.title)}
                whileHover={{
                  scale: 1.02,
                  transition: {
                    duration: 0.2,
                  },
                }}
                whileTap={{
                  scale: 0.98,
                  transition: {
                    duration: 0.1,
                  },
                }}
                className="bg-black/20 backdrop-blur-sm rounded-xl p-3 lg:p-4 border border-purple-400/20 hover:border-orange-400/30 hover:bg-black/25 transition-all duration-300 cursor-pointer"
              >
                <div className="flex items-center justify-between mb-2">
                  <h5 className="font-medium text-white/95 text-xs lg:text-sm">
                    {cluster.title}
                  </h5>
                  <div
                    className={`w-2 h-2 rounded-full ${cluster.statusColor}`}
                  />
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-white/75">{cluster.status}</span>
                  <span className="text-white/65">{cluster.timeline}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Content Templates */}
        <div className="space-y-3 lg:space-y-4">
          <h4 className="text-base lg:text-lg font-medium text-white/90 mb-3">
            Content Templates
          </h4>
          <div className="grid grid-cols-2 gap-2 lg:gap-3">
            {contentTemplates.map((template, index) => (
              <motion.div
                key={index}
                onClick={() => handleTemplateClick(template.name)}
                whileHover={{
                  scale: 1.02,
                  transition: {
                    duration: 0.2,
                  },
                }}
                whileTap={{
                  scale: 0.98,
                  transition: {
                    duration: 0.1,
                  },
                }}
                className="bg-black/20 backdrop-blur-sm rounded-xl p-3 lg:p-4 border border-purple-400/20 hover:border-orange-400/30 hover:bg-black/25 transition-all duration-300 text-center cursor-pointer"
              >
                <h5 className="font-medium text-white/95 text-xs lg:text-sm mb-1">
                  {template.name}
                </h5>
                <p className="text-xs text-white/65">{template.type}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

const BrandBOSDashboard: React.FC = () => {
  console.log("🎯 BrandBOSDashboard: Component mounting...");
  console.log("🎯 BrandBOSDashboard: Should show purple gradient background");
  console.log(
    "🎯 BrandBOSDashboard: Three main cards + Content Creation Hub + Intelligence Dashboard + Quick Actions",
  );

  return (
    <PageLayout
      pageTitle="Brand BOS Command Center"
      placeholder="Ask about your Brand BOS performance..."
    >
      {/* Purple gradient background per THEME_CONSTANTS.md */}
      <div className="fixed inset-0 bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 -z-10" />
      
      {/* Header - Global Standard */}
      <PageHeader
        title="Brand BOS Command Center"
        subtitle="AI-powered content intelligence and marketing automation"
      />

      {/* Top Row - 3 Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-6 mb-6 lg:mb-8">
        <DashboardCard
          title="Latest CIA Intelligence"
          number={12}
          subtitle="Fresh insights from your latest analysis"
          icon={Brain}
          delay={0.1}
          navigateTo="/cia"
        />
        <DashboardCard
          title="Viral Opportunities"
          number={8}
          subtitle="Trending topics ready for content creation"
          icon={TrendingUp}
          delay={0.2}
          navigateTo="/content-engine"
        />
        <DashboardCard
          title="Brand Voice Guidelines"
          number={5}
          subtitle="Your brand personality and messaging framework"
          icon={MessageSquare}
          delay={0.3}
          navigateTo="/settings"
        />
      </div>

      {/* Middle Row - 2 Wider Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 mb-8">
        <ContentCreationHub />
        <QuickActions />
      </div>

      {/* Bottom Row - Intelligence Dashboard */}
      <div className="mb-8">
        <IntelligenceDashboard />
      </div>
    </PageLayout>
  );
};

export default BrandBOSDashboard;
