"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import PageLayout from "../shared/PageLayout";
import PageHeader from "../shared/PageHeader";
import { perfectCardShadow, glassCardStyles } from "../../lib/utils";
import {
  CheckCircle,
  Heart,
  BarChart3,
  Users,
  MessageCircle,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  Zap,
  Link,
  Search,
  PieChart,
  Info,
  DollarSign,
  RotateCw,
  AlertCircle,
} from "lucide-react";
import {
  useGoogleAdsPerformance,
  useRotateBudget,
} from "../../services/googleAdsService";

const metrics = [
  {
    label: "Content Clusters Generated",
    value: 24,
    delta: "+18.3%",
    icon: <BarChart3 className="w-6 h-6 text-pink-300" />,
    percent: 92,
    color: "bg-pink-500",
    deltaColor: "text-green-400",
  },
  {
    label: "Publishing Success Rate",
    value: "94%",
    delta: "+5.2%",
    icon: <CheckCircle className="w-6 h-6 text-green-300" />,
    percent: 94,
    color: "bg-green-500",
    deltaColor: "text-green-400",
  },
  {
    label: "Social Engagement Rate",
    value: "7.8%",
    delta: "+12.7%",
    icon: <Heart className="w-6 h-6 text-pink-200" />,
    percent: 78,
    color: "bg-pink-400",
    deltaColor: "text-green-400",
  },
  {
    label: "Content Formats Created",
    value: 156,
    delta: "+23.4%",
    icon: <MessageCircle className="w-6 h-6 text-yellow-200" />,
    percent: 88,
    color: "bg-yellow-400",
    deltaColor: "text-green-400",
  },
  {
    label: "CIA Intelligence Sessions",
    value: 18,
    delta: "+15.7%",
    icon: <PieChart className="w-6 h-6 text-blue-200" />,
    percent: 80,
    color: "bg-blue-400",
    deltaColor: "text-green-400",
  },
  {
    label: "Active Campaigns",
    value: 7,
    delta: "+2.1%",
    icon: <TrendingUp className="w-6 h-6 text-blue-300" />,
    percent: 70,
    color: "bg-blue-500",
    deltaColor: "text-green-400",
  },
];

const socialMetrics = [
  {
    platform: "Instagram",
    followers: "125.0K",
    engagement: "5.2%",
    growth: "+12.3%",
  },
  {
    platform: "TikTok",
    followers: "89.0K",
    engagement: "12.1%",
    growth: "+18.7%",
  },
  {
    platform: "LinkedIn",
    followers: "45.8K",
    engagement: "6.8%",
    growth: "+8.4%",
  },
  {
    platform: "Facebook",
    followers: "67.0K",
    engagement: "4.2%",
    growth: "+5.1%",
  },
];

const pipelineSteps = [
  { step: "Weekly Content Clusters", count: 24, color: "bg-pink-500" },
  { step: "Content Pieces Generated", count: 156, color: "bg-purple-500" },
  { step: "Publishing Success Rate", count: "94%", color: "bg-green-500" },
  { step: "Content Approval Status", count: 3, color: "bg-yellow-500" },
];

const contentBreakdown = [
  {
    label: "Authority Articles",
    engagement: "8.4%",
    percent: 92,
    color: "bg-pink-500",
    gradient: "from-pink-500 to-pink-600",
  },
  {
    label: "Case Studies",
    engagement: "12.1%",
    percent: 88,
    color: "bg-rose-500",
    gradient: "from-rose-500 to-rose-600",
  },
  {
    label: "LinkedIn Posts",
    engagement: "6.2%",
    percent: 76,
    color: "bg-pink-400",
    gradient: "from-pink-400 to-pink-500",
  },
  {
    label: "Email Campaigns",
    engagement: "24.3%",
    percent: 84,
    color: "bg-fuchsia-500",
    gradient: "from-fuchsia-500 to-fuchsia-600",
  },
  {
    label: "Video Content",
    engagement: "9.8%",
    percent: 71,
    color: "bg-pink-600",
    gradient: "from-pink-600 to-pink-700",
  },
];

