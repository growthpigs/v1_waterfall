import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  ChevronRight, 
  ChevronLeft, 
  CheckCircle2, 
  AlertCircle, 
  Building2, 
  Globe, 
  Search, 
  Target, 
  Users, 
  FileText, 
  CreditCard
} from "lucide-react";

// Import shadcn/ui components
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../ui/card";

// Utility functions
import { cn, formatCurrency } from "../../lib/utils";

/**
 * CIA Wizard - Multi-step form for gathering company intelligence data
 * Collects information needed to generate a comprehensive marketing intelligence report
 */
const CIAWizard = () => {
  const navigate = useNavigate();
  
  // Form steps configuration
  const steps = [
    {
      id: "company",
      title: "Company Information",
      description: "Tell us about your business",
      icon: <Building2 className="h-5 w-5" />,
    },
    {
      id: "website",
      title: "Website Analysis",
      description: "Analyze your web presence",
      icon: <Globe className="h-5 w-5" />,
    },
    {
      id: "keywords",
      title: "Keyword Research",
      description: "Identify target keywords",
      icon: <Search className="h-5 w-5" />,
    },
    {
      id: "competitors",
      title: "Competitor Analysis",
      description: "Identify and analyze competitors",
      icon: <Target className="h-5 w-5" />,
    },
    {
      id: "audience",
      title: "Target Audience",
      description: "Define your ideal customers",
      icon: <Users className="h-5 w-5" />,
    },
    {
      id: "goals",
      title: "Content Goals",
      description: "Set your marketing objectives",
      icon: <FileText className="h-5 w-5" />,
    },
    {
      id: "review",
      title: "Review & Submit",
      description: "Confirm your information",
      icon: <CheckCircle2 className="h-5 w-5" />,
    },
  ];

  // State management
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    company: {
      name: "",
      industry: "",
      size: "",
      description: "",
      founded: "",
      location: "",
    },
    website: {
      url: "",
      analyzeCompetitors: true,
      includeSocialMedia: true,
    },
    keywords: {
      primary: "",
      secondary: "",
      additional: "",
    },
    competitors: {
      main: ["", "", ""],
      includeDetection: true,
    },
    audience: {
      demographics: "",
      painPoints: "",
      goals: "",
    },
    goals: {
      primary: "",
      kpis: "",
      timeline: "3 months",
    },
  });
  
  // Validation state
  const [errors, setErrors] = useState({});
  
  // Credits cost calculation (would be dynamic based on admin settings in real implementation)
  const [creditCost, setCreditCost] = useState({
    base: 50,
    competitors: 10,
    socialMedia: 15,
    autoDetection: 5,
    total: 80,
  });

  // Update total credit cost when options change
  useEffect(() => {
    let total = creditCost.base;
    
    if (formData.website.analyzeCompetitors) {
      total += creditCost.competitors;
    }
    
    if (formData.website.includeSocialMedia) {
      total += creditCost.socialMedia;
    }
    
    if (formData.competitors.includeDetection) {
      total += creditCost.autoDetection;
    }
    
    setCreditCost(prev => ({
      ...prev,
      total
    }));
  }, [formData.website.analyzeCompetitors, formData.website.includeSocialMedia, formData.competitors.includeDetection]);

  // Handle input changes
  const handleChange = (step, field, value) => {
    setFormData(prev => ({
      ...prev,
      [step]: {
        ...prev[step],
        [field]: value
      }
    }));
    
    // Clear error when field is updated
    if (errors[`${step}.${field}`]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[`${step}.${field}`];
        return newErrors;
      });
    }
  };

  // Handle checkbox changes
  const handleCheckboxChange = (step, field) => {
    setFormData(prev => ({
      ...prev,
      [step]: {
        ...prev[step],
        [field]: !prev[step][field]
      }
    }));
  };

  // Handle competitor input changes
  const handleCompetitorChange = (index, value) => {
    const updatedCompetitors = [...formData.competitors.main];
    updatedCompetitors[index] = value;
    
    setFormData(prev => ({
      ...prev,
      competitors: {
        ...prev.competitors,
        main: updatedCompetitors
      }
    }));
    
    // Clear error when field is updated
    if (errors[`competitors.main.${index}`]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[`competitors.main.${index}`];
        return newErrors;
      });
    }
  };

  // Validate current step
  const validateStep = () => {
    const currentStepId = steps[currentStep].id;
    const newErrors = {};
    
    switch (currentStepId) {
      case "company":
        if (!formData.company.name.trim()) {
          newErrors["company.name"] = "Company name is required";
        }
        if (!formData.company.industry.trim()) {
          newErrors["company.industry"] = "Industry is required";
        }
        break;
        
      case "website":
        if (!formData.website.url.trim()) {
          newErrors["website.url"] = "Website URL is required";
        } else if (!/^(https?:\/\/)?([\w-]+\.)+[\w-]+(\/[\w-./?%&=]*)?$/.test(formData.website.url)) {
          newErrors["website.url"] = "Please enter a valid URL";
        }
        break;
        
      case "keywords":
        if (!formData.keywords.primary.trim()) {
          newErrors["keywords.primary"] = "Primary keyword is required";
        }
        break;
        
      case "competitors":
        if (!formData.competitors.main[0].trim()) {
          newErrors["competitors.main.0"] = "At least one competitor is required";
        }
        break;
        
      case "audience":
        if (!formData.audience.demographics.trim()) {
          newErrors["audience.demographics"] = "Target demographics is required";
        }
        break;
        
      case "goals":
        if (!formData.goals.primary.trim()) {
          newErrors["goals.primary"] = "Primary goal is required";
        }
        break;
        
      default:
        break;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Navigate to next step
  const handleNext = () => {
    if (validateStep()) {
      if (currentStep < steps.length - 1) {
        setCurrentStep(currentStep + 1);
        window.scrollTo(0, 0);
      }
    }
  };

  // Navigate to previous step
  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      window.scrollTo(0, 0);
    }
  };

  // Submit form
  const handleSubmit = async () => {
    if (validateStep()) {
      try {
        // Here would be the API call to submit the form data
        console.log("Submitting CIA Wizard data:", formData);
        
        // Show success message and redirect
        alert("CIA Wizard data submitted successfully! Your report is being generated.");
        navigate("/dashboard");
      } catch (error) {
        console.error("Error submitting CIA Wizard data:", error);
        alert("There was an error submitting your data. Please try again.");
      }
    }
  };

  // Render form fields based on current step
  const renderStepContent = () => {
    const currentStepId = steps[currentStep].id;
    
    switch (currentStepId) {
      case "company":
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="company-name">Company Name *</Label>
              <Input
                id="company-name"
                value={formData.company.name}
                onChange={(e) => handleChange("company", "name", e.target.value)}
                placeholder="e.g. Acme Corporation"
                className={errors["company.name"] ? "border-destructive" : ""}
              />
              {errors["company.name"] && (
                <p className="text-sm text-destructive">{errors["company.name"]}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="company-industry">Industry *</Label>
              <Input
                id="company-industry"
                value={formData.company.industry}
                onChange={(e) => handleChange("company", "industry", e.target.value)}
                placeholder="e.g. Technology, Healthcare, Finance"
                className={errors["company.industry"] ? "border-destructive" : ""}
              />
              {errors["company.industry"] && (
                <p className="text-sm text-destructive">{errors["company.industry"]}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="company-size">Company Size</Label>
              <select
                id="company-size"
                value={formData.company.size}
                onChange={(e) => handleChange("company", "size", e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                <option value="">Select company size</option>
                <option value="1-10">1-10 employees</option>
                <option value="11-50">11-50 employees</option>
                <option value="51-200">51-200 employees</option>
                <option value="201-500">201-500 employees</option>
                <option value="501+">501+ employees</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="company-description">Brief Description</Label>
              <textarea
                id="company-description"
                value={formData.company.description}
                onChange={(e) => handleChange("company", "description", e.target.value)}
                placeholder="What does your company do? What products or services do you offer?"
                className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="company-founded">Year Founded</Label>
                <Input
                  id="company-founded"
                  value={formData.company.founded}
                  onChange={(e) => handleChange("company", "founded", e.target.value)}
                  placeholder="e.g. 2010"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="company-location">Primary Location</Label>
                <Input
                  id="company-location"
                  value={formData.company.location}
                  onChange={(e) => handleChange("company", "location", e.target.value)}
                  placeholder="e.g. San Francisco, CA"
                />
              </div>
            </div>
          </div>
        );
        
      case "website":
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="website-url">Website URL *</Label>
              <Input
                id="website-url"
                value={formData.website.url}
                onChange={(e) => handleChange("website", "url", e.target.value)}
                placeholder="e.g. https://www.example.com"
                className={errors["website.url"] ? "border-destructive" : ""}
              />
              {errors["website.url"] && (
                <p className="text-sm text-destructive">{errors["website.url"]}</p>
              )}
            </div>
            
            <div className="space-y-4 pt-4">
              <h4 className="text-sm font-medium">Analysis Options</h4>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="analyze-competitors"
                  checked={formData.website.analyzeCompetitors}
                  onChange={() => handleCheckboxChange("website", "analyzeCompetitors")}
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                />
                <Label htmlFor="analyze-competitors" className="text-sm font-normal">
                  Analyze competitor websites (+{creditCost.competitors} credits)
                </Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="include-social-media"
                  checked={formData.website.includeSocialMedia}
                  onChange={() => handleCheckboxChange("website", "includeSocialMedia")}
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                />
                <Label htmlFor="include-social-media" className="text-sm font-normal">
                  Include social media analysis (+{creditCost.socialMedia} credits)
                </Label>
              </div>
            </div>
            
            <div className="mt-6 p-4 bg-muted rounded-md">
              <div className="flex items-start space-x-2">
                <AlertCircle className="h-5 w-5 text-warning mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium">Website Analysis Information</p>
                  <p className="text-muted-foreground">
                    We'll analyze your website's structure, content, SEO factors, and performance metrics. 
                    This helps identify strengths and improvement opportunities.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );
        
      case "keywords":
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="primary-keyword">Primary Keyword/Phrase *</Label>
              <Input
                id="primary-keyword"
                value={formData.keywords.primary}
                onChange={(e) => handleChange("keywords", "primary", e.target.value)}
                placeholder="e.g. digital marketing services"
                className={errors["keywords.primary"] ? "border-destructive" : ""}
              />
              {errors["keywords.primary"] && (
                <p className="text-sm text-destructive">{errors["keywords.primary"]}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="secondary-keyword">Secondary Keywords/Phrases</Label>
              <Input
                id="secondary-keyword"
                value={formData.keywords.secondary}
                onChange={(e) => handleChange("keywords", "secondary", e.target.value)}
                placeholder="e.g. SEO services, content marketing"
              />
              <p className="text-xs text-muted-foreground">Separate multiple keywords with commas</p>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="additional-keywords">Additional Keywords</Label>
              <textarea
                id="additional-keywords"
                value={formData.keywords.additional}
                onChange={(e) => handleChange("keywords", "additional", e.target.value)}
                placeholder="Enter any additional keywords or phrases you'd like to target"
                className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
              <p className="text-xs text-muted-foreground">
                Our system will also automatically suggest related keywords based on your inputs
              </p>
            </div>
            
            <div className="mt-6 p-4 bg-muted rounded-md">
              <div className="flex items-start space-x-2">
                <AlertCircle className="h-5 w-5 text-primary mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium">Keyword Research</p>
                  <p className="text-muted-foreground">
                    We'll use DataForSEO to analyze your keywords for search volume, competition, 
                    and ranking difficulty. This helps identify the most valuable keywords for your content strategy.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );
        
      case "competitors":
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="competitor-1">Main Competitor 1 *</Label>
              <Input
                id="competitor-1"
                value={formData.competitors.main[0]}
                onChange={(e) => handleCompetitorChange(0, e.target.value)}
                placeholder="e.g. https://www.competitor1.com"
                className={errors["competitors.main.0"] ? "border-destructive" : ""}
              />
              {errors["competitors.main.0"] && (
                <p className="text-sm text-destructive">{errors["competitors.main.0"]}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="competitor-2">Competitor 2</Label>
              <Input
                id="competitor-2"
                value={formData.competitors.main[1]}
                onChange={(e) => handleCompetitorChange(1, e.target.value)}
                placeholder="e.g. https://www.competitor2.com"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="competitor-3">Competitor 3</Label>
              <Input
                id="competitor-3"
                value={formData.competitors.main[2]}
                onChange={(e) => handleCompetitorChange(2, e.target.value)}
                placeholder="e.g. https://www.competitor3.com"
              />
            </div>
            
            <div className="space-y-4 pt-4">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="include-detection"
                  checked={formData.competitors.includeDetection}
                  onChange={() => handleCheckboxChange("competitors", "includeDetection")}
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                />
                <Label htmlFor="include-detection" className="text-sm font-normal">
                  Auto-detect additional competitors (+{creditCost.autoDetection} credits)
                </Label>
              </div>
            </div>
            
            <div className="mt-6 p-4 bg-muted rounded-md">
              <div className="flex items-start space-x-2">
                <AlertCircle className="h-5 w-5 text-warning mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium">Competitor Analysis</p>
                  <p className="text-muted-foreground">
                    We'll analyze your competitors' websites, content strategies, keywords, and backlink profiles
                    to identify their strengths and weaknesses.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );
        
      case "audience":
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="audience-demographics">Target Demographics *</Label>
              <textarea
                id="audience-demographics"
                value={formData.audience.demographics}
                onChange={(e) => handleChange("audience", "demographics", e.target.value)}
                placeholder="Describe your ideal customer (age, gender, location, income, etc.)"
                className={cn(
                  "flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                  errors["audience.demographics"] ? "border-destructive" : ""
                )}
              />
              {errors["audience.demographics"] && (
                <p className="text-sm text-destructive">{errors["audience.demographics"]}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="audience-pain-points">Pain Points & Challenges</Label>
              <textarea
                id="audience-pain-points"
                value={formData.audience.painPoints}
                onChange={(e) => handleChange("audience", "painPoints", e.target.value)}
                placeholder="What problems does your audience face that your product/service solves?"
                className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="audience-goals">Audience Goals</Label>
              <textarea
                id="audience-goals"
                value={formData.audience.goals}
                onChange={(e) => handleChange("audience", "goals", e.target.value)}
                placeholder="What does your audience want to achieve?"
                className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
            </div>
          </div>
        );
        
      case "goals":
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="goals-primary">Primary Marketing Goal *</Label>
              <select
                id="goals-primary"
                value={formData.goals.primary}
                onChange={(e) => handleChange("goals", "primary", e.target.value)}
                className={cn(
                  "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                  errors["goals.primary"] ? "border-destructive" : ""
                )}
              >
                <option value="">Select primary goal</option>
                <option value="brand_awareness">Increase Brand Awareness</option>
                <option value="lead_generation">Generate More Leads</option>
                <option value="sales">Increase Sales</option>
                <option value="customer_retention">Improve Customer Retention</option>
                <option value="thought_leadership">Establish Thought Leadership</option>
                <option value="seo_ranking">Improve SEO Rankings</option>
                <option value="social_engagement">Increase Social Media Engagement</option>
                <option value="other">Other</option>
              </select>
              {errors["goals.primary"] && (
                <p className="text-sm text-destructive">{errors["goals.primary"]}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="goals-kpis">Key Performance Indicators</Label>
              <textarea
                id="goals-kpis"
                value={formData.goals.kpis}
                onChange={(e) => handleChange("goals", "kpis", e.target.value)}
                placeholder="What metrics will you use to measure success? (e.g., website traffic, conversion rate, etc.)"
                className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="goals-timeline">Timeline</Label>
              <select
                id="goals-timeline"
                value={formData.goals.timeline}
                onChange={(e) => handleChange("goals", "timeline", e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                <option value="1 month">1 Month</option>
                <option value="3 months">3 Months</option>
                <option value="6 months">6 Months</option>
                <option value="1 year">1 Year</option>
              </select>
            </div>
          </div>
        );
        
      case "review":
        return (
          <div className="space-y-6">
            <div className="space-y-2">
              <h3 className="text-lg font-medium">Review Your Information</h3>
              <p className="text-sm text-muted-foreground">
                Please review all the information you've provided before submitting.
              </p>
            </div>
            
            {/* Company Information Summary */}
            <div className="border rounded-md p-4">
              <h4 className="font-medium flex items-center">
                <Building2 className="h-4 w-4 mr-2" />
                Company Information
              </h4>
              <dl className="mt-2 divide-y divide-border">
                <div className="grid grid-cols-3 py-2">
                  <dt className="text-sm font-medium">Company Name:</dt>
                  <dd className="text-sm col-span-2">{formData.company.name || "Not provided"}</dd>
                </div>
                <div className="grid grid-cols-3 py-2">
                  <dt className="text-sm font-medium">Industry:</dt>
                  <dd className="text-sm col-span-2">{formData.company.industry || "Not provided"}</dd>
                </div>
                <div className="grid grid-cols-3 py-2">
                  <dt className="text-sm font-medium">Size:</dt>
                  <dd className="text-sm col-span-2">{formData.company.size || "Not provided"}</dd>
                </div>
              </dl>
            </div>
            
            {/* Website Information Summary */}
            <div className="border rounded-md p-4">
              <h4 className="font-medium flex items-center">
                <Globe className="h-4 w-4 mr-2" />
                Website Information
              </h4>
              <dl className="mt-2 divide-y divide-border">
                <div className="grid grid-cols-3 py-2">
                  <dt className="text-sm font-medium">Website URL:</dt>
                  <dd className="text-sm col-span-2">{formData.website.url || "Not provided"}</dd>
                </div>
                <div className="grid grid-cols-3 py-2">
                  <dt className="text-sm font-medium">Analyze Competitors:</dt>
                  <dd className="text-sm col-span-2">{formData.website.analyzeCompetitors ? "Yes" : "No"}</dd>
                </div>
                <div className="grid grid-cols-3 py-2">
                  <dt className="text-sm font-medium">Include Social Media:</dt>
                  <dd className="text-sm col-span-2">{formData.website.includeSocialMedia ? "Yes" : "No"}</dd>
                </div>
              </dl>
            </div>
            
            {/* Keywords Summary */}
            <div className="border rounded-md p-4">
              <h4 className="font-medium flex items-center">
                <Search className="h-4 w-4 mr-2" />
                Keywords
              </h4>
              <dl className="mt-2 divide-y divide-border">
                <div className="grid grid-cols-3 py-2">
                  <dt className="text-sm font-medium">Primary:</dt>
                  <dd className="text-sm col-span-2">{formData.keywords.primary || "Not provided"}</dd>
                </div>
                <div className="grid grid-cols-3 py-2">
                  <dt className="text-sm font-medium">Secondary:</dt>
                  <dd className="text-sm col-span-2">{formData.keywords.secondary || "Not provided"}</dd>
                </div>
              </dl>
            </div>
            
            {/* Credit Cost Summary */}
            <div className="border rounded-md p-4 bg-muted">
              <h4 className="font-medium flex items-center">
                <CreditCard className="h-4 w-4 mr-2" />
                Ops Credits Cost
              </h4>
              <dl className="mt-2 divide-y divide-border">
                <div className="grid grid-cols-3 py-2">
                  <dt className="text-sm font-medium">Base Cost:</dt>
                  <dd className="text-sm col-span-2">{creditCost.base} credits</dd>
                </div>
                {formData.website.analyzeCompetitors && (
                  <div className="grid grid-cols-3 py-2">
                    <dt className="text-sm font-medium">Competitor Analysis:</dt>
                    <dd className="text-sm col-span-2">+{creditCost.competitors} credits</dd>
                  </div>
                )}
                {formData.website.includeSocialMedia && (
                  <div className="grid grid-cols-3 py-2">
                    <dt className="text-sm font-medium">Social Media Analysis:</dt>
                    <dd className="text-sm col-span-2">+{creditCost.socialMedia} credits</dd>
                  </div>
                )}
                {formData.competitors.includeDetection && (
                  <div className="grid grid-cols-3 py-2">
                    <dt className="text-sm font-medium">Auto-Competitor Detection:</dt>
                    <dd className="text-sm col-span-2">+{creditCost.autoDetection} credits</dd>
                  </div>
                )}
                <div className="grid grid-cols-3 py-2 font-medium">
                  <dt className="text-sm">Total Cost:</dt>
                  <dd className="text-sm col-span-2">{creditCost.total} credits</dd>
                </div>
              </dl>
            </div>
          </div>
        );
        
      default:
        return null;
    }
  };

  // Calculate progress percentage
  const progress = Math.round(((currentStep) / (steps.length - 1)) * 100);

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
        
        {/* Progress Bar */}
        <div className="px-6">
          <div className="w-full bg-muted rounded-full h-2.5">
            <div
              className="bg-gradient-primary h-2.5 rounded-full"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="flex justify-between mt-2 text-xs text-muted-foreground">
            <span>Start</span>
            <span>{progress}% Complete</span>
            <span>Finish</span>
          </div>
        </div>
        
        {/* Step Indicators */}
        <div className="px-6 py-4">
          <div className="flex flex-wrap justify-center gap-2">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={cn(
                  "flex items-center px-3 py-1.5 rounded-full text-xs font-medium",
                  currentStep === index
                    ? "bg-primary text-primary-foreground"
                    : index < currentStep
                    ? "bg-success text-success-foreground"
                    : "bg-muted text-muted-foreground"
                )}
              >
                {step.icon}
                <span className="ml-1.5">{step.title}</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Current Step Content */}
        <CardContent>
          <div className="mb-6">
            <h2 className="text-2xl font-semibold">{steps[currentStep].title}</h2>
            <p className="text-muted-foreground">{steps[currentStep].description}</p>
          </div>
          
          {renderStepContent()}
        </CardContent>
        
        {/* Credit Cost Display */}
        {currentStep !== steps.length - 1 && (
          <div className="px-6 py-2">
            <div className="flex items-center justify-end space-x-2">
              <CreditCard className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                Estimated cost: <strong>{creditCost.total} Ops Credits</strong>
              </span>
            </div>
          </div>
        )}
        
        {/* Navigation Buttons */}
        <CardFooter className="flex justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentStep === 0}
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            Previous
          </Button>
          
          {currentStep < steps.length - 1 ? (
            <Button onClick={handleNext}>
              Next
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          ) : (
            <Button variant="gradient" onClick={handleSubmit}>
              Submit
              <CheckCircle2 className="ml-2 h-4 w-4" />
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
};

export default CIAWizard;
