import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Home,
  Target,
  Calendar,
  Zap,
  BarChart3,
  Settings,
  Search,
  Bell,
  User,
  Brain,
  Menu,
  X,
  TrendingUp,
} from "lucide-react";

const TopNavigation: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const notificationsRef = useRef<HTMLDivElement>(null);

  // Close notifications when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        notificationsRef.current &&
        !notificationsRef.current.contains(event.target as Node)
      ) {
        setShowNotifications(false);
      }
    };

    if (showNotifications) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showNotifications]);

  const navItems = [
    {
      icon: Home,
      label: "Dashboard",
      path: "/",
      active: location.pathname === "/",
    },
    {
      icon: Brain,
      label: "CIA",
      path: "/cia",
      active: location.pathname === "/cia",
    },
    {
      icon: Target,
      label: "Campaign",
      path: "/campaign",
      active: location.pathname === "/campaign",
    },
    {
      icon: Zap,
      label: "Content Engine",
      path: "/content-engine",
      active: location.pathname === "/content-engine",
    },
    {
      icon: Calendar,
      label: "Content Calendar",
      path: "/content-calendar",
      active: location.pathname === "/content-calendar",
    },
    {
      icon: BarChart3,
      label: "Performance",
      path: "/performance",
      active: location.pathname === "/performance",
    },
    {
      icon: Settings,
      label: "Settings",
      path: "/settings",
      active: location.pathname === "/settings",
    },
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-xl border-b border-purple-500/30"
    >
      <div className="max-w-7xl mx-auto px-4 lg:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo/Brand - Remove icon, move text left */}
          <div className="flex items-center">
            <span className="text-white/95 font-semibold text-lg">
              Brand BOS
            </span>
          </div>

          {/* Navigation Items - Increased spacing */}
          <div className="hidden md:flex items-center space-x-2">
            {navItems.map((item, index) => (
              <motion.button
                key={index}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleNavigation(item.path)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2 ${
                  item.active
                    ? "bg-white/20 text-white border border-white/30"
                    : "text-white/70 hover:text-white hover:bg-white/10"
                }`}
              >
                <item.icon className="w-4 h-4" />
                <span>{item.label}</span>
              </motion.button>
            ))}
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-3">
            {/* Notifications */}
            <div className="relative" ref={notificationsRef}>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-all duration-200 relative"
              >
                <Bell className="w-5 h-5" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-orange-500 rounded-full border-2 border-black/20" />
              </motion.button>

              {/* Notifications Dropdown */}
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute right-0 top-full mt-2 w-80 bg-white/90 backdrop-blur-xl rounded-2xl border border-white/20 shadow-2xl z-50"
                >
                  <div className="p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-gray-800 font-semibold">
                        Notifications
                      </h3>
                      <button
                        onClick={() => setShowNotifications(false)}
                        className="text-gray-600 hover:text-gray-800 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {[
                        {
                          id: 1,
                          title: "CIA Analysis Complete",
                          message: "New intelligence report ready for review",
                          time: "2 min ago",
                          type: "success",
                          icon: Brain,
                        },
                        {
                          id: 2,
                          title: "Content Scheduled",
                          message: "5 posts scheduled for this week",
                          time: "15 min ago",
                          type: "info",
                          icon: Calendar,
                        },
                        {
                          id: 3,
                          title: "Performance Alert",
                          message: "Engagement up 24% this week",
                          time: "1 hour ago",
                          type: "success",
                          icon: TrendingUp,
                        },
                        {
                          id: 4,
                          title: "Campaign Status",
                          message: "Q4 Authority Building at 68% progress",
                          time: "3 hours ago",
                          type: "info",
                          icon: Target,
                        },
                      ].map((notification) => (
                        <div
                          key={notification.id}
                          className="p-3 bg-gray-100/50 rounded-lg border border-gray-200/30 hover:bg-gray-200/50 transition-colors cursor-pointer"
                        >
                          <div className="flex items-start space-x-3">
                            <div
                              className={`p-2 rounded-lg ${
                                notification.type === "success"
                                  ? "bg-green-500/20 text-green-600"
                                  : "bg-blue-500/20 text-blue-600"
                              }`}
                            >
                              <notification.icon className="w-4 h-4" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="text-gray-800 font-medium text-sm">
                                {notification.title}
                              </div>
                              <div className="text-gray-600 text-xs mt-1">
                                {notification.message}
                              </div>
                              <div className="text-gray-500 text-xs mt-1">
                                {notification.time}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </div>

            {/* User Profile */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate("/settings")}
              className="p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-all duration-200"
            >
              <User className="w-5 h-5" />
            </motion.button>

            {/* Mobile Menu Button - Far Right */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-all duration-200"
            >
              <Menu className="w-6 h-6" />
            </motion.button>
          </div>
        </div>

        {/* Mobile Menu Full Screen Overlay */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, x: "100%" }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: "100%" }}
              transition={{ type: "tween", duration: 0.3 }}
              className="md:hidden fixed inset-0 bg-white z-50"
            >
              {/* Close Button */}
              <div className="flex justify-end p-6">
                <motion.button
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="p-2 rounded-lg text-white/70 hover:bg-white/10 transition-all duration-200"
                >
                  <X className="w-6 h-6" />
                </motion.button>
              </div>

              {/* Menu Items */}
              <div className="px-6 py-4 space-y-4">
                {navItems.map((item, index) => (
                  <motion.button
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => {
                      handleNavigation(item.path);
                      setIsMobileMenuOpen(false);
                    }}
                    className={`w-full px-6 py-4 rounded-lg font-semibold transition-all duration-200 flex items-center space-x-3 ${
                      item.active
                        ? "bg-white/20 text-white border-l-4 border-white/60"
                        : "text-white/80 hover:bg-white/10"
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="text-lg">{item.label}</span>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.nav>
  );
};

export default TopNavigation;