const contentData = [
  {
    cluster: "Customer Success Stories",
    date: "2024-01-16",
    format: "Epic Pillar",
    status: "Published",
    engagement: "2.3K",
    cia: "9.2/10",
    authority: "High",
    cross: true,
    approval: "Approved",
  },
  {
    cluster: "Product Demo Series",
    date: "2024-01-14",
    format: "TikTok UGC",
    status: "Scheduled",
    engagement: "Pending",
    cia: "7.8/10",
    authority: "Medium",
    cross: true,
    approval: "Approved",
  },
  {
    cluster: "Authority Insights",
    date: "2024-01-13",
    format: "LinkedIn Article",
    status: "Published",
    engagement: "1.8K",
    cia: "8.9/10",
    authority: "Very High",
    cross: true,
    approval: "Approved",
  },
  {
    cluster: "Industry Analysis",
    date: "2024-01-12",
    format: "Blog Post",
    status: "In Review",
    engagement: "Pending",
    cia: "8.1/10",
    authority: "High",
    cross: true,
    approval: "Pending",
  },
  {
    cluster: "Behind the Scenes",
    date: "2024-01-11",
    format: "Instagram Story",
    status: "Published",
    engagement: "3.1K",
    cia: "7.9/10",
    authority: "Medium",
    cross: true,
    approval: "Approved",
  },
];

const aiRecommendations = [
  {
    title: "CIA Pain Point Analysis",
    description:
      'CIA Analysis identified "customer onboarding friction" – your content addressing this gets 40% higher engagement. Generate 2 more pieces targeting this pain point.',
    priority: "High",
    priorityColor: "bg-red-500/20 text-red-400",
    impact: "Increase engagement by 40%",
  },
  {
    title: "Authority Positioning Insights",
    description:
      'Authority positioning from CIA Phase 1C suggests focusing on "automation expertise" area. This aligns with your highest-performing content themes.',
    priority: "Medium",
    priorityColor: "bg-yellow-500/20 text-yellow-400",
    impact: "Improve authority positioning",
  },
  {
    title: "Customer Psychology Insights",
    description:
      "Customer psychology insights show audience responds best to testimonial-driven content. Your success story format has 3x higher conversion rates.",
    priority: "High",
    priorityColor: "bg-red-500/20 text-red-400",
    impact: "3x higher conversion rates",
  },
  {
    title: "CIA Intelligence Integration",
    description:
      "Content with CIA scores above 9.0 generates 65% more authority impact. Focus on deeper intelligence integration for maximum positioning effect.",
    priority: "Medium",
    priorityColor: "bg-yellow-500/20 text-yellow-400",
    impact: "65% more authority impact",
  },
];

