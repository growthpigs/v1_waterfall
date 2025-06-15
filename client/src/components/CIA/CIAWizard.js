import React, { useState, useEffect, useRef } from "react";
import axios from "../../utils/axios";
// Import other dependencies
import {
  AlertCircle,
  Building2,
  Globe,
  FileText,
  Download,
  FileSpreadsheet,
  Database,
  Loader2,
  CheckCircle2
} from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter
} from "../ui/card";
import { cn } from "../../lib/utils";

const CIAWizard = () => {
  // State declarations
  const [formData, setFormData] = useState({
    companyName: "",
    websiteUrl: "",
    keyPersonOfInfluence: "",
    primaryKeyword: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [errors, setErrors] = useState({});
  const [reportId, setReportId] = useState(null);
  const [reportStatus, setReportStatus] = useState("idle");
  const [reportProgress, setReportProgress] = useState(0);
  const [currentPhase, setCurrentPhase] = useState(0);
  const [phaseDetails, setPhaseDetails] = useState([]);
  const [reportResults, setReportResults] = useState(null);
  const [currentPollInterval, setCurrentPollInterval] = useState(5000);
  const [exportLoading, setExportLoading] = useState({
    pdf: false,
    sheets: false,
    notion: false
  });
  const [exportError, setExportError] = useState(null);

  // Constants
  const initialPollInterval = 5000;
  const maxPollInterval = 60000;
  const pollTimeoutRef = useRef(null);

  // Define phases
  const phases = [
    { id: 1, name: "Business Intelligence", description: "Analyzing company data and market position" },
    { id: 2, name: "SEO & Social Intelligence", description: "Researching keywords and competitive landscape" },
    { id: 3, name: "Strategic Synthesis", description: "Combining insights for strategic recommendations" },
    { id: 4, name: "Golden Hippo Offer", description: "Developing tiered pricing and value stacks" },
    { id: 5, name: "Convergence Blender", description: "Creating 12-week content calendar" },
    { id: 6, name: "Master Content Bible", description: "Finalizing implementation roadmap" }
  ];

  // Poll for report status updates - FIXED VERSION WITH PROPER PARENTHESES
  const pollReportStatus = async (id, currentInterval) => {
    try {
      const response = await axios.get(`/cia/reports/${id}/status`);
      const { status, progress, currentPhase: newPhaseNumber, phaseProgress, errors: reportErrors } = response.data;

      setReportStatus(status);
      setReportProgress(progress);

      if (newPhaseNumber) {
        setCurrentPhase(newPhaseNumber);
        updatePhaseDetails(newPhaseNumber, phaseProgress, status);
      }

      if (status === "completed" || status === "failed") {
        if (status === "completed") {
          fetchReportResults(id);
        } else if (status === "failed" && reportErrors && reportErrors.length > 0) {
          setErrors(prevErrors => ({
            ...prevErrors,
            report: reportErrors.map(err => `${err.stage}: ${err.message}`).join(", ")
          }));
        }
        if (pollTimeoutRef.current) {
          clearTimeout(pollTimeoutRef.current);
        }
        return;
      }

      // If still processing, schedule next poll with exponential backoff
      const nextInterval = Math.min(currentInterval * 2, maxPollInterval);
      setCurrentPollInterval(nextInterval);
      pollTimeoutRef.current = setTimeout(() => pollReportStatus(id, nextInterval), nextInterval);

    } catch (error) {
      console.error("Error polling report status:", error);
      let nextInterval = currentInterval;
      
      if (error.response && error.response.status === 429) {
        console.warn("Rate limited. Increasing poll interval significantly.");
        nextInterval = maxPollInterval;
      } else {
        nextInterval = Math.min(currentInterval * 2, maxPollInterval);
      }
      
      setCurrentPollInterval(nextInterval);
      
      if (reportStatus !== "completed" && reportStatus !== "failed") {
        pollTimeoutRef.current = setTimeout(() => pollReportStatus(id, nextInterval), nextInterval);
      }
    }
  };

  // Function to update phaseDetails based on API response
  const updatePhaseDetails = (
    newPhaseNumber,
    phaseProgressFromServer,
    currentStatus
  ) => {
    setPhaseDetails(prevDetails => {
      let newPhaseDetails = [...prevDetails];

      // Initialize array if empty
      if (newPhaseDetails.length === 0) {
        newPhaseDetails = phases.map(p => ({
          id: p.id,
          name: p.name,
          progress: 0,
          status: "pending"
        }));
      }

      // If report is fully completed, mark every phase complete
      if (currentStatus === "completed") {
        return newPhaseDetails.map(phase => ({
          ...phase,
          progress: 100,
          status: "completed"
        }));
      }

      // Mark previous phases as completed
      for (let i = 0; i < newPhaseNumber - 1; i++) {
        if (newPhaseDetails[i]) {
          newPhaseDetails[i] = {
            ...newPhaseDetails[i],
            progress: 100,
            status: "completed"
          };
        }
      }

      // Update the current phase entry
      if (newPhaseNumber > 0 && newPhaseNumber <= phases.length) {
        const currentPhaseIndex = newPhaseNumber - 1;
        newPhaseDetails[currentPhaseIndex] = {
          ...newPhaseDetails[currentPhaseIndex],
          progress: phaseProgressFromServer ?? 0,
          status:
            phaseProgressFromServer >= 100 ? "completed" : "processing"
        };
      }

      // Handle failure status
      if (currentStatus === "failed" && newPhaseNumber > 0) {
        const failingPhaseIndex = newPhaseNumber - 1;
        // Mark active phase as failed if incomplete
        if (
          newPhaseDetails[failingPhaseIndex] &&
          newPhaseDetails[failingPhaseIndex].status !== "completed"
        ) {
          newPhaseDetails[failingPhaseIndex].status = "failed";
        }
        // Reset subsequent phases to pending
        for (let i = newPhaseNumber; i < phases.length; i++) {
          if (newPhaseDetails[i]) {
            newPhaseDetails[i].status = "pending";
            newPhaseDetails[i].progress = 0;
          }
        }
      }

      return newPhaseDetails;
    });
  };

  // Fetch report results
  const fetchReportResults = async id => {
    try {
      const response = await axios.get(`/cia/reports/${id}`);
      setReportResults(response.data);
    } catch (error) {
      console.error("Error fetching report results:", error);
      setErrors(prev => ({
        ...prev,
        results:
          "Failed to fetch report results. Please try refreshing the page."
      }));
    }
  };

  // Check if all phases are complete
  const areAllPhasesComplete = () => {
    if (phaseDetails.length !== phases.length) return false;
    return phaseDetails.every(
      phase => phase.status === "completed" && phase.progress === 100
    );
  };

  /* ------------------------------------------------------------------
   * Form helpers
   * ------------------------------------------------------------------ */

  // Handle input changes
  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => {
        const newErr = { ...prev };
        delete newErr[field];
        return newErr;
      });
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    if (!formData.companyName.trim()) {
      newErrors.companyName = "Company name is required";
    }
    if (!formData.websiteUrl.trim()) {
      newErrors.websiteUrl = "Website URL is required";
    } else {
      // Allow inputs like example.com or www.example.com without requiring http/https
      // Strip protocol and www for validation purposes
      const normalized = formData.websiteUrl
        .replace(/^(https?:\/\/)?/i, "")
        .replace(/^www\./i, "")
        .replace(/\/$/, ""); // Remove trailing slash if present

      // Very basic domain check: something.something (at least one dot and valid chars)
      console.log("Original URL:", formData.websiteUrl);
      console.log("Normalized URL for regex test:", normalized);
      const domainRegex = /^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$/;
      console.log("Regex test result:", domainRegex.test(normalized));
      if (!domainRegex.test(normalized)) {
        newErrors.websiteUrl =
          "Please enter a valid website address (e.g., example.com)";
      }
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Submit form
  const handleSubmit = async e => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);
    setErrors({});
    setPhaseDetails([]);
    setReportProgress(0);
    setCurrentPhase(0);
    setReportResults(null);

    try {
      const response = await axios.post("/cia/reports", {
        name: `${formData.companyName} Intelligence Report`,
        description: `CIA report for ${formData.companyName}`,
        initialData: {
          companyName: formData.companyName,
          websiteUrl: formData.websiteUrl.startsWith("http")
            ? formData.websiteUrl
            : `https://${formData.websiteUrl}`,
          keyPersonOfInfluence: formData.keyPersonOfInfluence
            ? { name: formData.keyPersonOfInfluence, role: "Key Person of Influence" }
            : {},
          primaryKeyword: formData.primaryKeyword
        }
      });
      const { id } = response.data.report;
      setReportId(id);
      setIsSubmitted(true);
      setReportStatus("processing");
    } catch (error) {
      console.error("Error submitting CIA report:", error);
      setErrors({
        submit:
          error.response?.data?.message ||
          "Failed to submit report. Please try again."
      });
      setReportStatus("failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Export report
  const exportReport = async format => {
    setExportLoading(prev => ({ ...prev, [format]: true }));
    setExportError(null);
    try {
      const response = await axios.post(`/cia/reports/${reportId}/export`, {
        format
      });
      if (!response.data?.exportUrl) {
        throw new Error("Missing export URL");
      }
      let fullUrl = response.data.exportUrl;
      if (fullUrl.startsWith("/")) {
        fullUrl = `${window.location.origin}${fullUrl}`;
      }
      if (format === "pdf") {
        const link = document.createElement("a");
        link.href = fullUrl;
        link.download = `${formData.companyName}_CIA_Report.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        window.open(fullUrl, "_blank");
      }
    } catch (error) {
      let msg = `Failed to export as ${format}. `;
      if (error.response) {
        msg += `Server responded ${error.response.status}`;
      } else if (error.request) {
        msg += "No response from server.";
      } else {
        msg += error.message;
      }
      setExportError(msg);
    } finally {
      setExportLoading(prev => ({ ...prev, [format]: false }));
    }
  };

  // Effect to handle polling
  useEffect(() => {
    if (reportId && reportStatus === "processing") {
      if (pollTimeoutRef.current) {
        clearTimeout(pollTimeoutRef.current);
      }
      setCurrentPollInterval(initialPollInterval);
      pollTimeoutRef.current = setTimeout(() => pollReportStatus(reportId, initialPollInterval), initialPollInterval);
    }
    
    return () => {
      if (pollTimeoutRef.current) {
        clearTimeout(pollTimeoutRef.current);
      }
    };
  }, [reportId, reportStatus]);

  // Render form 
  const renderForm = () => (
    <form onSubmit={handleSubmit}>
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="company-name">Company Name *</Label>
          <Input
            id="company-name"
            value={formData.companyName}
            onChange={(e) => handleChange("companyName", e.target.value)}
            placeholder="e.g. Acme Corporation"
            className={errors.companyName ? "border-destructive" : ""}
            disabled={isSubmitting}
          />
          {errors.companyName && (
            <p className="text-sm text-destructive">{errors.companyName}</p>
          )}
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="website-url">Website URL *</Label>
          <Input
            id="website-url"
            value={formData.websiteUrl}
            onChange={(e) => handleChange("websiteUrl", e.target.value)}
            placeholder="e.g. https://www.example.com"
            className={errors.websiteUrl ? "border-destructive" : ""}
            disabled={isSubmitting}
          />
          {errors.websiteUrl && (
            <p className="text-sm text-destructive">{errors.websiteUrl}</p>
          )}
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="kpoi">Key Person of Influence (Optional)</Label>
          <Input
            id="kpoi"
            value={formData.keyPersonOfInfluence}
            onChange={(e) => handleChange("keyPersonOfInfluence", e.target.value)}
            placeholder="e.g. John Smith, CEO"
            disabled={isSubmitting}
          />
          <p className="text-xs text-muted-foreground">The main person associated with your brand</p>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="primary-keyword">Primary Keyword (Optional)</Label>
          <Input
            id="primary-keyword"
            value={formData.primaryKeyword}
            onChange={(e) => handleChange("primaryKeyword", e.target.value)}
            placeholder="e.g. digital marketing services"
            disabled={isSubmitting}
          />
          <p className="text-xs text-muted-foreground">Main keyword you want to rank for</p>
        </div>
        
        {errors.submit && (
          <div className="p-3 bg-destructive/10 border border-destructive rounded-md">
            <p className="text-sm text-destructive flex items-center">
              <AlertCircle className="h-4 w-4 mr-2" />
              {errors.submit}
            </p>
          </div>
        )}
      </div>
      
      <div className="mt-6">
        <Button 
          type="submit" 
          className="w-full" 
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Submitting...
            </>
          ) : (
            <>
              Generate CIA Report
              <FileText className="ml-2 h-4 w-4" />
            </>
          )}
        </Button>
      </div>
    </form>
  );

  // Render progress
  const renderProgress = () => (
    <div className="space-y-6">
      <div className="space-y-2">
        <h3 className="text-lg font-medium">
          {reportStatus === "completed" 
            ? "Your CIA Report is Ready!" 
            : reportStatus === "failed"
            ? "Report Generation Failed"
            : "Generating Your CIA Report..."}
        </h3>
        <p className="text-sm text-muted-foreground">
          {reportStatus === "completed"
            ? "Your comprehensive marketing intelligence report has been generated. You can now export it in various formats."
            : reportStatus === "failed"
            ? "There was an error generating your report. Please check the error details below."
            : "Our AI is analyzing your company data across all 6 phases. This may take a few minutes."}
        </p>
      </div>
      
      {/* Overall progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Overall Progress</span>
          <span>{reportProgress}%</span>
        </div>
        <div className="w-full bg-muted rounded-full h-2.5">
          <div
            className={cn(
              "h-2.5 rounded-full",
              reportStatus === "completed" ? "bg-green-500" : 
              reportStatus === "failed" ? "bg-destructive" : "bg-primary animate-pulse"
            )}
            style={{ width: `${reportProgress}%` }}
          ></div>
        </div>
      </div>
      
      {/* Phase progress */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium">CIA Workflow Phases</h4>
        
        {phases.map((phase, index) => {
          const phaseInfo = phaseDetails[index] || { progress: 0, status: "pending" };
          
          let displayStatus = phaseInfo.status;
          let displayProgress = phaseInfo.progress;

          if (reportStatus === "processing") {
            if (index < currentPhase - 1) {
                displayStatus = "completed";
                displayProgress = 100;
            } else if (index === currentPhase - 1) {
                displayStatus = "processing";
                displayProgress = phaseInfo.progress; // Use actual progress from API
            } else {
                displayStatus = "pending";
                displayProgress = 0;
            }
          } else if (reportStatus === "completed") {
            displayStatus = "completed";
            displayProgress = 100;
          } else if (reportStatus === "failed") {
            if (index < currentPhase - 1) { // Phases before the failing one
                displayStatus = "completed";
                displayProgress = 100;
            } else if (index === currentPhase - 1) { // The phase that might have failed
                displayStatus = phaseInfo.status === "completed" ? "completed" : "failed";
                displayProgress = phaseInfo.progress;
            } else { // Subsequent phases
                displayStatus = "pending";
                displayProgress = 0;
            }
          }
          
          return (
            <div key={phase.id} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="flex items-center">
                  {displayStatus === "completed" ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                  ) : displayStatus === "processing" ? (
                    <Loader2 className="h-4 w-4 text-primary mr-2 animate-spin" />
                  ) : displayStatus === "failed" ? (
                    <AlertCircle className="h-4 w-4 text-destructive mr-2" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border border-muted-foreground mr-2" />
                  )}
                  {phase.name}
                </span>
                <span>{displayProgress}%</span>
              </div>
              <div className="w-full bg-muted rounded-full h-1.5">
                <div
                  className={cn(
                    "h-1.5 rounded-full",
                    displayStatus === "completed" ? "bg-green-500" : 
                    displayStatus === "failed" ? "bg-destructive" : 
                    displayStatus === "processing" ? "bg-primary" : "bg-muted-foreground"
                  )}
                  style={{ width: `${displayProgress}%` }}
                ></div>
              </div>
              <p className="text-xs text-muted-foreground">{phase.description}</p>
            </div>
          );
        })}
      </div>
      
      {/* Error message (visible when failed) */}
      {reportStatus === "failed" && (
        <div className="p-4 bg-destructive/10 border border-destructive rounded-md">
          <div className="flex items-start space-x-2">
            <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
            <div>
              <h5 className="font-medium text-destructive">Report Generation Failed</h5>
              <p className="text-sm text-muted-foreground mt-1">
                {errors.report || errors.submit || "An unexpected error occurred. Please try again or contact support."}
              </p>
              <Button 
                variant="outline" 
                className="mt-4" 
                onClick={() => {
                  setIsSubmitted(false);
                  setReportStatus("idle");
                  setReportProgress(0);
                  setCurrentPhase(0);
                  setPhaseDetails([]);
                  setReportResults(null);
                  setErrors({});
                  setReportId(null);
                  setFormData({
                    companyName: "",
                    websiteUrl: "",
                    keyPersonOfInfluence: "",
                    primaryKeyword: "",
                    industry: "",
                    targetAudience: "",
                    businessGoals: "",
                    contentGoals: "",
                    brandVoice: ""
                  });
                }}
              >
                Try Again
              </Button>
            </div>
          </div>
        </div>
      )}
      
      {/* Export options (visible when completed AND all phases are at 100%) */}
      {reportStatus === "completed" && reportProgress === 100 && areAllPhasesComplete() && (
        <div className="space-y-4 pt-4 border-t">
          <h4 className="text-sm font-medium">Export Options</h4>
          
          <div className="flex flex-col sm:flex-row gap-3">
            <Button 
              variant="outline" 
              onClick={() => exportReport("pdf")}
              disabled={exportLoading.pdf}
              className="flex-1"
            >
              {exportLoading.pdf ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Download className="mr-2 h-4 w-4" />
              )}
              Export as PDF
            </Button>
            
            <Button 
              variant="outline" 
              onClick={() => exportReport("google_sheets")}
              disabled={exportLoading.sheets}
              className="flex-1"
            >
              {exportLoading.sheets ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <FileSpreadsheet className="mr-2 h-4 w-4" />
              )}
              Export to Google Sheets
            </Button>
            
            <Button 
              variant="outline" 
              onClick={() => exportReport("notion")}
              disabled={exportLoading.notion}
              className="flex-1"
            >
              {exportLoading.notion ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Database className="mr-2 h-4 w-4" />
              )}
              Export to Notion
            </Button>
          </div>
          
          {exportError && (
            <div className="p-3 bg-destructive/10 border border-destructive rounded-md">
              <p className="text-sm text-destructive flex items-center">
                <AlertCircle className="h-4 w-4 mr-2" />
                {exportError}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );

  // Main component render
  return (
    <div className="container mx-auto py-8 px-4 md:px-6">
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center">
            <span className="gradient-text">CIA Wizard</span>
          </CardTitle>
          <CardDescription>
            The Colossal Intelligence Arsenal will gather and process data to create your "Master Content Bible"
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          {isSubmitted || reportStatus === "processing" || reportStatus === "completed" || reportStatus === "failed" ? renderProgress() : renderForm()}
        </CardContent>
        
        <CardFooter className="flex justify-between">
          <div className="text-xs text-muted-foreground">
            <div className="flex items-center">
              <Building2 className="h-3 w-3 mr-1" />
              <span>{formData.companyName || "Your Company"}</span>
            </div>
            {formData.websiteUrl && (
              <div className="flex items-center mt-1">
                <Globe className="h-3 w-3 mr-1" />
                <span>{formData.websiteUrl}</span>
              </div>
            )}
          </div>
          {(reportStatus === "completed" || reportStatus === "failed") && !isSubmitting && (
            <Button 
              variant="outline" 
              onClick={() => {
                setIsSubmitted(false);
                setReportStatus("idle");
                setReportProgress(0);
                setCurrentPhase(0);
                setPhaseDetails([]);
                setReportResults(null);
                setErrors({});
                setReportId(null);
                setFormData({
                  companyName: "",
                  websiteUrl: "",
                  keyPersonOfInfluence: "",
                  primaryKeyword: "",
                  industry: "",
                  targetAudience: "",
                  businessGoals: "",
                  contentGoals: "",
                  brandVoice: ""
                });
              }}
            >
              Start New Report
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
};

export default CIAWizard;
