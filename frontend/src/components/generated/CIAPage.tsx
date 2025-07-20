"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Search,
  Globe,
  Play,
  CheckCircle,
  Clock,
  AlertTriangle,
  Download,
  Send,
  Archive,
  ChevronDown,
  ChevronUp,
  Target,
  Users,
  Shield,
  MapPin,
  FileText,
} from "lucide-react";
import PageLayout from "../shared/PageLayout";
import PageHeader from "../shared/PageHeader";
import {
  perfectCardShadow,
  glassCardStyles,
} from "../../lib/utils";

interface PhaseData {
  id: string;
  label: string;
  description: string;
  status: "pending" | "active" | "completed" | "requires-input";
  progress?: number;
  results?: Record<string, unknown>;
  estimatedTime?: string;
}

interface AnalysisResult {
  phase: string;
  title: string;
  summary: string;
  details: string[];
  icon: React.ComponentType<{
    className?: string;
  }>;
}

interface HumanInputAlert {
  phase: string;
  title: string;
  description: string;
  action: string;
}

const CIAPage: React.FC = () => {
  const [url, setUrl] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [country, setCountry] = useState("United States");
  const [keyPerson, setKeyPerson] = useState("");
  const [testimonialsUrl, setTestimonialsUrl] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [expandedResults, setExpandedResults] = useState<string[]>([]);

  const phases: PhaseData[] = [
    {
      id: "1a",
      label: "Phase 1A",
      description: "Business Foundation",
      status: "completed",
      progress: 100,
    },
    {
      id: "1b",
      label: "Phase 1B",
      description: "Customer Psychology",
      status: "completed",
      progress: 100,
    },
    {
      id: "1c",
      label: "Phase 1C",
      description: "Authority Positioning",
      status: "completed",
      progress: 100,
    },
    {
      id: "1d",
      label: "Phase 1D",
      description: "Competitive Intelligence",
      status: "completed",
      progress: 100,
    },
    {
      id: "2a",
      label: "Phase 2A",
      description: "SEO Intelligence",
      status: "requires-input",
    },
    {
      id: "2b",
      label: "Phase 2B",
      description: "Content Strategy",
      status: "completed",
      progress: 100,
    },
  ];

  const analysisResults: AnalysisResult[] = [
    {
      phase: "1a",
      title: "Business Foundation Analysis",
      summary:
        "Value proposition clarity and competitive positioning identified with 94% confidence",
      details: [
        "Value proposition clarity: Clear differentiation in workflow automation space",
        "Revenue model analysis: SaaS subscription with freemium tier shows strong growth potential",
        "Market positioning: Mid-market focus (50-500 employees) with expansion opportunities",
        "Competitive differentiation: AI-powered insights create sustainable advantage",
      ],
      icon: Target,
    },
    {
      phase: "1b",
      title: "Customer Psychology Profile",
      summary:
        "Pain points and false solutions identified across 3 key personas using Benson framework",
      details: [
        "Primary pain points: Manual processes causing 40% productivity loss",
        "False solutions identified: Band-aid tools that create more complexity",
        "Decision-making triggers: Cost reduction (67%), time savings (89%), compliance (45%)",
        "Buying psychology: Risk-averse, requires social proof and gradual implementation",
      ],
      icon: Users,
    },
    {
      phase: "1c",
      title: "Authority Positioning Assessment",
      summary:
        "K-PoI expertise areas and thought leadership opportunities mapped with Daniel Priestley 5 P's",
      details: [
        "Pitch: Strong technical narrative, needs emotional connection enhancement",
        "Publish: Limited content output, opportunity for thought leadership expansion",
        "Product: Solid core offering, potential for premium tier development",
        "Profile: Industry recognition moderate, speaking opportunities identified",
        "Partnership: Strategic alliances underdeveloped, key connector relationships needed",
      ],
      icon: Shield,
    },
    {
      phase: "1d",
      title: "Competitive Intelligence Summary",
      summary:
        "Direct and indirect competitor analysis revealing market gaps and positioning opportunities",
      details: [
        "Direct competitors: 3 major players with similar feature sets but poor UX",
        "Indirect competitors: 12 point solutions creating integration challenges",
        "Market gaps: Mid-market segment underserved with 67% dissatisfaction rate",
        "Competitive advantages: Superior integration capabilities and AI-driven insights",
        "Vulnerabilities: Limited brand recognition and smaller marketing budget",
      ],
      icon: MapPin,
    },
    {
      phase: "2a",
      title: "Content Strategy Foundation",
      summary:
        "Authority-building content themes and customer journey mapping with SEO prioritization",
      details: [
        "Authority content themes: Workflow optimization, AI integration, industry best practices",
        "Customer journey mapping: Awareness (educational), Consideration (case studies), Decision (demos)",
        "SEO opportunity prioritization: 47 high-value keywords with low competition identified",
        "Content gaps: Technical depth content missing, competitor analysis shows 3x opportunity",
      ],
      icon: FileText,
    },
  ];

  const humanInputAlerts = [
    {
      phase: "2A",
      title: "DataForSEO Keywords Required",
      description:
        "Manual keyword research needed for comprehensive SEO analysis",
      action: "Upload Keywords",
    },
    {
      phase: "3A",
      title: "Perplexity Research Needed",
      description:
        "Additional market research required for competitive analysis",
      action: "Start Research",
    },
  ] as HumanInputAlert[];

  const countries = [
    "United States",
    "United Kingdom",
    "Canada",
    "Australia",
    "Germany",
    "France",
    "Netherlands",
    "Sweden",
    "Japan",
    "Singapore",
  ];

  const handleLaunchAnalysis = () => {
    if (url && country) {
      setIsAnalyzing(true);
      // Simulate analysis start
      setTimeout(() => setIsAnalyzing(false), 2000);
    }
  };

  const toggleResultExpansion = (phaseId: string) => {
    setExpandedResults((prev) =>
      prev.includes(phaseId)
        ? prev.filter((id) => id !== phaseId)
        : [...prev, phaseId],
    );
  };

  const getPhaseStatusColor = (status: PhaseData["status"]) => {
    switch (status) {
      case "completed":
        return "text-green-400";
      case "active":
        return "text-blue-400";
      case "requires-input":
        return "text-yellow-400";
      default:
        return "text-white/40";
    }
  };

  const getPhaseStatusIcon = (status: PhaseData["status"]) => {
    switch (status) {
      case "completed":
        return CheckCircle;
      case "active":
        return Clock;
      case "requires-input":
        return AlertTriangle;
      default:
        return Clock;
    }
  };

  return (
    <PageLayout
      pageTitle="Central Intelligence Arsenal"
      placeholder="Ask CIA for content insights..."
    >
      {/* Full-screen gradient background */}
      <div className="fixed inset-0 bg-gradient-to-br from-blue-400 via-blue-600 to-blue-900 -z-10" />

      {/* Header Section - Global Standard */}
      <PageHeader
        title="Central Intelligence Arsenal"
        subtitle="Comprehensive brand analysis and intelligence gathering system"
      />

      {/* Phase Progress Bar - Reduced margin */}
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
        className={`${glassCardStyles} mb-6`}
        style={{ boxShadow: perfectCardShadow }}
      >
        <div className="p-6 mb-6">
          <h2 className="text-xl font-semibold text-white mb-6">
            Analysis Progress
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {phases.map((phase, index) => {
              const StatusIcon = getPhaseStatusIcon(phase.status);
              return (
                <motion.div
                  key={phase.id}
                  initial={{
                    opacity: 0,
                    scale: 0.9,
                  }}
                  animate={{
                    opacity: 1,
                    scale: 1,
                  }}
                  transition={{
                    duration: 0.4,
                    delay: 0.1 * index,
                  }}
                  className={`relative p-4 rounded-xl border transition-all duration-300 ${phase.status === "active" ? "bg-blue-500/20 border-blue-400/50" : phase.status === "completed" ? "bg-green-500/20 border-green-400/50" : phase.status === "requires-input" ? "bg-yellow-500/20 border-yellow-400/50" : "bg-white/5 border-white/20"}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-white">
                      {phase.label}
                    </span>
                    <StatusIcon
                      className={`w-4 h-4 ${getPhaseStatusColor(phase.status)}`}
                    />
                  </div>
                  <p className="text-xs text-white/70 mb-2">
                    {phase.description}
                  </p>
                  {phase.progress && (
                    <div className="w-full bg-white/20 rounded-full h-1.5">
                      <div
                        className="bg-blue-400 h-1.5 rounded-full transition-all duration-500"
                        style={{
                          width: `${phase.progress}%`,
                        }}
                      />
                    </div>
                  )}
                  {phase.estimatedTime && (
                    <p className="text-xs text-blue-300 mt-1">
                      {phase.estimatedTime} remaining
                    </p>
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* URL Analysis Input Section - Reduced margin */}
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
          delay: 0.5,
        }}
        className={`${glassCardStyles} mb-6`}
        style={{ boxShadow: perfectCardShadow }}
      >
        <div className="p-6 mb-6">
          <h2 className="text-xl font-semibold text-white mb-6">
            Launch New Analysis
          </h2>

          {/* Target URL - Full Width */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-white/80 mb-2">
              Target URL <span className="text-red-400">*</span>
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/60" />
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full pl-10 pr-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-transparent"
                required
              />
            </div>
          </div>

          {/* Row 2: Company Name | Country */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Company Name
              </label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="Enter company name"
                className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Country <span className="text-red-400">*</span>
              </label>
              <div className="relative">
                <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/60" />
                <select
                  value={country}
                  onChange={(e) => setCountry(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-transparent appearance-none"
                  required
                >
                  {countries.map((c) => (
                    <option
                      key={c}
                      value={c}
                      className="bg-gray-800 text-white"
                    >
                      {c}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Row 3: K-PoI | Testimonials URL */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Key Person of Influence (K-PoI)
              </label>
              <input
                type="text"
                value={keyPerson}
                onChange={(e) => setKeyPerson(e.target.value)}
                placeholder="Enter key person name (CEO, founder, etc.)"
                className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-transparent"
              />
              <p className="text-xs text-white/60 mt-1">
                Optional: Person to analyze for authority positioning
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Testimonials URL
              </label>
              <input
                type="url"
                value={testimonialsUrl}
                onChange={(e) => setTestimonialsUrl(e.target.value)}
                placeholder="https://testimonials-page.com or Google My Business URL"
                className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-transparent"
              />
              <p className="text-xs text-white/60 mt-1">
                Optional: URL with customer testimonials for analysis
              </p>
            </div>
          </div>

          <motion.button
            onClick={handleLaunchAnalysis}
            disabled={!url || !country || isAnalyzing}
            whileHover={{
              scale: url && country ? 1.02 : 1,
            }}
            whileTap={{
              scale: url && country ? 0.98 : 1,
            }}
            className={`w-full py-4 rounded-xl font-semibold transition-all duration-300 ${
              url && country && !isAnalyzing
                ? "bg-blue-500/80 hover:bg-blue-500 text-white shadow-lg hover:shadow-xl"
                : "bg-white/20 text-white/60 cursor-not-allowed"
            }`}
          >
            {isAnalyzing ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" />
                Launching Analysis...
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <Play className="w-5 h-5 mr-2" />
                Launch CIA Analysis
              </div>
            )}
          </motion.button>
        </div>
      </motion.div>

      {/* Human Input Required Alerts - Reduced margin */}
      {humanInputAlerts.length > 0 && (
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
            delay: 0.6,
          }}
          className="bg-yellow-500/10 backdrop-blur-lg rounded-2xl border border-yellow-400/30 mb-6"
          style={{ boxShadow: perfectCardShadow }}
        >
          <div className="p-6 mb-6">
            <h2 className="text-xl font-semibold text-yellow-300 mb-4 flex items-center">
              <AlertTriangle className="w-6 h-6 mr-2" />
              Human Input Required
            </h2>
            <div className="space-y-4">
              {humanInputAlerts.map((alert, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-yellow-500/20 rounded-xl border border-yellow-400/30"
                >
                  <div>
                    <h3 className="font-semibold text-yellow-200">
                      {alert.title}
                    </h3>
                    <p className="text-sm text-yellow-300/80">
                      {alert.description}
                    </p>
                  </div>
                  <button className="px-4 py-2 bg-yellow-500 text-yellow-900 rounded-lg font-medium hover:bg-yellow-400 transition-colors">
                    {alert.action}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Phase Results Display - Reduced margin */}
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
          delay: 0.7,
        }}
        className={`${glassCardStyles} mb-6`}
        style={{ boxShadow: perfectCardShadow }}
      >
        <div className="p-6 mb-6">
          <h2 className="text-xl font-semibold text-white mb-6">
            Analysis Results
          </h2>
          <div className="space-y-4">
            {analysisResults.map((result, index) => {
              const Icon = result.icon;
              const isExpanded = expandedResults.includes(result.phase);
              return (
                <motion.div
                  key={result.phase}
                  initial={{
                    opacity: 0,
                    x: -20,
                  }}
                  animate={{
                    opacity: 1,
                    x: 0,
                  }}
                  transition={{
                    duration: 0.5,
                    delay: 0.1 * index,
                  }}
                  className="bg-white/10 rounded-xl border border-white/20 overflow-hidden"
                >
                  <button
                    onClick={() => toggleResultExpansion(result.phase)}
                    className="w-full p-4 text-left hover:bg-white/5 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Icon className="w-6 h-6 text-blue-400 mr-3" />
                        <div>
                          <h3 className="font-semibold text-white">
                            {result.title}
                          </h3>
                          <p className="text-sm text-white/70">
                            {result.summary}
                          </p>
                        </div>
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-white/60" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-white/60" />
                      )}
                    </div>
                  </button>
                  {isExpanded && (
                    <motion.div
                      initial={{
                        height: 0,
                        opacity: 0,
                      }}
                      animate={{
                        height: "auto",
                        opacity: 1,
                      }}
                      exit={{
                        height: 0,
                        opacity: 0,
                      }}
                      transition={{
                        duration: 0.3,
                      }}
                      className="px-4 pb-4"
                    >
                      <div className="pl-9 space-y-2">
                        {result.details.map((detail, idx) => (
                          <p
                            key={idx}
                            className="text-sm text-white/80 flex items-start"
                          >
                            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2 mr-2 flex-shrink-0" />
                            {detail}
                          </p>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* Intelligence Archives - Reduced margin */}
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
          delay: 0.8,
        }}
        className={`${glassCardStyles} mb-6`}
        style={{ boxShadow: perfectCardShadow }}
      >
        <div className="p-6 mb-6">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
            <Archive className="w-6 h-6 mr-2" />
            Intelligence Archives
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-4 bg-white/10 rounded-xl border border-white/20 hover:bg-white/20 transition-colors text-left">
              <Archive className="w-8 h-8 text-blue-400 mb-2" />
              <h3 className="font-semibold text-white mb-1">Master Archive</h3>
              <p className="text-sm text-white/70">
                Access complete analysis history
              </p>
            </button>
            <button className="p-4 bg-white/10 rounded-xl border border-white/20 hover:bg-white/20 transition-colors text-left">
              <Download className="w-8 h-8 text-green-400 mb-2" />
              <h3 className="font-semibold text-white mb-1">
                Export Intelligence
              </h3>
              <p className="text-sm text-white/70">
                Download reports (PDF, CSV)
              </p>
            </button>
            <button className="p-4 bg-white/10 rounded-xl border border-white/20 hover:bg-white/20 transition-colors text-left">
              <Send className="w-8 h-8 text-blue-400 mb-2" />
              <h3 className="font-semibold text-white mb-1">
                Send to Content Engine
              </h3>
              <p className="text-sm text-white/70">
                Transfer insights for content creation
              </p>
            </button>
          </div>
        </div>
      </motion.div>
    </PageLayout>
  );
};

export default CIAPage;
