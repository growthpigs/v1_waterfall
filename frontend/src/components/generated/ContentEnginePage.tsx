"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  FileText,
  Calendar,
  ChevronLeft,
  ChevronRight,
  Settings,
  Play,
  CheckCircle,
  Clock,
  AlertCircle,
  Instagram,
  Twitter,
  Linkedin,
  Facebook,
  Youtube,
  Mic,
  Mail,
  Video,
  BookOpen,
  Download,
  Target,
  Zap,
  BarChart3,
  TrendingUp,
  Send,
  Loader2,
} from "lucide-react";
import PageLayout from "../shared/PageLayout";
import PageHeader from "../shared/PageHeader";
import { useNavigate } from "react-router-dom";
import { perfectCardShadow, glassCardStyles } from "../../lib/utils";
import { useGHLPost, useGHLSchedules } from "../../services/ghlService";
// import { z } from "zod";

interface ContentFormat {
  id: string;
  title: string;
  category: "blog" | "social" | "audio-video";
  status: "ready" | "in-progress" | "scheduled" | "published";
  icon: React.ComponentType<{
    className?: string;
  }>;
  enabled: boolean;
  description: string;
  authorityScore: string;
  customerPsychology: string;
  alignment: string;
}

interface ContentEnginePageProps {
  selectedCluster?: string;
  weekOffset?: number;
  enabledFormats?: string[];
  onFormatToggle?: (formatId: string, enabled: boolean) => void;
  onPublishContent?: (contentId: string, platform: string) => void;
  onClusterChange?: (clusterId: string) => void;
}

