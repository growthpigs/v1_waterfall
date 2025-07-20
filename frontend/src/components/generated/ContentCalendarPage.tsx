"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  ChevronLeft,
  ChevronRight,
  Clock,
  CheckCircle,
  Edit3,
  Instagram,
  Twitter,
  Linkedin,
  Facebook,
  Youtube,
  MessageSquare,
  BarChart3,
  ArrowRight,
  TrendingUp,
  Zap,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import PageLayout from "../shared/PageLayout";
import PageHeader from "../shared/PageHeader";
import { perfectCardShadow, glassCardStyles } from "../../lib/utils";

interface ContentCard {
  id: string;
  platform: "instagram" | "twitter" | "linkedin" | "facebook" | "youtube";
  content: string;
  time: string;
  status: "published" | "scheduled" | "draft";
  type: "post" | "story" | "reel" | "video";
  engagement?: number;
}

interface TimeSlot {
  hour: number;
  label: string;
}

interface DayColumn {
  date: string;
  dayName: string;
  dayNumber: number;
  isToday: boolean;
  content: ContentCard[];
}

const timeSlots: TimeSlot[] = [
  { hour: 6, label: "6 AM" },
  { hour: 7, label: "7 AM" },
  { hour: 8, label: "8 AM" },
  { hour: 9, label: "9 AM" },
  { hour: 10, label: "10 AM" },
  { hour: 11, label: "11 AM" },
  { hour: 12, label: "12 PM" },
  { hour: 13, label: "1 PM" },
  { hour: 14, label: "2 PM" },
  { hour: 15, label: "3 PM" },
  { hour: 16, label: "4 PM" },
  { hour: 17, label: "5 PM" },
  { hour: 18, label: "6 PM" },
  { hour: 19, label: "7 PM" },
  { hour: 20, label: "8 PM" },
  { hour: 21, label: "9 PM" },
  { hour: 22, label: "10 PM" },
  { hour: 23, label: "11 PM" },
];

const sampleContent: ContentCard[] = [
  {
    id: "1",
    platform: "instagram",
    content: "AI Productivity Tips #1",
    time: "9:00",
    status: "published",
    type: "post",
    engagement: 85,
  },
  {
    id: "2",
    platform: "twitter",
    content: "Thread: 5 AI Tools for Content",
    time: "14:30",
    status: "scheduled",
    type: "post",
  },
  {
    id: "3",
    platform: "linkedin",
    content: "Professional AI Insights",
    time: "16:00",
    status: "draft",
    type: "post",
  },
  {
    id: "4",
    platform: "youtube",
    content: "AI Tutorial Video",
    time: "19:00",
    status: "scheduled",
    type: "video",
  },
];

const generateWeekData = (): DayColumn[] => {
  const today = new Date();
  const startOfWeek = new Date(today);
  startOfWeek.setDate(today.getDate() - today.getDay());

  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(startOfWeek);
    date.setDate(startOfWeek.getDate() + index);

    return {
      date: date.toISOString().split("T")[0],
      dayName: date.toLocaleDateString("en-US", { weekday: "short" }),
      dayNumber: date.getDate(),
      isToday: date.toDateString() === today.toDateString(),
      content:
        index < 4
          ? sampleContent.slice(0, Math.floor(Math.random() * 3) + 1)
          : [],
    };
  });
};

