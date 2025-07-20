import React from "react";
import { motion } from "framer-motion";

interface PageHeaderProps {
  title: string;
  subtitle: string;
}

const PageHeader: React.FC<PageHeaderProps> = ({ title, subtitle }) => {
  return (
    <div className="mb-6 -mt-4">
      <motion.h1
        initial={{
          opacity: 0,
          x: -20,
        }}
        animate={{
          opacity: 1,
          x: 0,
        }}
        transition={{
          duration: 0.7,
          delay: 0.2,
        }}
        className="text-3xl font-bold text-white mb-2 drop-shadow-lg leading-tight pl-4"
      >
        {title}
      </motion.h1>
      <motion.p
        initial={{
          opacity: 0,
          x: -20,
        }}
        animate={{
          opacity: 1,
          x: 0,
        }}
        transition={{
          duration: 0.7,
          delay: 0.3,
        }}
        className="text-base text-white/90 drop-shadow-sm font-light pl-4"
      >
        {subtitle}
      </motion.p>
    </div>
  );
};

export default PageHeader;