const contentFormats: ContentFormat[] = [
  // Blog Content (Blue)
  {
    id: "ai-search-blog",
    title: "AI Search Blog",
    category: "blog",
    status: "ready",
    icon: Target,
    enabled: true,
    description: "SEO-optimized long-form content",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  {
    id: "epic-pillar",
    title: "Epic Pillar",
    category: "blog",
    status: "in-progress",
    icon: BookOpen,
    enabled: true,
    description: "Comprehensive authority piece",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  {
    id: "supporting-posts",
    title: "Supporting Posts",
    category: "blog",
    status: "scheduled",
    icon: FileText,
    enabled: true,
    description: "3-5 supporting articles",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  {
    id: "advertorial",
    title: "Advertorial",
    category: "blog",
    status: "ready",
    icon: Zap,
    enabled: false,
    description: "Promotional content piece",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  // Social Content (Green)
  {
    id: "instagram",
    title: "Instagram",
    category: "social",
    status: "ready",
    icon: Instagram,
    enabled: true,
    description: "Stories & feed posts",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  {
    id: "twitter",
    title: "X/Twitter",
    category: "social",
    status: "published",
    icon: Twitter,
    enabled: true,
    description: "Thread & single posts",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  {
    id: "linkedin",
    title: "LinkedIn",
    category: "social",
    status: "in-progress",
    icon: Linkedin,
    enabled: true,
    description: "Professional content",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  {
    id: "facebook",
    title: "Facebook",
    category: "social",
    status: "scheduled",
    icon: Facebook,
    enabled: false,
    description: "Community posts",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  {
    id: "tiktok",
    title: "TikTok",
    category: "social",
    status: "ready",
    icon: Video,
    enabled: true,
    description: "Short-form videos",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  {
    id: "youtube-shorts",
    title: "YouTube Shorts",
    category: "social",
    status: "ready",
    icon: Youtube,
    enabled: true,
    description: "Vertical video content",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  // Audio/Video Content (Orange)
  {
    id: "pillar-podcast",
    title: "Pillar Podcast",
    category: "audio-video",
    status: "in-progress",
    icon: Mic,
    enabled: true,
    description: "Long-form audio content",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  {
    id: "email-series",
    title: "Email Series",
    category: "audio-video",
    status: "ready",
    icon: Mail,
    enabled: true,
    description: "5-part email sequence",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  {
    id: "webinar",
    title: "Webinar",
    category: "audio-video",
    status: "scheduled",
    icon: Video,
    enabled: false,
    description: "Live presentation",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  {
    id: "case-study",
    title: "Case Study",
    category: "audio-video",
    status: "ready",
    icon: BarChart3,
    enabled: true,
    description: "Success story analysis",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
  {
    id: "lead-magnet",
    title: "Lead Magnet",
    category: "audio-video",
    status: "published",
    icon: Download,
    enabled: true,
    description: "Free resource offer",
    authorityScore: "Authority Score: Customer Psychology:",
    customerPsychology: "Customer Psychology:",
    alignment: "Aligned",
  },
];

const ContentEnginePage: React.FC<ContentEnginePageProps> = ({
  selectedCluster = "AI Productivity Hacks",
  weekOffset = 0,
  // enabledFormats = [],
  onFormatToggle,
  onPublishContent,
  // onClusterChange,
}) => {
  const navigate = useNavigate();
  const [currentWeek, setCurrentWeek] = useState(weekOffset);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [contentText, setContentText] = useState("");
  const [scheduleDate, setScheduleDate] = useState(
    new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
  );

  const ghlPost = useGHLPost();
  const { data: schedules } = useGHLSchedules();

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "blog":
        return "blue";
      case "social":
        return "green";
      case "audio-video":
        return "orange";
      default:
        return "gray";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "ready":
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case "in-progress":
        return <Clock className="w-4 h-4 text-yellow-400" />;
      case "scheduled":
        return <Calendar className="w-4 h-4 text-blue-400" />;
      case "published":
        return <CheckCircle className="w-4 h-4 text-emerald-400" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "ready":
        return "Ready ✅";
      case "in-progress":
        return "In Progress 🟡";
      case "scheduled":
        return "Scheduled 📅";
      case "published":
        return "Published 🔴";
      default:
        return "Unknown";
    }
  };

  const handleFormatToggle = (formatId: string, enabled: boolean) => {
    onFormatToggle?.(formatId, enabled);
  };

  const handlePublishContent = (contentId: string, platform: string) => {
    onPublishContent?.(contentId, platform);
  };

  const handleGHLPublish = async () => {
    if (selectedPlatforms.length === 0 || !contentText) {
      alert("Please select at least one platform and enter content");
      return;
    }

    try {
      for (const platform of selectedPlatforms) {
        await ghlPost.mutateAsync({
          platform,
          content: {
            text: contentText,
            scheduleDate: new Date(scheduleDate),
          },
        });
      }

      // Reset form
      setSelectedPlatforms([]);
      setContentText("");
      setScheduleDate(
        new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
      );
    } catch (error) {
      console.error("Failed to publish content:", error);
    }
  };

  const togglePlatform = (platform: string) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platform)
        ? prev.filter((p) => p !== platform)
        : [...prev, platform],
    );
  };

  return (
    <PageLayout
      pageTitle="Content Engine"
      placeholder="Ask Content Engine to transform viral opportunities..."
    >
      {/* Green gradient background per THEME_CONSTANTS.md */}
      <div className="fixed inset-0 bg-gradient-to-br from-green-600 via-green-700 to-emerald-800 -z-10" />

      <PageHeader
        title="Content Engine"
        subtitle="Transform viral opportunities into authority-building content across all platforms"
      />

      {/* Enhanced Content Cluster Overview */}
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
          delay: 0.1,
        }}
        className="mb-8"
      >
        <div
          className={glassCardStyles + " p-6"}
          style={{ boxShadow: perfectCardShadow }}
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-emerald-400 rounded-full mr-3"></div>
              <h2 className="text-xl font-bold text-white">
                Content Cluster: {selectedCluster}
              </h2>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setCurrentWeek(currentWeek - 1)}
                className="p-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-white font-medium px-4">
                Week{" "}
                {currentWeek === 0
                  ? "Current"
                  : currentWeek > 0
                    ? `+${currentWeek}`
                    : currentWeek}
              </span>
              <button
                onClick={() => setCurrentWeek(currentWeek + 1)}
                className="p-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Enhanced cluster info */}
          <div className="bg-white/10 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-4">
                <div className="text-white/70 text-sm">
                  Convergence Score:{" "}
                  <span className="text-white font-bold">94%</span>
                </div>
                <div className="text-white/70 text-sm">
                  Sources: Grok Trending + Reddit Marketing
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded">
                  CIA Intelligence
                </span>
                <span className="px-2 py-1 bg-orange-500/20 text-orange-300 text-xs rounded">
                  Customer Pain Point Focus
                </span>
              </div>
            </div>
            <p className="text-white/80 text-sm">
              High viral opportunity detected through convergence analysis.
              Customer psychology integration active.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-white/70 text-sm mb-1">Total Formats</div>
              <div className="text-2xl font-bold text-white">15</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-white/70 text-sm mb-1">Ready to Publish</div>
              <div className="text-2xl font-bold text-green-400">8</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-white/70 text-sm mb-1">In Progress</div>
              <div className="text-2xl font-bold text-yellow-400">4</div>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button className="px-4 py-2 bg-emerald-500/20 text-emerald-300 rounded-lg text-sm hover:bg-emerald-500/30 transition-colors">
                Generate Next Cluster
              </button>
              <button className="px-4 py-2 bg-white/10 text-white/80 rounded-lg text-sm hover:bg-white/20 transition-colors">
                Cluster Performance History
              </button>
            </div>
            <div className="flex items-center text-white/70 text-sm">
              <span className="mr-2">Viral momentum:</span>
              <TrendingUp className="w-4 h-4 mr-1" />
              <span>Trending upward</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Enhanced Content Format Grid */}
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
          delay: 0.2,
        }}
        className="mb-8"
      >
        <div
          className={glassCardStyles + " p-6"}
          style={{ boxShadow: perfectCardShadow }}
        >
          <h3 className="text-xl font-bold text-white mb-6 flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Content Format Grid
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {contentFormats.map((format) => {
              const Icon = format.icon;
              const categoryColor = getCategoryColor(format.category);
              return (
                <motion.div
                  key={format.id}
                  whileHover={{
                    scale: 1.02,
                  }}
                  whileTap={{
                    scale: 0.98,
                  }}
                  className={`relative p-4 rounded-xl border transition-all cursor-pointer ${format.enabled ? `bg-${categoryColor}-500/20 border-${categoryColor}-400/50 hover:bg-${categoryColor}-500/30` : "bg-white/10 border-white/20 hover:bg-white/15"}`}
                >
                  {/* CIA Tag */}
                  <div className="absolute top-2 left-2 px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded">
                    CIA
                  </div>

                  {/* Category Color Indicator */}
                  <div
                    className={`absolute top-2 right-2 w-3 h-3 rounded-full ${categoryColor === "blue" ? "bg-blue-400" : categoryColor === "green" ? "bg-green-400" : categoryColor === "orange" ? "bg-orange-400" : "bg-gray-400"}`}
                  />

                  {/* Content */}
                  <div className="mt-6 mb-3">
                    <div className="flex items-center mb-2">
                      <Icon className="w-5 h-5 text-white mr-2" />
                      <h4 className="text-white font-semibold text-sm">
                        {format.title}
                      </h4>
                    </div>
                    <p className="text-white/70 text-xs mb-3">
                      {format.description}
                    </p>

                    {/* Authority Score and Psychology */}
                    <div className="space-y-1 mb-3">
                      <div className="text-white/60 text-xs">
                        Authority Score:
                        <span className="text-emerald-400 ml-1">
                          Customer Psychology:
                        </span>
                      </div>
                      <div className="text-white/60 text-xs">
                        Customer Psychology:
                        <span className="text-emerald-400 ml-1">✓ Aligned</span>
                      </div>
                    </div>
                  </div>

                  {/* Status */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      {getStatusIcon(format.status)}
                      <span className="text-xs text-white/80 ml-1">
                        {getStatusText(format.status)}
                      </span>
                    </div>
                  </div>

                  {/* Toggle Switch and Play Button */}
                  <div className="flex items-center justify-between">
                    <button
                      onClick={() =>
                        handleFormatToggle(format.id, !format.enabled)
                      }
                      className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${format.enabled ? "bg-green-500" : "bg-gray-600"}`}
                    >
                      <span
                        className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${format.enabled ? "translate-x-5" : "translate-x-1"}`}
                      />
                    </button>

                    {format.status === "ready" && format.enabled && (
                      <button
                        onClick={() =>
                          handlePublishContent(format.id, format.title)
                        }
                        className="px-2 py-1 bg-green-500 hover:bg-green-600 text-white text-xs rounded transition-colors"
                      >
                        <Play className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* Enhanced Publishing Pipeline */}
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
      >
        <div
          className={glassCardStyles + " p-6"}
          style={{ boxShadow: perfectCardShadow }}
        >
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            <Zap className="w-5 h-5 mr-2" />
            Publishing Pipeline
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-500/20 rounded-lg p-4 border border-blue-400/30">
              <h4 className="text-white font-semibold mb-2 flex items-center">
                <BookOpen className="w-4 h-4 mr-2 text-blue-400" />
                Blog Content
              </h4>
              <div className="text-white/70 text-sm space-y-1">
                <div>• 3 of 4 formats enabled</div>
                <div>• 2 ready to publish</div>
                <div>• 1 in progress</div>
              </div>
              <div className="mt-2 text-xs text-blue-300">
                Notion MCP: Connected ✓
              </div>
            </div>

            <div className="bg-green-500/20 rounded-lg p-4 border border-green-400/30">
              <h4 className="text-white font-semibold mb-2 flex items-center">
                <Instagram className="w-4 h-4 mr-2 text-green-400" />
                Social Content
              </h4>
              <div className="text-white/70 text-sm space-y-1">
                <div>• 4 of 6 formats enabled</div>
                <div>• 3 ready to publish</div>
                <div>• 1 published</div>
              </div>
              <div className="mt-2 text-xs text-green-300">
                GHL MCP: Connected ✓
              </div>
            </div>

            <div className="bg-orange-500/20 rounded-lg p-4 border border-orange-400/30">
              <h4 className="text-white font-semibold mb-2 flex items-center">
                <Mic className="w-4 h-4 mr-2 text-orange-400" />
                Audio/Video
              </h4>
              <div className="text-white/70 text-sm space-y-1">
                <div>• 3 of 5 formats enabled</div>
                <div>• 2 ready to publish</div>
                <div>• 1 scheduled</div>
              </div>
              <div className="mt-2 text-xs text-orange-300">
                Cross-Platform Timing: Optimized
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate("/performance")}
                className="px-6 py-2 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg transition-colors"
              >
                Publish All Ready
              </button>
              <button
                onClick={() => navigate("/campaign")}
                className="px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-lg transition-colors"
              >
                Schedule Batch
              </button>
              <button
                onClick={() => navigate("/settings")}
                className="px-6 py-2 bg-white/15 hover:bg-white/20 text-white rounded-lg transition-colors"
              >
                Export All
              </button>
            </div>

            <div className="text-white/70 text-sm">
              Last updated: 2 minutes ago
            </div>
          </div>
        </div>
      </motion.div>

      {/* GHL MCP Publishing Interface */}
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
        className="mt-8"
      >
        <div
          className={glassCardStyles + " p-6"}
          style={{ boxShadow: perfectCardShadow }}
        >
          <h3 className="text-xl font-bold text-white mb-6 flex items-center">
            <Send className="w-5 h-5 mr-2" />
            GHL Social Publishing
          </h3>

          <div className="space-y-6">
            {/* Platform Selection */}
            <div>
              <label className="block text-sm font-medium text-white/80 mb-3">
                Select Platforms
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                {[
                  { id: "instagram", name: "Instagram", icon: Instagram },
                  { id: "twitter", name: "Twitter", icon: Twitter },
                  { id: "linkedin", name: "LinkedIn", icon: Linkedin },
                  { id: "facebook", name: "Facebook", icon: Facebook },
                  { id: "youtube", name: "YouTube", icon: Youtube },
                ].map((platform) => {
                  const Icon = platform.icon;
                  const isSelected = selectedPlatforms.includes(platform.id);
                  return (
                    <button
                      key={platform.id}
                      onClick={() => togglePlatform(platform.id)}
                      className={`p-3 rounded-lg border transition-all ${
                        isSelected
                          ? "bg-emerald-500/30 border-emerald-400/50 text-white"
                          : "bg-white/10 border-white/20 text-white/70 hover:bg-white/20"
                      }`}
                    >
                      <Icon className="w-5 h-5 mx-auto mb-1" />
                      <span className="text-xs">{platform.name}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Content Input */}
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Content
              </label>
              <textarea
                value={contentText}
                onChange={(e) => setContentText(e.target.value)}
                placeholder="Enter your social media content..."
                className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-emerald-400/50 focus:border-transparent resize-none"
                rows={4}
              />
            </div>

            {/* Schedule Date */}
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Schedule Date & Time
              </label>
              <input
                type="datetime-local"
                value={scheduleDate}
                onChange={(e) => setScheduleDate(e.target.value)}
                className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-emerald-400/50 focus:border-transparent"
              />
            </div>

            {/* Publish Button */}
            <div className="flex items-center justify-between">
              <button
                onClick={handleGHLPublish}
                disabled={
                  ghlPost.isLoading ||
                  selectedPlatforms.length === 0 ||
                  !contentText
                }
                className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center ${
                  ghlPost.isLoading ||
                  selectedPlatforms.length === 0 ||
                  !contentText
                    ? "bg-white/20 text-white/60 cursor-not-allowed"
                    : "bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg hover:shadow-xl"
                }`}
              >
                {ghlPost.isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Publishing...
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5 mr-2" />
                    Publish to Selected Platforms
                  </>
                )}
              </button>

              {ghlPost.isSuccess && (
                <div className="text-emerald-400 text-sm flex items-center">
                  <CheckCircle className="w-4 h-4 mr-1" />
                  Successfully published!
                </div>
              )}
            </div>

            {/* Scheduled Posts Preview */}
            {schedules && schedules.schedules.length > 0 && (
              <div className="mt-6 pt-6 border-t border-white/20">
                <h4 className="text-lg font-semibold text-white mb-4">
                  Upcoming Scheduled Posts
                </h4>
                <div className="space-y-3">
                  {schedules.schedules.slice(0, 5).map((schedule) => (
                    <div
                      key={schedule.id}
                      className="flex items-center justify-between p-3 bg-white/10 rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-emerald-500/20 rounded-lg flex items-center justify-center">
                          {schedule.platform === "instagram" && (
                            <Instagram className="w-4 h-4 text-emerald-400" />
                          )}
                          {schedule.platform === "twitter" && (
                            <Twitter className="w-4 h-4 text-emerald-400" />
                          )}
                          {schedule.platform === "linkedin" && (
                            <Linkedin className="w-4 h-4 text-emerald-400" />
                          )}
                          {schedule.platform === "facebook" && (
                            <Facebook className="w-4 h-4 text-emerald-400" />
                          )}
                          {schedule.platform === "youtube" && (
                            <Youtube className="w-4 h-4 text-emerald-400" />
                          )}
                        </div>
                        <div>
                          <p className="text-white text-sm font-medium">
                            {schedule.content}
                          </p>
                          <p className="text-white/60 text-xs">
                            {new Date(schedule.scheduledDate).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          schedule.status === "scheduled"
                            ? "bg-yellow-500/20 text-yellow-400"
                            : schedule.status === "published"
                              ? "bg-green-500/20 text-green-400"
                              : "bg-red-500/20 text-red-400"
                        }`}
                      >
                        {schedule.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </PageLayout>
  );
};

export default ContentEnginePage;