const PerformancePage: React.FC = () => {
  const [barWidths, setBarWidths] = useState(Array(metrics.length).fill(0));
  const [breakdownWidths, setBreakdownWidths] = useState(
    Array(contentBreakdown.length).fill(0),
  );

  const { data: googleAdsData, isLoading: googleAdsLoading } =
    useGoogleAdsPerformance();
  const rotateBudget = useRotateBudget();

  const handleBudgetRotation = async (campaignId: string) => {
    // In a real app, you'd show a modal to select the new cluster
    const newClusterId = prompt("Enter new cluster name for budget rotation:");
    if (newClusterId) {
      try {
        await rotateBudget.mutateAsync({
          worstCampaignId: campaignId,
          newClusterId,
        });
        alert("Budget rotation successful!");
      } catch (error) {
        console.error("Budget rotation failed:", error);
      }
    }
  };

  useEffect(() => {
    setTimeout(() => {
      setBarWidths(metrics.map((m) => m.percent));
      setBreakdownWidths(contentBreakdown.map((b) => b.percent));
    }, 300);
  }, []);

  return (
    <PageLayout
      pageTitle="Performance Analytics"
      placeholder="Ask about performance metrics..."
    >
      {/* Cyan to Blue gradient background per THEME_CONSTANTS.md */}
      <div className="fixed inset-0 bg-gradient-to-br from-cyan-600 via-cyan-700 to-blue-800 -z-10" />

      <PageHeader
        title="Performance Analytics"
        subtitle="Real-time insights and metrics for your authority building campaigns"
      />

      {/* Content Performance Breakdown - Top Section */}
      <div className="mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className={glassCardStyles + " p-6"}
          style={{ boxShadow: perfectCardShadow }}
        >
          <h2 className="text-xl font-bold text-white mb-6 flex items-center">
            <BarChart3 className="w-6 h-6 mr-3 text-pink-300" />
            Content Performance Breakdown
          </h2>
          <div className="space-y-4">
            {contentBreakdown.map((item, index) => (
              <div
                key={item.label}
                className="flex items-center justify-between"
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full ${item.color}`}></div>
                  <span className="text-white font-medium">{item.label}</span>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-32 bg-white/20 rounded-full h-3 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${breakdownWidths[index] || 0}%` }}
                      transition={{ duration: 1.2, delay: index * 0.1 }}
                      className={`h-full bg-gradient-to-r ${item.gradient}`}
                    />
                  </div>
                  <span className="text-white font-semibold min-w-[3rem] text-right">
                    {item.percent}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* Left Column - Main Metrics */}
        <div className="space-y-8">
          {/* Top Metrics Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {metrics.map((metric, i) => (
              <div
                key={metric.label}
                className={
                  glassCardStyles + " p-5 flex flex-col items-start relative"
                }
                style={{ boxShadow: perfectCardShadow }}
              >
                <div className="flex items-center mb-2">
                  {metric.icon}
                  <span className="ml-2 text-white/80 font-medium text-sm">
                    {metric.label}
                  </span>
                </div>
                <div className="text-2xl font-bold text-white mb-1">
                  {metric.value}
                </div>
                <div
                  className={`text-sm font-medium ${metric.deltaColor} flex items-center`}
                >
                  {metric.delta.startsWith("+") ? (
                    <ArrowUpRight className="w-4 h-4 mr-1" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4 mr-1" />
                  )}
                  {metric.delta}
                </div>

                {/* Animated Progress Bar */}
                <div className="w-full mt-3 bg-white/20 rounded-full h-2 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${barWidths[i] || 0}%` }}
                    transition={{ duration: 1.5, delay: i * 0.1 }}
                    className={`h-full ${metric.color}`}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* GHL Social Performance */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className={glassCardStyles + " p-6"}
            style={{ boxShadow: perfectCardShadow }}
          >
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <Users className="w-6 h-6 mr-3 text-pink-300" />
              GHL Social Performance
            </h2>
            <div className="grid grid-cols-2 gap-4">
              {socialMetrics.map((social) => (
                <div
                  key={social.platform}
                  className="bg-white/10 rounded-lg p-4 backdrop-blur-sm"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white/80 font-medium">
                      {social.platform}
                    </span>
                    <div
                      className={`text-sm font-medium ${social.growth.startsWith("+") ? "text-green-400" : "text-red-400"}`}
                    >
                      {social.growth}
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-white mb-1">
                    {social.followers}
                  </div>
                  <div className="text-sm text-white/60">
                    {social.engagement} engagement
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Right Column - Additional Metrics */}
        <div className="space-y-8">
          {/* Content Generation Pipeline */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className={glassCardStyles + " p-6"}
            style={{ boxShadow: perfectCardShadow }}
          >
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <Zap className="w-6 h-6 mr-3 text-pink-300" />
              Content Generation Pipeline
            </h2>
            <div className="space-y-4">
              {pipelineSteps.map((step, i) => (
                <div
                  key={step.step}
                  className="flex items-center justify-between p-3 bg-white/10 rounded-lg backdrop-blur-sm"
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-8 h-8 rounded-full ${step.color} flex items-center justify-center text-white font-bold text-sm`}
                    >
                      {i + 1}
                    </div>
                    <span className="text-white font-medium">{step.step}</span>
                  </div>
                  <div className="text-white/80 font-semibold">
                    {step.count}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Connect Analytics Cards */}
          <div className="grid grid-cols-1 gap-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className={glassCardStyles + " p-6 text-center"}
              style={{ boxShadow: perfectCardShadow }}
            >
              <TrendingUp className="w-12 h-12 text-pink-300 mx-auto mb-4" />
              <h3 className="text-lg font-bold text-white mb-2">
                Connect Analytics
              </h3>
              <p className="text-white/80 text-sm mb-4">
                Link your Google Analytics for deeper insights
              </p>
              <button className="bg-pink-600 hover:bg-pink-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                Connect Now
              </button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className={glassCardStyles + " p-6 text-center"}
              style={{ boxShadow: perfectCardShadow }}
            >
              <Search className="w-12 h-12 text-pink-300 mx-auto mb-4" />
              <h3 className="text-lg font-bold text-white mb-2">
                Search Console
              </h3>
              <p className="text-white/80 text-sm mb-4">
                Monitor your search performance and rankings
              </p>
              <button className="bg-pink-600 hover:bg-pink-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                Connect Now
              </button>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Full Content Performance Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.7 }}
        className={glassCardStyles + " p-6 mt-8"}
        style={{ boxShadow: perfectCardShadow }}
      >
        <h2 className="text-xl font-bold text-white mb-6 flex items-center">
          <BarChart3 className="w-6 h-6 mr-3 text-pink-300" />
          Full Content Performance
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/20">
                <th className="text-left text-white/80 font-medium py-3 px-2">
                  Content Cluster
                </th>
                <th className="text-left text-white/80 font-medium py-3 px-2">
                  Date
                </th>
                <th className="text-left text-white/80 font-medium py-3 px-2">
                  Format
                </th>
                <th className="text-left text-white/80 font-medium py-3 px-2">
                  Status
                </th>
                <th className="text-left text-white/80 font-medium py-3 px-2">
                  Engagement
                </th>
                <th className="text-left text-white/80 font-medium py-3 px-2">
                  CIA Score
                </th>
                <th className="text-left text-white/80 font-medium py-3 px-2">
                  Authority
                </th>
                <th className="text-left text-white/80 font-medium py-3 px-2">
                  Cross-Platform
                </th>
              </tr>
            </thead>
            <tbody>
              {contentData.map((item) => (
                <tr
                  key={item.cluster}
                  className="border-b border-white/10 hover:bg-white/5 transition-colors"
                >
                  <td className="py-3 px-2 text-white font-medium">
                    {item.cluster}
                  </td>
                  <td className="py-3 px-2 text-white/80">{item.date}</td>
                  <td className="py-3 px-2 text-white/80">{item.format}</td>
                  <td className="py-3 px-2">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        item.status === "Published"
                          ? "bg-green-500/20 text-green-400"
                          : item.status === "Scheduled"
                            ? "bg-yellow-500/20 text-yellow-400"
                            : "bg-blue-500/20 text-blue-400"
                      }`}
                    >
                      {item.status}
                    </span>
                  </td>
                  <td className="py-3 px-2 text-white font-medium">
                    {item.engagement}
                  </td>
                  <td className="py-3 px-2 text-white/80">{item.cia}</td>
                  <td className="py-3 px-2">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        item.authority === "High"
                          ? "bg-pink-500/20 text-pink-400"
                          : item.authority === "Medium"
                            ? "bg-yellow-500/20 text-yellow-400"
                            : "bg-gray-500/20 text-gray-400"
                      }`}
                    >
                      {item.authority}
                    </span>
                  </td>
                  <td className="py-3 px-2">
                    {item.cross ? (
                      <div className="flex items-center space-x-1">
                        <Link className="w-4 h-4 text-pink-400" />
                        <span className="text-pink-400 text-sm">Yes</span>
                      </div>
                    ) : (
                      <span className="text-white/60 text-sm">No</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* AI Content Optimization Recommendations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.8 }}
        className={glassCardStyles + " p-6 mt-8"}
        style={{ boxShadow: perfectCardShadow }}
      >
        <h2 className="text-xl font-bold text-white mb-6 flex items-center">
          <Info className="w-6 h-6 mr-3 text-pink-300" />
          AI Content Optimization Recommendations
        </h2>
        <div className="space-y-4">
          {aiRecommendations.map((rec, i) => (
            <div
              key={i}
              className="p-4 bg-white/10 rounded-lg backdrop-blur-sm"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-white">{rec.title}</h3>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${rec.priorityColor}`}
                >
                  {rec.priority}
                </span>
              </div>
              <p className="text-white/80 text-sm mb-3">{rec.description}</p>
              <div className="text-sm text-white/60">
                <span className="font-medium">Impact:</span> {rec.impact}
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Google Ads Performance Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.9 }}
        className={glassCardStyles + " p-6 mt-8"}
        style={{ boxShadow: perfectCardShadow }}
      >
        <h2 className="text-xl font-bold text-white mb-6 flex items-center">
          <DollarSign className="w-6 h-6 mr-3 text-pink-300" />
          Google Ads Performance - $10k Grant
        </h2>

        {googleAdsData ? (
          <>
            {/* Budget Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white/80 font-medium">
                    Total Budget
                  </span>
                  <DollarSign className="w-5 h-5 text-pink-300" />
                </div>
                <div className="text-2xl font-bold text-white">
                  ${googleAdsData.totalBudget.toLocaleString()}
                </div>
                <div className="text-sm text-white/60 mt-1">
                  Monthly allocation
                </div>
              </div>
              <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white/80 font-medium">Budget Used</span>
                  <PieChart className="w-5 h-5 text-pink-300" />
                </div>
                <div className="text-2xl font-bold text-white">
                  {googleAdsData.budgetUtilization}%
                </div>
                <div className="text-sm text-white/60 mt-1">
                  $
                  {(
                    (googleAdsData.totalBudget *
                      googleAdsData.budgetUtilization) /
                    100
                  ).toFixed(2)}{" "}
                  spent
                </div>
              </div>
              <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white/80 font-medium">
                    Active Clusters
                  </span>
                  <BarChart3 className="w-5 h-5 text-pink-300" />
                </div>
                <div className="text-2xl font-bold text-white">
                  {googleAdsData.campaigns.length}
                </div>
                <div className="text-sm text-white/60 mt-1">
                  Campaigns running
                </div>
              </div>
            </div>

            {/* Campaign Performance Table */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-white mb-4">
                Campaign Performance by Cluster
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/20">
                      <th className="text-left text-white/80 font-medium py-3 px-2">
                        Cluster
                      </th>
                      <th className="text-left text-white/80 font-medium py-3 px-2">
                        Impressions
                      </th>
                      <th className="text-left text-white/80 font-medium py-3 px-2">
                        Clicks
                      </th>
                      <th className="text-left text-white/80 font-medium py-3 px-2">
                        CTR
                      </th>
                      <th className="text-left text-white/80 font-medium py-3 px-2">
                        Conversions
                      </th>
                      <th className="text-left text-white/80 font-medium py-3 px-2">
                        Spend
                      </th>
                      <th className="text-left text-white/80 font-medium py-3 px-2">
                        ROAS
                      </th>
                      <th className="text-left text-white/80 font-medium py-3 px-2">
                        Score
                      </th>
                      <th className="text-left text-white/80 font-medium py-3 px-2">
                        Action
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {googleAdsData.campaigns
                      .sort((a, b) => b.performanceScore - a.performanceScore)
                      .map((campaign) => {
                        const isLowPerformer = campaign.performanceScore < 70;
                        return (
                          <tr
                            key={campaign.campaignId}
                            className="border-b border-white/10 hover:bg-white/5 transition-colors"
                          >
                            <td className="py-3 px-2">
                              <div>
                                <div className="text-white font-medium">
                                  {campaign.cluster}
                                </div>
                                <div className="text-white/60 text-xs">
                                  {campaign.campaignName}
                                </div>
                              </div>
                            </td>
                            <td className="py-3 px-2 text-white/80">
                              {campaign.impressions.toLocaleString()}
                            </td>
                            <td className="py-3 px-2 text-white/80">
                              {campaign.clicks.toLocaleString()}
                            </td>
                            <td className="py-3 px-2 text-white/80">
                              {campaign.ctr.toFixed(2)}%
                            </td>
                            <td className="py-3 px-2 text-white/80">
                              {campaign.conversions}
                            </td>
                            <td className="py-3 px-2 text-white/80">
                              ${campaign.spend.toFixed(2)}
                            </td>
                            <td className="py-3 px-2">
                              <span
                                className={`font-medium ${
                                  campaign.roas >= 3
                                    ? "text-green-400"
                                    : campaign.roas >= 2
                                      ? "text-yellow-400"
                                      : "text-red-400"
                                }`}
                              >
                                {campaign.roas.toFixed(2)}x
                              </span>
                            </td>
                            <td className="py-3 px-2">
                              <div className="flex items-center">
                                <div className="w-16 bg-white/20 rounded-full h-2 mr-2">
                                  <div
                                    className={`h-full rounded-full ${
                                      campaign.performanceScore >= 80
                                        ? "bg-green-500"
                                        : campaign.performanceScore >= 60
                                          ? "bg-yellow-500"
                                          : "bg-red-500"
                                    }`}
                                    style={{
                                      width: `${campaign.performanceScore}%`,
                                    }}
                                  />
                                </div>
                                <span className="text-white/80 text-sm">
                                  {campaign.performanceScore}
                                </span>
                              </div>
                            </td>
                            <td className="py-3 px-2">
                              {isLowPerformer && (
                                <button
                                  onClick={() =>
                                    handleBudgetRotation(campaign.campaignId)
                                  }
                                  disabled={rotateBudget.isLoading}
                                  className="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-sm font-medium transition-colors flex items-center"
                                >
                                  <RotateCw className="w-3 h-3 mr-1" />
                                  Rotate
                                </button>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Low Performer Alert */}
            {googleAdsData.campaigns.some((c) => c.performanceScore < 70) && (
              <div className="bg-red-500/10 border border-red-400/30 rounded-lg p-4">
                <div className="flex items-start">
                  <AlertCircle className="w-5 h-5 text-red-400 mr-3 mt-0.5" />
                  <div>
                    <h4 className="text-red-300 font-semibold mb-1">
                      Low Performing Campaign Detected
                    </h4>
                    <p className="text-red-300/80 text-sm">
                      One or more campaigns are performing below threshold (70
                      score). Consider rotating budget to new high-opportunity
                      clusters identified by CIA.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </>
        ) : googleAdsLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white" />
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-white/60">No Google Ads data available</p>
          </div>
        )}
      </motion.div>
    </PageLayout>
  );
};

export default PerformancePage;
