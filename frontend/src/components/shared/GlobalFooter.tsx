import React from "react";

const GlobalFooter: React.FC = () => {
  return (
    <footer className="mt-16 pt-4 pb-3 border-t border-white/10">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <div className="space-y-1">
          <p className="text-white/70 text-sm font-medium">
            Waterfall Brand BOS, copyright 2025
          </p>
          <p className="text-white/70 text-xs">
            Badaboost | Paris, France | roderic@badaboost.com
          </p>
        </div>
      </div>
    </footer>
  );
};

export default GlobalFooter;
