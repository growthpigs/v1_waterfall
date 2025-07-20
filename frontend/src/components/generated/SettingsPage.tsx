import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Settings,
  User,
  Bell,
  Shield,
  Palette,
  Database,
  Key,
  Globe,
  Mail,
  Smartphone,
} from "lucide-react";
import {
  pageGradients,
  glassCardStyles,
  fireAccentOverlay,
  perfectCardShadow,
} from "../../lib/utils";
import PageLayout from "../shared/PageLayout";
import PageHeader from "../shared/PageHeader";

interface SettingsSectionProps {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
  delay?: number;
}

const SettingsSection: React.FC<SettingsSectionProps> = ({
  title,
  icon: Icon,
  children,
  delay = 0,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      className={glassCardStyles + " p-6"}
      style={{ boxShadow: perfectCardShadow }}
    >
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-3 bg-black/20 backdrop-blur-sm rounded-xl border border-purple-400/20">
          <Icon className="w-6 h-6 text-white/95" />
        </div>
        <h3 className="text-xl font-semibold text-white/95">{title}</h3>
      </div>
      {children}
    </motion.div>
  );
};

const ToggleSwitch: React.FC<{
  enabled: boolean;
  onChange: (enabled: boolean) => void;
}> = ({ enabled, onChange }) => (
  <button
    onClick={() => onChange(!enabled)}
    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
      enabled ? "bg-gray-500/80" : "bg-black/30 border border-gray-400/20"
    }`}
  >
    <span
      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
        enabled ? "translate-x-6" : "translate-x-1"
      }`}
    />
  </button>
);

