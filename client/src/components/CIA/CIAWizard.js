import React, { useState, useEffect } from "react";
import axios from "../../utils/axios";
import { 
  CheckCircle2, 
  AlertCircle, 
  Building2, 
  Globe,
  FileText,
  Download,
  FileSpreadsheet,
  Database,
  Loader2
} from "lucide-react";

// Import shadcn/ui components
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../ui/card";

// Utility functions
import { cn } from "../../lib/utils";

/**
 * CIA Wizard - Simplified form for gathering company intelligence data
 * Collects minimal information needed to generate a comprehensive marketing intelligence report
 */
const CIAWizard = () => {
  // Form state
  const [formData, setFormData] = useState({
    companyName: "",
    websiteUrl: "",
    keyPersonOfInfluence: "",
    primaryKeyword: ""
  });
  
  // Submission state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [errors, setErrors] = useState({});
  
  // Report state
  const [reportId, setReportId] = useState(null);
  const [reportStatus, setReportStatus] = useState("idle"); // idle, processing, completed, failed
  const [reportProgress, setReportProgress] = useState(0);
  const [currentPhase, setCurrentPhase] = useState(0);
  const [phaseDetails, setPhaseDetails] = useState([]);
  const [reportResults, setReportResults] = useState(null);
  const [exportLoading, setExportLoading] = useState({
    pdf: false,
    sheets: false,
    notion: false
  });
  const [exportError, setExportError] = useState(null);

  // CIA workflow phases
  const phases = [
    { id: 1, name: "Business Intelligence", description: "Analyzing company data and market position" },
    { id: 2, name: "SEO & Social Intelligence", description: "Researching keywords and competitive landscape" },
    { id: 3, name: "Strategic Synthesis", description: "Combining insights for strategic recommendations" },
    { id: 4, name: "Golden Hippo Offer", description: "Developing tiered pricing and value stacks" },
    { id: 5, name: "Convergence Blender", description: "Creating 12-week content calendar" },
    { id: 6, name: "Master Content Bible", description: "Finalizing implementation roadmap" }
  ];

  // Handle input changes
  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when field is updated
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
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
    } else if (!/^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z0-9-]+(\/[a-zA-Z0-9-._~:/?#[\]@!$&'()*+,;=]*)?$/.test(formData.websiteUrl)) {
      newErrors.websiteUrl = "Please enter a valid URL";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Submit form
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Create a new CIA report
      const response = await axios.post("/cia/reports", {
        name: `${formData.companyName} Intelligence Report`,
        description: `CIA report for ${formData.companyName}`,
        initialData: {
          companyName: formData.companyName,
          websiteUrl: formData.websiteUrl,
          keyPersonOfInfluence: formData.keyPersonOfInfluence ? {
            name: formData.keyPersonOfInfluence,
            role: "Key Person of Influence"
          } : {},
          primaryKeyword: formData.primaryKeyword
        }
      });
      
      // Get the report ID
      const { id } = response.data.report;
      setReportId(id);
      setIsSubmitted(true);
      setReportStatus("processing");
      
      // Begin polling for status updates
      startStatusPolling(id);
    } catch (error) {
      console.error("Error submitting CIA report:", error);
      setErrors({
        submit: error.response?.data?.message || "Failed to submit report. Please try again."
      });
      setIsSubmitting(false);
    }
  };

  // Poll for report status updates
  const startStatusPolling = (id) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`/cia/reports/${id}/status`);
        const { status, progress, currentPhase, phaseProgress } = response.data;
        
        setReportStatus(status);
        setReportProgress(progress);
        
        if (currentPhase) {
          setCurrentPhase(currentPhase);
          
          // Update phase details
          setPhaseDetails(prev => {
            const updatedPhases = [...prev];
            const phaseIndex = currentPhase - 1;
            
            if (!updatedPhases[phaseIndex]) {
              updatedPhases[phaseIndex] = {
                id: currentPhase,
                progress: phaseProgress || 0,
                status: "processing"
              };
            } else {
              updatedPhases[phaseIndex] = {
                ...updatedPhases[phaseIndex],
                // keep the max between existing and new progress
                progress: Math.max(
                  updatedPhases[phaseIndex].progress || 0,
                  phaseProgress || 0
                ),
                status:
                  (phaseProgress ?? updatedPhases[phaseIndex].progress) >= 100
                    ? "completed"
                    : "processing"
              };
            }

            // -----------------------------------------------------------------
            // Ensure *all previous* phases are marked as completed (100 %)
            // so their bars don’t remain stuck at 0 %.
            // -----------------------------------------------------------------
            for (let i = 0; i < phaseIndex; i++) {
              if (!updatedPhases[i]) {
                updatedPhases[i] = {
                  id: i + 1,
                  progress: 100,
                  status: "completed"
                };
              } else {
                updatedPhases[i] = {
                  ...updatedPhases[i],
                  progress: 100,
                  status: "completed"
                };
              }
            }
            
            return updatedPhases;
          });
        }
        
        // If completed or failed, stop polling and fetch results
        if (status === "completed" || status === "failed") {
          clearInterval(pollInterval);
          
          if (status === "completed") {
            fetchReportResults(id);
          }
        }
      } catch (error) {
        console.error("Error polling report status:", error);
        // Don't stop polling on error, just log it
      }
    }, 3000); // Poll every 3 seconds
    
    // Clean up interval on component unmount
    return () => clearInterval(pollInterval);
  };

  // Fetch report results
  const fetchReportResults = async (id) => {
    try {
      const response = await axios.get(`/cia/reports/${id}`);
      setReportResults(response.data);
    } catch (error) {
      console.error("Error fetching report results:", error);
      setErrors({
        results: "Failed to fetch report results. Please try refreshing the page."
      });
    }
  };

  // Export report
  const exportReport = async (format) => {
    setExportLoading(prev => ({ ...prev, [format]: true }));
    setExportError(null);
    
    try {
      const response = await axios.post(`/cia/reports/${reportId}/export`, {
        format
      });
      
      // Handle different export formats
      if (format === "pdf") {
        // For PDF, create a download link
        const link = document.createElement("a");
        link.href = response.data.exportUrl;
        link.download = `${formData.companyName}_CIA_Report.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        // For other formats, open in new tab
        window.open(response.data.exportUrl, "_blank");
      }
    } catch (error) {
      console.error(`Error exporting report as ${format}:`, error);
      setExportError(`Failed to export as ${format}. ${error.response?.data?.message || "Please try again."}`);
    } finally {
      setExportLoading(prev => ({ ...prev, [format]: false }));
    }
  };

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
            ? "There was an error generating your report. Please try again or contact support."
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
              reportStatus === "completed" ? "bg-success" : "bg-primary"
            )}
            style={{ width: `${reportProgress}%` }}
          ></div>
        </div>
      </div>
      
      {/* Phase progress */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium">CIA Workflow Phases</h4>
        
        {phases.map((phase, index) => {
          const phaseDetail = phaseDetails[index] || { progress: 0, status: index === currentPhase - 1 ? "processing" : "pending" };
          
          return (
            <div key={phase.id} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="flex items-center">
                  {phaseDetail.status === "completed" ? (
                    <CheckCircle2 className="h-4 w-4 text-success mr-2" />
                  ) : phaseDetail.status === "processing" ? (
                    <Loader2 className="h-4 w-4 text-primary mr-2 animate-spin" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border border-muted-foreground mr-2" />
                  )}
                  {phase.name}
                </span>
                <span>{phaseDetail.progress}%</span>
              </div>
              <div className="w-full bg-muted rounded-full h-1.5">
                <div
                  className={cn(
                    "h-1.5 rounded-full",
                    phaseDetail.status === "completed" ? "bg-success" : "bg-primary"
                  )}
                  style={{ width: `${phaseDetail.progress}%` }}
                ></div>
              </div>
              <p className="text-xs text-muted-foreground">{phase.description}</p>
            </div>
          );
        })}
      </div>
      
      {/* Export options (visible when completed) */}
      {reportStatus === "completed" && (
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
      
      {/* Results preview (visible when completed) */}
      {reportStatus === "completed" && reportResults && (
        <div className="space-y-4 pt-4 border-t">
          <h4 className="text-sm font-medium">Report Preview</h4>
          
          {/* This would be expanded with actual report data visualization */}
          <div className="border rounded-md p-4 bg-muted/50">
            <h5 className="font-medium">{reportResults.name}</h5>
            <p className="text-sm text-muted-foreground mt-1">{reportResults.description}</p>
            
            {/* Example of displaying some report data */}
            {reportResults.phases && reportResults.phases.map((phase) => (
              <div key={phase.id} className="mt-4">
                <h6 className="text-sm font-medium">{phase.name}</h6>
                <p className="text-xs text-muted-foreground">{phase.summary}</p>
              </div>
            ))}
            
            <p className="text-sm mt-4">
              For the complete report with all insights and recommendations, please use one of the export options above.
            </p>
          </div>
        </div>
      )}
      
      {/* Error message (visible when failed) */}
      {reportStatus === "failed" && (
        <div className="p-4 bg-destructive/10 border border-destructive rounded-md">
          <div className="flex items-start space-x-2">
            <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
            <div>
              <h5 className="font-medium text-destructive">Report Generation Failed</h5>
              <p className="text-sm text-muted-foreground mt-1">
                There was an error generating your CIA report. Please try again or contact support for assistance.
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
                }}
              >
                Try Again
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

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
          {isSubmitted ? renderProgress() : renderForm()}
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
        </CardFooter>
      </Card>
    </div>
  );
};

export default CIAWizard;
