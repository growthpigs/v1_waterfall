import React, { ReactNode } from "react";
import TopNavigation from "../generated/SidebarNavigation";
import FloatingChatBar from "../generated/FloatingChatBar";
import GlobalFooter from "./GlobalFooter";

type PageLayoutProps = {
  children: ReactNode;
  pageTitle: string; // For accessibility or meta
  placeholder: string; // For chat bar
};

const PageLayout: React.FC<PageLayoutProps> = ({
  children,
  pageTitle,
  placeholder,
}) => {
  console.log(`🔍 PageLayout rendering for: ${pageTitle}`);

  const handleSendMessage = (message: string) => {
    console.log(`Message from ${pageTitle}:`, message);
  };

  return (
    <div className="min-h-screen w-full relative">
      {/* Theme-independent layout - each page sets its own gradient background */}
      <div className="min-h-screen w-full flex flex-col relative z-10">
        {/* Fixed Top Nav */}
        <TopNavigation />

        {/* Scrollable Main Content with Padding */}
        <main
          className="flex-1 overflow-y-auto"
          style={{
            paddingTop: "80px", // Nav height + space (adjust if nav changes)
            paddingBottom: "180px", // Bottom elements height + 100px below content
            scrollBehavior: "smooth",
            WebkitOverflowScrolling: "touch",
          }}
        >
          <div className="max-w-7xl mx-auto px-4 py-8">
            {children}
            <GlobalFooter />
          </div>
        </main>

        {/* Fixed Bottom Elements */}
        <div className="fixed bottom-12 left-0 right-0 z-50 px-4 lg:px-6">
          <FloatingChatBar
            onSendMessage={handleSendMessage}
            placeholder={placeholder}
          />
        </div>
      </div>
    </div>
  );
};

export default PageLayout;
