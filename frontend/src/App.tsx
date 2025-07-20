import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";
import BrandBOSDashboard from "./components/generated/BrandBOSDashboard";
import CIAPage from "./components/generated/CIAPage";
import CampaignCenterPage from "./components/generated/CampaignCenterPage";
import PerformancePage from "./components/generated/PerformancePage";
import SettingsPage from "./components/generated/SettingsPage";
import ContentCalendarPage from "./components/generated/ContentCalendarPage";
import ContentEnginePage from "./components/generated/ContentEnginePage";
import ErrorBoundary from "./components/generated/ErrorBoundary";
import NotFound from "./components/generated/NotFound";
import TickerTape from "./components/generated/TickerTape";
import { useEffect } from "react";

function RouteLogger() {
  const location = useLocation();

  useEffect(() => {
    console.log("Route loaded: " + location.pathname);
    console.log("Route: " + location.pathname);
  }, [location]);

  return null;
}

function App() {
  useEffect(() => {
    console.log("Page loaded: " + window.location.pathname);

    // Add scroll test logging
    const handleScroll = () => {
      console.log("Scrolling test: window.scrollY", window.scrollY);
    };

    window.addEventListener("scroll", handleScroll);

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  return (
    <Router>
      <ErrorBoundary>
        <RouteLogger />
        <Routes>
          <Route path="/" element={<BrandBOSDashboard />} />
          <Route path="/cia" element={<CIAPage />} />
          <Route path="/campaign" element={<CampaignCenterPage />} />
          <Route path="/performance" element={<PerformancePage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/content-calendar" element={<ContentCalendarPage />} />
          <Route path="/content-engine" element={<ContentEnginePage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
        {/* Ticker runs independently at app level */}
        <TickerTape />
      </ErrorBoundary>
    </Router>
  );
}

export default App;