const ContentCalendarPage: React.FC = () => {
  const navigate = useNavigate();
  const [currentView, setCurrentView] = useState<"month" | "week" | "day">(
    "week",
  );
  const [weekData] = useState<DayColumn[]>(generateWeekData());

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case "instagram":
        return Instagram;
      case "twitter":
        return Twitter;
      case "linkedin":
        return Linkedin;
      case "facebook":
        return Facebook;
      case "youtube":
        return Youtube;
      default:
        return MessageSquare;
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case "instagram":
        return "bg-orange-400";
      case "twitter":
        return "bg-orange-600";
      case "linkedin":
        return "bg-orange-500";
      case "facebook":
        return "bg-orange-300";
      case "youtube":
        return "bg-orange-700";
      default:
        return "bg-orange-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "published":
        return <CheckCircle className="w-3 h-3 text-green-400" />;
      case "scheduled":
        return <Clock className="w-3 h-3 text-yellow-400" />;
      case "draft":
        return <Edit3 className="w-3 h-3 text-gray-400" />;
      default:
        return null;
    }
  };

  return (
    <PageLayout
      pageTitle="Content Calendar"
      placeholder="Ask about content scheduling and optimization..."
    >
      {/* Orange gradient background with warm accents */}
      <div className="fixed inset-0 bg-gradient-to-br from-orange-600 via-orange-700 to-red-800 -z-10" />

      {/* Header - Global Standard */}
      <PageHeader
        title="Content Calendar"
        subtitle="Schedule, manage, and optimize your content across all platforms"
      />

      {/* Calendar Controls */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="mb-8"
      >
        <div
          className={glassCardStyles + " p-6"}
          style={{ boxShadow: perfectCardShadow }}
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="flex items-center bg-white/10 rounded-lg p-1">
                {["Month", "Week", "Day"].map((view) => (
                  <button
                    key={view}
                    onClick={() =>
                      setCurrentView(
                        view.toLowerCase() as "month" | "week" | "day",
                      )
                    }
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      currentView === view.toLowerCase()
                        ? "bg-white/20 text-white"
                        : "text-white/70 hover:text-white"
                    }`}
                  >
                    {view}
                  </button>
                ))}
              </div>
              <div className="flex items-center space-x-2">
                <button className="p-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors">
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="text-white font-medium px-4">
                  {currentView === "month" && "December 2024"}
                  {currentView === "week" && "Week of Dec 16-22, 2024"}
                  {currentView === "day" &&
                    new Date().toLocaleDateString("en-US", {
                      month: "long",
                      day: "numeric",
                      year: "numeric",
                    })}
                </span>
                <button className="p-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors">
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-white/70 text-sm">
                {currentView === "month" && (
                  <>
                    <span className="font-medium text-white">96</span> posts
                    this month
                  </>
                )}
                {currentView === "week" && (
                  <>
                    <span className="font-medium text-white">24</span> posts
                    this week
                  </>
                )}
                {currentView === "day" && (
                  <>
                    <span className="font-medium text-white">6</span> posts
                    today
                  </>
                )}
              </div>
              <button
                onClick={() => navigate("/content-engine")}
                className="px-4 py-2 bg-orange-500/80 hover:bg-orange-500 text-white rounded-lg transition-colors"
              >
                Add Content
              </button>
            </div>
          </div>

          {/* Weekly Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/5 rounded-lg p-4">
              <div className="text-white/70 text-sm mb-1">Total Posts</div>
              <div className="text-2xl font-bold text-white">24</div>
              <div className="text-green-400 text-xs flex items-center mt-1">
                <TrendingUp className="w-3 h-3 mr-1" />
                +12% vs last week
              </div>
            </div>
            <div className="bg-white/5 rounded-lg p-4">
              <div className="text-white/70 text-sm mb-1">Scheduled</div>
              <div className="text-2xl font-bold text-yellow-400">8</div>
              <div className="text-white/60 text-xs mt-1">Ready to publish</div>
            </div>
            <div className="bg-white/5 rounded-lg p-4">
              <div className="text-white/70 text-sm mb-1">Published</div>
              <div className="text-2xl font-bold text-green-400">12</div>
              <div className="text-white/60 text-xs mt-1">This week</div>
            </div>
            <div className="bg-white/5 rounded-lg p-4">
              <div className="text-white/70 text-sm mb-1">Engagement</div>
              <div className="text-2xl font-bold text-orange-300">89%</div>
              <div className="text-green-400 text-xs flex items-center mt-1">
                <TrendingUp className="w-3 h-3 mr-1" />
                +5% avg rate
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Calendar Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="mb-8"
      >
        <div
          className={glassCardStyles + " p-6"}
          style={{ boxShadow: perfectCardShadow }}
        >
          {currentView === "week" && (
            <div className="grid grid-cols-8 gap-4">
              {/* Time Column */}
              <div className="space-y-4">
                <div className="h-12 flex items-center justify-center">
                  <span className="text-white/70 text-sm font-medium">
                    Time
                  </span>
                </div>
                {timeSlots.map((slot) => (
                  <div
                    key={slot.hour}
                    className="h-16 flex items-center justify-center"
                  >
                    <span className="text-white/60 text-xs">{slot.label}</span>
                  </div>
                ))}
              </div>

              {/* Day Columns */}
              {weekData.map((day) => (
                <div key={day.date} className="space-y-4">
                  {/* Day Header */}
                  <div
                    className={`h-12 flex flex-col items-center justify-center rounded-lg ${
                      day.isToday
                        ? "bg-orange-500/20 border border-orange-400/40"
                        : "bg-white/5"
                    }`}
                  >
                    <span className="text-white text-sm font-medium">
                      {day.dayName}
                    </span>
                    <span
                      className={`text-xs ${day.isToday ? "text-orange-200" : "text-white/60"}`}
                    >
                      {day.dayNumber}
                    </span>
                  </div>

                  {/* Time Slots */}
                  {timeSlots.map((slot) => {
                    const contentForSlot = day.content.find(
                      (c) => parseInt(c.time.split(":")[0]) === slot.hour,
                    );
                    return (
                      <div
                        key={`${day.date}-${slot.hour}`}
                        className="h-16 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors relative"
                      >
                        {contentForSlot && (
                          <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className={`absolute inset-1 ${getPlatformColor(contentForSlot.platform)} rounded-md p-2 cursor-pointer`}
                          >
                            <div className="flex items-center justify-between mb-1">
                              {React.createElement(
                                getPlatformIcon(contentForSlot.platform),
                                {
                                  className: "w-3 h-3 text-white",
                                },
                              )}
                              {getStatusIcon(contentForSlot.status)}
                            </div>
                            <div className="text-white text-xs font-medium truncate">
                              {contentForSlot.content}
                            </div>
                            <div className="text-white/70 text-xs">
                              {contentForSlot.time}
                            </div>
                          </motion.div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          )}

          {currentView === "day" && (
            <div className="space-y-4">
              {/* Day View Header */}
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-white">
                  Today -{" "}
                  {new Date().toLocaleDateString("en-US", {
                    weekday: "long",
                    month: "long",
                    day: "numeric",
                  })}
                </h3>
                <div className="text-white/70 text-sm">
                  <span className="font-medium text-white">6</span> posts
                  scheduled
                </div>
              </div>

              {/* Hourly Schedule */}
              <div className="grid grid-cols-1 gap-2">
                {timeSlots.map((slot) => {
                  const todayContent = weekData
                    .find((day) => day.isToday)
                    ?.content.find(
                      (c) => parseInt(c.time.split(":")[0]) === slot.hour,
                    );

                  return (
                    <div
                      key={slot.hour}
                      className="flex items-center bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors p-4"
                    >
                      <div className="w-20 text-white/60 text-sm font-medium">
                        {slot.label}
                      </div>

                      <div className="flex-1 ml-6">
                        {todayContent ? (
                          <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className={`${getPlatformColor(todayContent.platform)} rounded-lg p-4 flex items-center justify-between`}
                          >
                            <div className="flex items-center space-x-3">
                              {React.createElement(
                                getPlatformIcon(todayContent.platform),
                                {
                                  className: "w-5 h-5 text-white",
                                },
                              )}
                              <div>
                                <div className="text-white font-medium">
                                  {todayContent.content}
                                </div>
                                <div className="text-white/70 text-sm">
                                  {todayContent.time} • {todayContent.type}
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(todayContent.status)}
                              <button className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors">
                                <Edit3 className="w-4 h-4 text-white" />
                              </button>
                            </div>
                          </motion.div>
                        ) : (
                          <div className="text-white/40 text-sm italic">
                            No content scheduled
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {currentView === "month" && (
            <div className="space-y-4">
              {/* Month View Header */}
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-white">December 2024</h3>
                <div className="text-white/70 text-sm">
                  <span className="font-medium text-white">96</span> posts this
                  month
                </div>
              </div>

              {/* Month Calendar Grid */}
              <div className="grid grid-cols-7 gap-2">
                {/* Weekday Headers */}
                {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(
                  (day) => (
                    <div
                      key={day}
                      className="h-12 flex items-center justify-center bg-white/5 rounded-lg"
                    >
                      <span className="text-white/70 text-sm font-medium">
                        {day}
                      </span>
                    </div>
                  ),
                )}

                {/* Calendar Days */}
                {Array.from({ length: 35 }, (_, index) => {
                  const dayNumber = index - 6; // Start from previous month's last days
                  const isCurrentMonth = dayNumber > 0 && dayNumber <= 31;
                  const isToday =
                    dayNumber === new Date().getDate() && isCurrentMonth;
                  const hasContent = isCurrentMonth && Math.random() > 0.6; // Random content for demo

                  return (
                    <div
                      key={index}
                      className={`h-24 rounded-lg border transition-colors ${
                        isCurrentMonth
                          ? isToday
                            ? "bg-orange-500/20 border-orange-400/40"
                            : "bg-white/5 border-white/10 hover:bg-white/10"
                          : "bg-white/5 border-white/5"
                      }`}
                    >
                      <div className="p-2 h-full flex flex-col">
                        <span
                          className={`text-xs ${
                            isCurrentMonth
                              ? isToday
                                ? "text-orange-200 font-bold"
                                : "text-white"
                              : "text-white/30"
                          }`}
                        >
                          {isCurrentMonth ? dayNumber : ""}
                        </span>

                        {hasContent && isCurrentMonth && (
                          <div className="flex-1 mt-1 space-y-1">
                            <div className="bg-orange-400 rounded text-xs px-1 py-0.5 text-white truncate">
                              Post
                            </div>
                            {Math.random() > 0.7 && (
                              <div className="bg-orange-600 rounded text-xs px-1 py-0.5 text-white truncate">
                                Story
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </motion.div>

      {/* Bottom Section: Pipeline & Analytics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-8"
      >
        {/* Publishing Pipeline */}
        <div
          className={glassCardStyles + " p-6"}
          style={{ boxShadow: perfectCardShadow }}
        >
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            <ArrowRight className="w-5 h-5 mr-2" />
            Publishing Pipeline
          </h3>

          <div className="space-y-4">
            {[
              { stage: "Generation", count: 5, color: "blue" },
              { stage: "Review", count: 3, color: "yellow" },
              { stage: "Approved", count: 8, color: "green" },
              { stage: "Scheduled", count: 12, color: "purple" },
              { stage: "Live", count: 24, color: "pink" },
            ].map((item, index) => (
              <div
                key={item.stage}
                className="flex items-center justify-between p-3 bg-white/5 rounded-lg"
              >
                <div className="flex items-center">
                  <div
                    className={`w-3 h-3 rounded-full mr-3 ${
                      item.color === "blue"
                        ? "bg-blue-400"
                        : item.color === "yellow"
                          ? "bg-yellow-400"
                          : item.color === "green"
                            ? "bg-green-400"
                            : item.color === "purple"
                              ? "bg-orange-400"
                              : "bg-pink-400"
                    }`}
                  />
                  <span className="text-white font-medium">{item.stage}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-white/70">{item.count}</span>
                  {index < 4 && (
                    <ArrowRight className="w-4 h-4 text-white/40" />
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex items-center space-x-3">
            <button className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors text-sm">
              Auto-Schedule
            </button>
            <button className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors text-sm">
              Bulk Actions
            </button>
          </div>
        </div>

        {/* Platform Analytics */}
        <div
          className={glassCardStyles + " p-6"}
          style={{ boxShadow: perfectCardShadow }}
        >
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            Platform Optimization
          </h3>

          <div className="space-y-4">
            {[
              {
                platform: "Instagram",
                optimal: "9:00 AM",
                engagement: "89%",
                icon: Instagram,
                color: "bg-orange-400",
              },
              {
                platform: "LinkedIn",
                optimal: "8:00 AM",
                engagement: "76%",
                icon: Linkedin,
                color: "bg-orange-500",
              },
              {
                platform: "Twitter",
                optimal: "2:30 PM",
                engagement: "82%",
                icon: Twitter,
                color: "bg-orange-600",
              },
              {
                platform: "YouTube",
                optimal: "7:00 PM",
                engagement: "91%",
                icon: Youtube,
                color: "bg-orange-700",
              },
            ].map((platform) => (
              <div
                key={platform.platform}
                className="flex items-center justify-between p-3 bg-white/5 rounded-lg"
              >
                <div className="flex items-center">
                  <div
                    className={`w-8 h-8 rounded-lg ${platform.color} flex items-center justify-center mr-3`}
                  >
                    {React.createElement(platform.icon, {
                      className: "w-4 h-4 text-white",
                    })}
                  </div>
                  <div>
                    <div className="text-white font-medium text-sm">
                      {platform.platform}
                    </div>
                    <div className="text-white/60 text-xs">
                      Best: {platform.optimal}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-white font-medium text-sm">
                    {platform.engagement}
                  </div>
                  <div className="text-white/60 text-xs">Avg engagement</div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-3 bg-green-500/20 border border-green-400/30 rounded-lg">
            <div className="flex items-center text-green-400 text-sm font-medium mb-1">
              <Zap className="w-4 h-4 mr-2" />
              GHL Sync Active
            </div>
            <div className="text-white/70 text-xs">
              Auto-posting enabled • Last sync: 2 min ago
            </div>
          </div>
        </div>
      </motion.div>
    </PageLayout>
  );
};

export default ContentCalendarPage;
