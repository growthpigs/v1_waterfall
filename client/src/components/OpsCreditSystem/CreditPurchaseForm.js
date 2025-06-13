import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { 
  CreditCard, 
  Package, 
  Tag, 
  Check, 
  X, 
  AlertCircle,
  Loader2,
  BadgePercent,
  ArrowRight,
  Sparkles
} from "lucide-react";

// Import shadcn/ui components
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../ui/card";

// Utility functions
import { cn, formatCurrency } from "../../lib/utils";

/**
 * CreditPurchaseForm - Component for purchasing Ops Credits with package selection and coupon support
 * 
 * Features:
 * - Display available credit packages
 * - Select package
 * - Apply coupon codes
 * - Process payment
 * - Show purchase confirmation
 */
const CreditPurchaseForm = ({ onSuccess }) => {
  const navigate = useNavigate();
  
  // State management
  const [packages, setPackages] = useState([]);
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [couponCode, setCouponCode] = useState("");
  const [appliedCoupon, setAppliedCoupon] = useState(null);
  const [couponError, setCouponError] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("credit_card");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [validatingCoupon, setValidatingCoupon] = useState(false);

  // Fetch available credit packages
  useEffect(() => {
    const fetchPackages = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/credits/packages');
        setPackages(response.data);
        
        // Auto-select featured package or first package
        const featured = response.data.find(pkg => pkg.isFeatured);
        setSelectedPackage(featured || (response.data.length > 0 ? response.data[0] : null));
      } catch (err) {
        console.error('Error fetching credit packages:', err);
        setError('Failed to load available credit packages. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchPackages();
  }, []);

  // Handle package selection
  const handleSelectPackage = (pkg) => {
    setSelectedPackage(pkg);
  };

  // Handle coupon code application
  const handleApplyCoupon = async () => {
    if (!couponCode.trim()) {
      setCouponError("Please enter a coupon code");
      return;
    }
    
    try {
      setValidatingCoupon(true);
      setCouponError("");
      
      // Call API to validate coupon
      const response = await axios.post('/api/coupons/validate', {
        code: couponCode,
        context: {
          type: 'credit_purchase',
          packageId: selectedPackage?._id
        }
      });
      
      if (response.data.valid) {
        setAppliedCoupon(response.data.coupon);
        setCouponError("");
      } else {
        setAppliedCoupon(null);
        setCouponError(response.data.message || "Invalid coupon code");
      }
    } catch (err) {
      console.error('Error validating coupon:', err);
      setAppliedCoupon(null);
      setCouponError(err.response?.data?.message || "Failed to validate coupon");
    } finally {
      setValidatingCoupon(false);
    }
  };

  // Remove applied coupon
  const handleRemoveCoupon = () => {
    setAppliedCoupon(null);
    setCouponCode("");
    setCouponError("");
  };

  // Calculate final price with coupon discount
  const calculateFinalPrice = () => {
    if (!selectedPackage) return 0;
    
    let finalPrice = selectedPackage.basePrice;
    
    if (appliedCoupon) {
      if (appliedCoupon.discountType === 'percentage') {
        finalPrice = finalPrice * (1 - (appliedCoupon.discountValue / 100));
      } else if (appliedCoupon.discountType === 'fixed') {
        finalPrice = Math.max(0, finalPrice - appliedCoupon.discountValue);
      } else if (appliedCoupon.discountType === 'free') {
        finalPrice = 0;
      }
    }
    
    return Math.max(0, Math.round(finalPrice));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedPackage) {
      setError("Please select a credit package");
      return;
    }
    
    try {
      setSubmitting(true);
      setError(null);
      
      // In a real implementation, this would integrate with a payment processor
      // For now, we'll simulate a successful payment
      const paymentDetails = {
        method: paymentMethod,
        amount: calculateFinalPrice(),
        currency: selectedPackage.currency,
        success: true,
        id: `sim_${Date.now()}`
      };
      
      // Process the purchase
      const response = await axios.post('/api/credits/purchase', {
        packageId: selectedPackage._id,
        paymentDetails,
        couponId: appliedCoupon?._id
      });
      
      // Show success message
      setSuccess(true);
      
      // Call onSuccess callback if provided
      if (onSuccess) {
        onSuccess(response.data);
      }
      
      // Reset form after short delay
      setTimeout(() => {
        navigate('/credits');
      }, 3000);
      
    } catch (err) {
      console.error('Error processing purchase:', err);
      setError(err.response?.data?.message || "Failed to process payment. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  // If loading, show loading state
  if (loading) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Purchase Ops Credits</CardTitle>
          <CardDescription>Loading available packages...</CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  // If success, show success message
  if (success) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader className="text-center border-b pb-6">
          <div className="mx-auto rounded-full bg-success/20 p-3 w-16 h-16 flex items-center justify-center mb-4">
            <Check className="h-8 w-8 text-success" />
          </div>
          <CardTitle className="text-2xl">Purchase Successful!</CardTitle>
          <CardDescription>Your Ops Credits have been added to your account</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <div className="bg-muted rounded-md p-4">
              <div className="flex justify-between mb-2">
                <span className="text-muted-foreground">Package:</span>
                <span className="font-medium">{selectedPackage?.name}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span className="text-muted-foreground">Credits:</span>
                <span className="font-medium">
                  {selectedPackage?.creditAmount + (selectedPackage?.bonusCredits || 0)}
                  {selectedPackage?.bonusCredits > 0 && (
                    <span className="text-success ml-1">
                      (includes {selectedPackage.bonusCredits} bonus)
                    </span>
                  )}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Amount Paid:</span>
                <span className="font-medium">
                  {formatCurrency(calculateFinalPrice() / 100, selectedPackage?.currency === 'EUR' ? '€' : '$')}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
        <CardFooter>
          <Button 
            onClick={() => navigate('/credits')} 
            className="w-full"
          >
            View My Credits
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </CardFooter>
      </Card>
    );
  }

  // Main form render
  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          Purchase Ops Credits
        </CardTitle>
        <CardDescription>
          Select a package and payment method to purchase Ops Credits
        </CardDescription>
      </CardHeader>
      
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          {/* Error message if any */}
          {error && (
            <div className="bg-destructive/10 text-destructive p-3 rounded-md flex items-start gap-2">
              <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium">Error</p>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}
          
          {/* Package Selection */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium flex items-center">
              <Package className="h-4 w-4 mr-2" />
              Select Credit Package
            </h3>
            
            <div className="grid gap-3 sm:grid-cols-1 md:grid-cols-3">
              {packages.map((pkg) => (
                <div
                  key={pkg._id}
                  className={cn(
                    "border rounded-md p-4 cursor-pointer transition-all",
                    selectedPackage?._id === pkg._id
                      ? "border-primary bg-primary/5 shadow-sm"
                      : "hover:border-primary/50"
                  )}
                  onClick={() => handleSelectPackage(pkg)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium">{pkg.name}</h4>
                    {pkg.isFeatured && (
                      <span className="bg-primary/10 text-primary text-xs px-2 py-0.5 rounded-full">
                        Best Value
                      </span>
                    )}
                  </div>
                  
                  <div className="text-2xl font-bold mb-1">
                    {pkg.creditAmount}
                    <span className="text-sm font-normal text-muted-foreground ml-1">credits</span>
                  </div>
                  
                  {pkg.bonusCredits > 0 && (
                    <div className="flex items-center text-success text-sm mb-2">
                      <Sparkles className="h-3 w-3 mr-1" />
                      +{pkg.bonusCredits} bonus credits
                    </div>
                  )}
                  
                  <div className="text-sm font-medium">
                    {formatCurrency(pkg.basePrice / 100, pkg.currency === 'EUR' ? '€' : '$')}
                  </div>
                  
                  {pkg.description && (
                    <p className="text-xs text-muted-foreground mt-2">{pkg.description}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
          
          {/* Coupon Code */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium flex items-center">
              <Tag className="h-4 w-4 mr-2" />
              Coupon Code
            </h3>
            
            {appliedCoupon ? (
              <div className="flex items-center justify-between bg-success/10 border border-success/20 rounded-md p-3">
                <div className="flex items-center">
                  <BadgePercent className="h-5 w-5 text-success mr-2" />
                  <div>
                    <p className="font-medium">{appliedCoupon.code}</p>
                    <p className="text-xs text-success">
                      {appliedCoupon.discountType === 'percentage' && `${appliedCoupon.discountValue}% off`}
                      {appliedCoupon.discountType === 'fixed' && `${formatCurrency(appliedCoupon.discountValue / 100)} off`}
                      {appliedCoupon.discountType === 'free' && 'Free'}
                    </p>
                  </div>
                </div>
                <Button 
                  type="button" 
                  variant="ghost" 
                  size="sm" 
                  onClick={handleRemoveCoupon}
                >
                  <X className="h-4 w-4" />
                  <span className="sr-only">Remove coupon</span>
                </Button>
              </div>
            ) : (
              <div className="flex space-x-2">
                <div className="flex-1">
                  <Input
                    placeholder="Enter coupon code"
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value)}
                    className={couponError ? "border-destructive" : ""}
                  />
                  {couponError && (
                    <p className="text-xs text-destructive mt-1">{couponError}</p>
                  )}
                </div>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={handleApplyCoupon}
                  disabled={validatingCoupon || !couponCode.trim()}
                >
                  {validatingCoupon ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-1" />
                  ) : (
                    <Check className="h-4 w-4 mr-1" />
                  )}
                  Apply
                </Button>
              </div>
            )}
          </div>
          
          {/* Payment Method */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium">Payment Method</h3>
            
            <div className="space-y-2">
              <div className="flex items-center">
                <input
                  type="radio"
                  id="credit-card"
                  name="payment-method"
                  value="credit_card"
                  checked={paymentMethod === "credit_card"}
                  onChange={() => setPaymentMethod("credit_card")}
                  className="h-4 w-4 text-primary focus:ring-primary"
                />
                <Label htmlFor="credit-card" className="ml-2">Credit Card</Label>
              </div>
              
              <div className="flex items-center">
                <input
                  type="radio"
                  id="paypal"
                  name="payment-method"
                  value="paypal"
                  checked={paymentMethod === "paypal"}
                  onChange={() => setPaymentMethod("paypal")}
                  className="h-4 w-4 text-primary focus:ring-primary"
                />
                <Label htmlFor="paypal" className="ml-2">PayPal</Label>
              </div>
            </div>
          </div>
          
          {/* Order Summary */}
          {selectedPackage && (
            <div className="border rounded-md p-4 bg-muted/50">
              <h3 className="font-medium mb-3">Order Summary</h3>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>{selectedPackage.name}</span>
                  <span>{formatCurrency(selectedPackage.basePrice / 100, selectedPackage.currency === 'EUR' ? '€' : '$')}</span>
                </div>
                
                {appliedCoupon && (
                  <div className="flex justify-between text-success">
                    <span>
                      Coupon: {appliedCoupon.code}
                      {appliedCoupon.discountType === 'percentage' && ` (${appliedCoupon.discountValue}% off)`}
                    </span>
                    <span>
                      -{formatCurrency((selectedPackage.basePrice - calculateFinalPrice()) / 100, selectedPackage.currency === 'EUR' ? '€' : '$')}
                    </span>
                  </div>
                )}
                
                <div className="border-t pt-2 mt-2 font-medium flex justify-between">
                  <span>Total</span>
                  <span>{formatCurrency(calculateFinalPrice() / 100, selectedPackage.currency === 'EUR' ? '€' : '$')}</span>
                </div>
                
                <div className="border-t pt-2 mt-2 flex justify-between text-sm text-muted-foreground">
                  <span>Credits you'll receive</span>
                  <span className="font-medium">
                    {selectedPackage.creditAmount + (selectedPackage.bonusCredits || 0)}
                    {selectedPackage.bonusCredits > 0 && (
                      <span className="text-success ml-1">
                        (includes {selectedPackage.bonusCredits} bonus)
                      </span>
                    )}
                  </span>
                </div>
              </div>
            </div>
          )}
        </CardContent>
        
        <CardFooter className="flex flex-col space-y-2">
          <Button 
            type="submit" 
            className="w-full" 
            disabled={submitting || !selectedPackage}
          >
            {submitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                Complete Purchase
                <ArrowRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
          
          <p className="text-xs text-center text-muted-foreground">
            By completing this purchase, you agree to our Terms of Service and Privacy Policy.
          </p>
        </CardFooter>
      </form>
    </Card>
  );
};

export default CreditPurchaseForm;
