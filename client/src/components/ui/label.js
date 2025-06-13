import * as React from "react";
import * as LabelPrimitive from "@radix-ui/react-label";
import { clsx } from "clsx";

/**
 * Label component based on Radix UI's Label primitive
 * @param {Object} props - Component props
 * @param {string} [props.className] - Additional CSS classes
 */
const Label = React.forwardRef(({ className, ...props }, ref) => (
  <LabelPrimitive.Root
    ref={ref}
    className={clsx(
      "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
      className
    )}
    {...props}
  />
));

Label.displayName = "Label";

export { Label };
