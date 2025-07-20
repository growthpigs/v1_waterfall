import React from "react";
import { motion } from "framer-motion";
import {
  Brain,
  DollarSign,
  FileText,
  Target,
  TrendingUp,
  Users,
  ChevronDown,
  Settings,
  Rocket,
  Calendar,
  Play,
  Pause,
  CheckCircle,
  AlertCircle,
  Megaphone,
  Edit3,
  MoreHorizontal,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import PageLayout from "../shared/PageLayout";
import PageHeader from "../shared/PageHeader";
import { perfectCardShadow, glassCardStyles } from "../../lib/utils";

interface CampaignCardProps {
  name: string;
  status: "active" | "paused" | "completed" | "draft";
  progress: number;
  startDate: string;
  endDate: string;
  leads: number;
  engagement: string;
  type:
    | "content-cluster"
    | "social"
    | "email"
    | "authority"
    | "case-study"
    | "thought-leadership";
  delay?: number;
}

const getCampaignIcon = (type: CampaignCardProps["type"]) => {
  switch (type) {
    case "content-cluster":
      return <Users className="w-5 h-5 text-white" />;
    case "social":
      return <TrendingUp className="w-5 h-5 text-white" />;
    case "email":
      return <Megaphone className="w-5 h-5 text-white" />;
    case "authority":
      return <Target className="w-5 h-5 text-white" />;
    case "case-study":
      return <FileText className="w-5 h-5 text-white" />;
    case "thought-leadership":
      return <Brain className="w-5 h-5 text-white" />;
    default:
      return <Rocket className="w-5 h-5 text-white" />;
  }
};

interface DashboardMetricCardProps {
  title: string;
  subtitle: string;
  metrics: { label: string; value: string | number }[];
  icon: React.ComponentType<{ className?: string }>;
  delay?: number;
  onClick?: () => void;
}

const DashboardMetricCard: React.FC<DashboardMetricCardProps> = ({
  title,
  subtitle,
  metrics,
  icon: Icon,
  delay = 0,
  onClick,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ y: -2, scale: 1.02, transition: { duration: 0.2 } }}
      whileTap={{ scale: 0.98, transition: { duration: 0.1 } }}
      onClick={onClick}
      className={`${glassCardStyles} p-5 cursor-pointer hover:border-white/40 hover:bg-white/10 transition-all duration-300`}
      style={{ boxShadow: perfectCardShadow }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center">
          <div className="w-12 h-12 bg-white/15 backdrop-blur-sm rounded-xl flex items-center justify-center mr-4 group-hover:bg-white/25 transition-all duration-300 border border-white/20">
            <Icon className="w-6 h-6 text-white group-hover:text-orange-200 transition-colors duration-300" />
          </div>
          <div>
            <h3 className="text-white font-semibold leading-tight">{title}</h3>
            <p className="text-white/70 text-sm leading-tight">{subtitle}</p>
          </div>
        </div>
        <TrendingUp className="w-5 h-5 text-white" />
      </div>
      <div className="space-y-1">
        {metrics.map((metric, index) => (
          <div key={index} className="flex justify-between leading-tight">
            <span className="text-white/80">{metric.label}:</span>
            <span className="text-white font-medium">{metric.value}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

const getStatusIcon = (status: CampaignCardProps["status"]) => {
  switch (status) {
    case "active":
      return <Play className="w-4 h-4" />;
    case "paused":
      return <Pause className="w-4 h-4" />;
    case "completed":
      return <CheckCircle className="w-4 h-4" />;
    case "draft":
      return <AlertCircle className="w-4 h-4" />;
  }
};

const getStatusColor = (status: CampaignCardProps["status"]) => {
  switch (status) {
    case "active":
      return "bg-green-500/20 text-green-400 border-green-400/30";
    case "paused":
      return "bg-yellow-500/20 text-yellow-400 border-yellow-400/30";
    case "completed":
      return "bg-blue-500/20 text-blue-400 border-blue-400/30";
    case "draft":
      return "bg-gray-500/20 text-gray-400 border-gray-400/30";
  }
};

const CampaignCard: React.FC<CampaignCardProps> = ({
  name,
  status,
  progress,
  startDate,
  endDate,
  leads,
  engagement,
  type,
  delay = 0,
}) => {
  const navigate = useNavigate();

  const handleCampaignClick = () => {
    console.log(`🧭 Campaign clicked: ${name} - navigating to /content-engine`);
    navigate("/content-engine");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ y: -2, scale: 1.02, transition: { duration: 0.2 } }}
      whileTap={{ scale: 0.98, transition: { duration: 0.1 } }}
      onClick={handleCampaignClick}
      className={`${glassCardStyles} p-6 cursor-pointer hover:bg-white/10 hover:border-white/40 transition-all duration-300`}
      style={{ boxShadow: perfectCardShadow }}
    >
      {/* Clean Header with inline icon */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
            {getCampaignIcon(type)}
          </div>
          <h3 className="text-lg font-semibold text-white/95">{name}</h3>
        </div>
        <div
          className={`flex items-center space-x-1 px-3 py-1 rounded-lg border ${getStatusColor(status)}`}
        >
          {getStatusIcon(status)}
          <span className="text-sm font-medium capitalize">{status}</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-sm text-white/75 mb-2">
          <span>Progress</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full bg-white/20 rounded-lg h-3 overflow-hidden border border-white/20">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 1, delay: delay + 0.3 }}
            className="h-full bg-gradient-to-r from-orange-400 to-yellow-400 rounded-lg shadow-sm"
          />
        </div>
      </div>

      {/* Campaign Details */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 border border-white/20">
          <div className="flex items-center space-x-2 mb-1">
            <Calendar className="w-4 h-4 text-white/80" />
            <span className="text-xs text-white/80">Duration</span>
          </div>
          <p className="text-sm font-medium text-white/95">
            {startDate} - {endDate}
          </p>
        </div>
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 border border-white/20">
          <div className="flex items-center space-x-2 mb-1">
            <Users className="w-4 h-4 text-white/80" />
            <span className="text-xs text-white/80">Leads Generated</span>
          </div>
          <p className="text-sm font-medium text-white/95">
            {leads.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Engagement Metric */}
      <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 border border-white/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-white/80" />
            <span className="text-sm text-white/80">Engagement Rate</span>
          </div>
          <span className="text-sm font-medium text-white/95">
            {engagement}
          </span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2 mt-4">
        <button
          onClick={(e) => {
            e.stopPropagation();
            console.log(`🔧 Edit campaign: ${name}`);
          }}
          className="flex-1 flex items-center justify-center px-3 py-2 bg-white/15 hover:bg-white/25 border border-white/20 hover:border-white/30 rounded-lg text-white text-xs transition-all duration-200"
        >
          <Edit3 className="w-3 h-3 mr-1 text-white" />
          Edit
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            console.log(
              `${status === "active" ? "⏸️ Pause" : "▶️ Play"} campaign: ${name}`,
            );
          }}
          className="flex items-center justify-center p-2 bg-white/15 hover:bg-white/25 border border-white/20 hover:border-white/30 rounded-lg text-white transition-all duration-200"
        >
          {status === "active" ? (
            <Pause className="w-3 h-3 text-white" />
          ) : (
            <Play className="w-3 h-3 text-white" />
          )}
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            console.log(`⚙️ More options for campaign: ${name}`);
          }}
          className="flex items-center justify-center p-2 bg-white/15 hover:bg-white/25 border border-white/20 hover:border-white/30 rounded-lg text-white transition-all duration-200"
        >
          <MoreHorizontal className="w-3 h-3 text-white" />
        </button>
      </div>
    </motion.div>
  );
};

const CampaignCenterPage: React.FC = () => {
  console.log("[Campaign] Campaign Center rendered with burnt orange theme");
  const navigate = useNavigate();

  // Dashboard Metrics from Magic Path
  const dashboardMetrics = [
    {
      title: "Active Content Clusters",
      subtitle: "Weekly Campaigns",
      icon: Users,
      metrics: [
        { label: "Running", value: 8 },
        { label: "Weekly Reach", value: "125K" },
        { label: "Engagement", value: "7.2%" },
      ],
      onClick: () => {
        console.log(
          "🧭 Content Clusters clicked - navigating to /content-engine",
        );
        navigate("/content-engine");
      },
    },
    {
      title: "Google Ad Grant",
      subtitle: "Budget Allocation",
      icon: DollarSign,
      metrics: [
        { label: "Total Budget", value: "$10,000" },
        { label: "Allocated", value: "$10,000" },
        { label: "Efficiency", value: "94%" },
      ],
      onClick: () => {
        console.log("🧭 Google Ad Grant clicked - navigating to /performance");
        navigate("/performance");
      },
    },
    {
      title: "Humbleboast Briefs",
      subtitle: "Facebook Ad Concepts",
      icon: FileText,
      metrics: [
        { label: "Generated", value: 23 },
        { label: "Ready", value: 12 },
        { label: "Est. Reach", value: "180K" },
      ],
      onClick: () => {
        console.log(
          "🧭 Humbleboast Briefs clicked - navigating to /content-engine",
        );
        navigate("/content-engine");
      },
    },
    {
      title: "Authority Impact",
      subtitle: "Campaign Effectiveness",
      icon: Target,
      metrics: [
        { label: "Score", value: "87/100" },
        { label: "Weekly", value: "+12%" },
        { label: "Ranking", value: "Top 15%" },
      ],
      onClick: () => {
        console.log("🧭 Authority Impact clicked - navigating to /performance");
        navigate("/performance");
      },
    },
  ];

  // Campaign data (existing production campaigns)
  const campaigns: CampaignCardProps[] = [
    {
      name: "Q4 Authority Building Series",
      status: "active",
      progress: 68,
      startDate: "Oct 1",
      endDate: "Dec 31",
      leads: 342,
      engagement: "12.4%",
      type: "authority",
    },
    {
      name: "LinkedIn Thought Leadership",
      status: "active",
      progress: 45,
      startDate: "Nov 15",
      endDate: "Jan 15",
      leads: 128,
      engagement: "9.2%",
      type: "thought-leadership",
    },
    {
      name: "Email Nurture Sequence",
      status: "paused",
      progress: 30,
      startDate: "Nov 1",
      endDate: "Dec 15",
      leads: 87,
      engagement: "24.6%",
      type: "email",
    },
    {
      name: "Holiday Content Blitz",
      status: "completed",
      progress: 100,
      startDate: "Dec 1",
      endDate: "Dec 25",
      leads: 523,
      engagement: "18.7%",
      type: "content-cluster",
    },
    {
      name: "New Year Authority Launch",
      status: "draft",
      progress: 0,
      startDate: "Jan 1",
      endDate: "Feb 28",
      leads: 0,
      engagement: "0%",
      type: "authority",
    },
    {
      name: "Case Study Showcase",
      status: "active",
      progress: 82,
      startDate: "Dec 10",
      endDate: "Jan 10",
      leads: 256,
      engagement: "15.3%",
      type: "case-study",
    },
  ];

  const handleActionClick = (action: string) => {
    console.log(`🎯 Action clicked: ${action}`);
    switch (action) {
      case "Generate Campaign from CIA Intelligence":
        navigate("/cia");
        break;
      case "Create Humbleboast Brief":
        navigate("/content-engine");
        break;
      case "Launch Content Cluster Campaign":
        navigate("/content-engine");
        break;
      default:
        console.log(`Action: ${action}`);
    }
  };

  const quickActions = [
    {
      label: "Launch Campaign",
      icon: Rocket,
      onClick: () => navigate("/content-engine"),
    },
    {
      label: "Schedule Content",
      icon: Calendar,
      onClick: () => navigate("/content-calendar"),
    },
    { label: "Import Leads", icon: Users, onClick: () => navigate("/cia") },
    {
      label: "View Analytics",
      icon: TrendingUp,
      onClick: () => navigate("/performance"),
    },
  ];

  return (
    <PageLayout
      pageTitle="Campaign Center"
      placeholder="Ask about campaign management and optimization..."
    >
      {/* Burnt Orange gradient background per THEME_CONSTANTS.md */}
      <div className="fixed inset-0 bg-gradient-to-br from-orange-600 via-orange-700 to-orange-800 -z-10" />

      {/* Header - Global Standard */}
      <PageHeader
        title="Campaign Center"
        subtitle="Manage Brand BOS campaigns powered by CIA intelligence and content clusters"
      />

      {/* Dashboard Metrics Cards - From Magic Path */}
      <section className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
        {dashboardMetrics.map((metric, index) => (
          <DashboardMetricCard
            key={index}
            title={metric.title}
            subtitle={metric.subtitle}
            metrics={metric.metrics}
            icon={metric.icon}
            delay={0.1 * (index + 1)}
            onClick={metric.onClick}
          />
        ))}
      </section>

      {/* Action Buttons Bar - From Magic Path */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className={`${glassCardStyles} p-5 mb-6`}
        style={{ boxShadow: perfectCardShadow }}
      >
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex flex-wrap gap-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() =>
                handleActionClick("Generate Campaign from CIA Intelligence")
              }
              className="flex items-center px-6 py-3 bg-white hover:bg-gray-50 border border-gray-200 rounded-xl text-orange-800 font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <Brain className="w-4 h-4 mr-2 text-orange-800" />
              Generate Campaign from CIA Intelligence
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleActionClick("Create Humbleboast Brief")}
              className="flex items-center px-6 py-3 bg-white hover:bg-gray-50 border border-gray-200 rounded-xl text-orange-800 font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <Megaphone className="w-4 h-4 mr-2 text-orange-800" />
              Create Humbleboast Brief
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() =>
                handleActionClick("Launch Content Cluster Campaign")
              }
              className="flex items-center px-6 py-3 bg-white hover:bg-gray-50 border border-gray-200 rounded-xl text-orange-800 font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <Users className="w-4 h-4 mr-2 text-orange-800" />
              Launch Content Cluster Campaign
            </motion.button>
          </div>
          <div className="flex items-center gap-3">
            <button className="flex items-center px-4 py-3 bg-white/15 hover:bg-white/25 border border-white/30 rounded-xl text-white font-medium transition-all duration-200">
              Bulk Actions
              <ChevronDown className="w-4 h-4 ml-2 text-white" />
            </button>
            <button className="p-3 bg-white/15 hover:bg-white/25 border border-white/30 rounded-xl text-white transition-all duration-200">
              <Settings className="w-4 h-4 text-white" />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Campaign Grid - Production Version with Improvements */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white leading-tight">
            Active Brand BOS Campaigns
          </h2>
          <div className="flex items-center gap-3">
            <span className="text-white/70 text-sm">
              {campaigns.length} campaigns
            </span>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate("/content-engine")}
              className="flex items-center px-4 py-2 bg-white/15 hover:bg-white/25 border border-white/30 rounded-lg text-white text-sm transition-all duration-200"
            >
              <Rocket className="w-4 h-4 mr-2 text-white" />
              New Campaign
            </motion.button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {campaigns.map((campaign, index) => (
            <CampaignCard key={index} {...campaign} delay={index * 0.1} />
          ))}
        </div>
      </motion.div>

      {/* Quick Actions - At Bottom */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.7 }}
        className={glassCardStyles + " p-6"}
        style={{ boxShadow: perfectCardShadow }}
      >
        <h3 className="text-xl font-semibold text-white/95 mb-4">
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action, index) => (
            <motion.button
              key={index}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={action.onClick}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20 hover:border-white/30 hover:bg-white/15 transition-all duration-300 text-center"
            >
              <action.icon className="w-6 h-6 text-white/95 mx-auto mb-2" />
              <span className="text-sm font-medium text-white/90">
                {action.label}
              </span>
            </motion.button>
          ))}
        </div>
      </motion.div>
    </PageLayout>
  );
};

export default CampaignCenterPage;