const SettingsPage: React.FC = () => {
  console.log("Settings loaded successfully");
  console.log("[Settings] rendered successfully");
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(false);
  const [autoPublish, setAutoPublish] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const [twoFactor, setTwoFactor] = useState(false);
  const [dataSharing, setDataSharing] = useState(true);

  const themes = [
    "Purple Fire",
    "Ocean Blue",
    "Forest Green",
    "Sunset Orange",
    "Midnight Black",
  ];
  const languages = ["English", "Spanish", "French", "German", "Portuguese"];
  const timezones = ["EST", "PST", "CST", "GMT", "CET"];

  return (
    <PageLayout pageTitle="Settings" placeholder="Ask about settings...">
      {/* Slate/Gray gradient background with fire accents */}
      <div
        className={`fixed inset-0 bg-gradient-to-br ${pageGradients.settings} -z-10`}
      />
      <div className={`fixed inset-0 ${fireAccentOverlay} -z-10`} />
      {/* Header - Global Standard */}
      <PageHeader
        title="Settings"
        subtitle="Customize your Brand BOS experience and preferences"
      />

      {/* Settings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Profile Settings */}
        <SettingsSection title="Profile Settings" icon={User} delay={0.1}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-white/75 mb-2">
                Display Name
              </label>
              <input
                type="text"
                defaultValue="John Smith"
                className="w-full bg-white/95 rounded-2xl px-4 py-3 border border-slate-200 text-slate-800 placeholder-slate-400 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-400/20 transition-all duration-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-white/75 mb-2">
                Email Address
              </label>
              <input
                type="email"
                defaultValue="john@agency.com"
                className="w-full bg-white/95 rounded-2xl px-4 py-3 border border-slate-200 text-slate-800 placeholder-slate-400 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-400/20 transition-all duration-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-white/75 mb-2">
                Company Name
              </label>
              <input
                type="text"
                defaultValue="Elite Marketing Agency"
                className="w-full bg-white/95 rounded-2xl px-4 py-3 border border-slate-200 text-slate-800 placeholder-slate-400 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-400/20 transition-all duration-300"
              />
            </div>
          </div>
        </SettingsSection>

        {/* Notification Settings */}
        <SettingsSection title="Notifications" icon={Bell} delay={0.2}>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-white/75" />
                <div>
                  <p className="text-white/90 font-medium">
                    Email Notifications
                  </p>
                  <p className="text-sm text-white/60">
                    Receive campaign updates via email
                  </p>
                </div>
              </div>
              <ToggleSwitch
                enabled={emailNotifications}
                onChange={setEmailNotifications}
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Smartphone className="w-5 h-5 text-white/75" />
                <div>
                  <p className="text-white/90 font-medium">
                    Push Notifications
                  </p>
                  <p className="text-sm text-white/60">
                    Get instant alerts on your device
                  </p>
                </div>
              </div>
              <ToggleSwitch
                enabled={pushNotifications}
                onChange={setPushNotifications}
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Globe className="w-5 h-5 text-white/75" />
                <div>
                  <p className="text-white/90 font-medium">
                    Auto-Publish Content
                  </p>
                  <p className="text-sm text-white/60">
                    Automatically publish scheduled content
                  </p>
                </div>
              </div>
              <ToggleSwitch enabled={autoPublish} onChange={setAutoPublish} />
            </div>
          </div>
        </SettingsSection>

        {/* Appearance Settings */}
        <SettingsSection title="Appearance" icon={Palette} delay={0.3}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-white/75 mb-2">
                Theme
              </label>
              <select className="w-full bg-white/95 rounded-2xl px-4 py-3 border border-slate-200 text-slate-800 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-400/20 transition-all duration-300 appearance-none cursor-pointer">
                {themes.map((theme) => (
                  <option
                    key={theme}
                    value={theme}
                    className="bg-white text-slate-800"
                  >
                    {theme}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/90 font-medium">Dark Mode</p>
                <p className="text-sm text-white/60">
                  Use dark theme across the platform
                </p>
              </div>
              <ToggleSwitch enabled={darkMode} onChange={setDarkMode} />
            </div>
            <div>
              <label className="block text-sm font-medium text-white/75 mb-2">
                Language
              </label>
              <select className="w-full bg-white/95 rounded-2xl px-4 py-3 border border-slate-200 text-slate-800 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-400/20 transition-all duration-300 appearance-none cursor-pointer">
                {languages.map((lang) => (
                  <option
                    key={lang}
                    value={lang}
                    className="bg-white text-slate-800"
                  >
                    {lang}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </SettingsSection>

        {/* Security Settings */}
        <SettingsSection title="Security" icon={Shield} delay={0.4}>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Key className="w-5 h-5 text-white/75" />
                <div>
                  <p className="text-white/90 font-medium">
                    Two-Factor Authentication
                  </p>
                  <p className="text-sm text-white/60">
                    Add an extra layer of security
                  </p>
                </div>
              </div>
              <ToggleSwitch enabled={twoFactor} onChange={setTwoFactor} />
            </div>
            <div>
              <button className="w-full bg-black/20 backdrop-blur-sm rounded-xl px-4 py-3 border border-purple-400/20 text-white/90 hover:border-orange-400/30 hover:bg-black/25 transition-all duration-300 text-left">
                Change Password
              </button>
            </div>
            <div>
              <button className="w-full bg-black/20 backdrop-blur-sm rounded-xl px-4 py-3 border border-purple-400/20 text-white/90 hover:border-orange-400/30 hover:bg-black/25 transition-all duration-300 text-left">
                View Login History
              </button>
            </div>
          </div>
        </SettingsSection>

        {/* Data & Privacy */}
        <SettingsSection title="Data & Privacy" icon={Database} delay={0.5}>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/90 font-medium">Data Sharing</p>
                <p className="text-sm text-white/60">
                  Share anonymized data for improvements
                </p>
              </div>
              <ToggleSwitch enabled={dataSharing} onChange={setDataSharing} />
            </div>
            <div>
              <button className="w-full bg-black/20 backdrop-blur-sm rounded-xl px-4 py-3 border border-purple-400/20 text-white/90 hover:border-orange-400/30 hover:bg-black/25 transition-all duration-300 text-left">
                Download My Data
              </button>
            </div>
            <div>
              <button className="w-full bg-black/20 backdrop-blur-sm rounded-xl px-4 py-3 border border-red-400/20 text-red-400 hover:border-red-400/30 hover:bg-red-900/10 transition-all duration-300 text-left">
                Delete My Account
              </button>
            </div>
          </div>
        </SettingsSection>

        {/* Regional Settings */}
        <SettingsSection title="Regional" icon={Globe} delay={0.6}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-white/75 mb-2">
                Timezone
              </label>
              <select className="w-full bg-white/95 rounded-2xl px-4 py-3 border border-slate-200 text-slate-800 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-400/20 transition-all duration-300 appearance-none cursor-pointer">
                {timezones.map((tz) => (
                  <option key={tz} value={tz} className="bg-gray-800">
                    {tz}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-white/75 mb-2">
                Date Format
              </label>
              <select className="w-full bg-white/95 rounded-2xl px-4 py-3 border border-slate-200 text-slate-800 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-400/20 transition-all duration-300 appearance-none cursor-pointer">
                <option className="bg-gray-800">MM/DD/YYYY</option>
                <option className="bg-gray-800">DD/MM/YYYY</option>
                <option className="bg-gray-800">YYYY-MM-DD</option>
              </select>
            </div>
          </div>
        </SettingsSection>
      </div>

      {/* Save Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.7 }}
        className="mt-8 flex justify-center"
      >
        <button className="bg-gray-600/80 hover:bg-gray-600 text-white px-8 py-3 rounded-xl font-semibold hover:shadow-lg transition-all duration-300">
          Save Settings
        </button>
      </motion.div>
    </PageLayout>
  );
};

export default SettingsPage;
