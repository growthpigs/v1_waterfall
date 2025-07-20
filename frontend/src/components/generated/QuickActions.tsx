import React from "react";
import { motion } from "framer-motion";
import {
  TrendingUp,
  Search,
  Activity,
  FileText,
  Zap,
  Share2,
} from "lucide-react";
import { perfectCardShadow } from "../../lib/utils";

interface QuickAction {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  color: string;
  bgColor: string;
  borderColor: string;
  hoverBorderColor: string;
  hoverShadowColor: string;
}

const QuickActions: React.FC = () => {
  const actions: QuickAction[] = [
    {
      icon: TrendingUp,
      label: "Viral Opps",
      color: "text-pink-600",
      bgColor: "bg-pink-600/10",
      borderColor: "border-pink-600/30",
      hoverBorderColor: "hover:border-pink-500/50",
      hoverShadowColor: "",
    },
    {
      icon: Search,
      label: "Trend Opps",
      color: "text-indigo-600",
      bgColor: "bg-indigo-600/10",
      borderColor: "border-indigo-600/30",
      hoverBorderColor: "hover:border-indigo-500/50",
      hoverShadowColor: "",
    },
    {
      icon: Activity,
      label: "Live Monitor",
      color: "text-green-600",
      bgColor: "bg-green-600/10",
      borderColor: "border-green-600/30",
      hoverBorderColor: "hover:border-green-500/50",
      hoverShadowColor: "",
    },
    {
      icon: FileText,
      label: "Make Content",
      color: "text-amber-600",
      bgColor: "bg-amber-600/10",
      borderColor: "border-amber-600/30",
      hoverBorderColor: "hover:border-amber-500/50",
      hoverShadowColor: "",
    },
    {
      icon: Zap,
      label: "Quick Campaign",
      color: "text-indigo-400",
      bgColor: "bg-indigo-600/10",
      borderColor: "border-indigo-600/30",
      hoverBorderColor: "hover:border-indigo-500/50",
      hoverShadowColor: "",
    },
    {
      icon: Share2,
      label: "Social Media",
      color: "text-orange-600",
      bgColor: "bg-orange-600/10",
      borderColor: "border-orange-600/30",
      hoverBorderColor: "hover:border-orange-500/50",
      hoverShadowColor: "",
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.4 }}
      whileHover={{
        y: -2,
        transition: { duration: 0.2 },
      }}
      className="bg-black/15 backdrop-blur-lg rounded-2xl p-4 lg:p-6 border border-purple-500/30 hover:bg-black/20 hover:border-orange-500/40 transition-all duration-300 group"
      style={{ boxShadow: perfectCardShadow }}
    >
      <div className="flex items-start justify-between mb-4 lg:mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 lg:p-3 bg-black/20 backdrop-blur-sm rounded-xl border border-purple-400/20 group-hover:border-orange-400/30 group-hover:shadow-lg group-hover:shadow-purple-400/10 transition-all duration-300">
            <Zap className="w-5 h-5 lg:w-6 lg:h-6 text-white/95" />
          </div>
          <h3 className="text-lg lg:text-xl font-semibold text-white/95">
            Quick Actions
          </h3>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 lg:gap-4">
        {actions.map((action, index) => (
          <motion.button
            key={index}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={`${action.bgColor} backdrop-blur-sm rounded-xl p-4 lg:p-5 border ${action.borderColor} ${action.hoverBorderColor} hover:bg-black/25 ${action.hoverShadowColor} transition-all duration-300 flex flex-col items-center space-y-2`}
          >
            <action.icon className={`w-6 h-6 lg:w-8 lg:h-8 ${action.color}`} />
            <span className="text-xs lg:text-sm font-medium text-white/90">
              {action.label}
            </span>
          </motion.button>
        ))}
      </div>

      <div className="mt-4 lg:mt-6 pt-4 border-t border-purple-400/20">
        <div className="flex items-center justify-between text-sm">
          <span className="text-white/75">Quick access to key features</span>
          <span className="text-white/90">Ready</span>
        </div>
      </div>
    </motion.div>
  );
};

export default QuickActions;
