import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { 
  CreditCard, 
  AlertCircle, 
  TrendingUp, 
  TrendingDown, 
  Plus, 
  History,
  RefreshCw,
  Loader2
} from "lucide-react";

// Import shadcn/ui components
import { Button } from "../ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../ui/card";

// Utility functions
import { cn, formatCurrency } from "../../lib/utils";

/**
 * CreditDisplay - Component to display user's current Ops Credits balance with visual indicators
 * 
 * Features:
 * - Shows current credit balance prominently
 * - Visual indicators for low balance
 * - Recent transaction history preview
 * - Button to purchase more credits
 */
const CreditDisplay = ({ 
  showTransactions = true, 
  compact = false,
  onPurchase = null,
  className = "" 
}) => {
  const navigate = useNavigate();
  
  // State management
  const [creditData, setCreditData] = useState({
    balance: 0,
    totalPurchased: 0,
    totalUsed: 0,
    lowBalanceThreshold: 10
  });
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch credit balance and recent transactions
  const fetchCreditData = async () => {
    try {
      setRefreshing(true);
      
      // Get user balance
      const balanceResponse = await axios.get('/api/credits/balance');
      setCreditData(balanceResponse.data);
      
      // Get recent transactions if needed
      if (showTransactions) {
        const transactionsResponse = await axios.get('/api/credits/transactions', {
          params: { limit: 3 } // Only get the 3 most recent transactions
        });
        setTransactions(transactionsResponse.data.transactions);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching credit data:', err);
      setError('Failed to load credit information');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Load credit data on component mount
  useEffect(() => {
    fetchCreditData();
  }, [showTransactions]);

  // Handle refresh button click
  const handleRefresh = () => {
    fetchCreditData();
  };

  // Handle purchase button click
  const handlePurchase = () => {
    if (onPurchase) {
      onPurchase();
    } else {
      navigate('/credits/purchase');
    }
  };

  // Determine if balance is low
  const isLowBalance = creditData.balance <= creditData.lowBalanceThreshold;

  // Format transaction type for display
  const formatTransactionType = (type) => {
    switch (type) {
      case 'purchase':
        return 'Purchase';
      case 'usage':
        return 'Used';
      case 'refund':
        return 'Refunded';
      case 'adjustment':
        return 'Adjusted';
      case 'subscription_allocation':
        return 'Subscription';
      default:
        return type.charAt(0).toUpperCase() + type.slice(1);
    }
  };

  // Render compact version
  if (compact) {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        <CreditCard className="h-4 w-4 text-primary" />
        <span className="font-medium">
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin inline mr-1" />
          ) : (
            <>
              {creditData.balance} <span className="text-xs text-muted-foreground">credits</span>
            </>
          )}
        </span>
        {isLowBalance && !loading && (
          <AlertCircle className="h-4 w-4 text-warning" />
        )}
      </div>
    );
  }

  // Render full version
  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="pb-3">
        <div className="flex justify-between items-center">
          <CardTitle className="text-xl flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Ops Credits
          </CardTitle>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleRefresh} 
            disabled={refreshing}
            className="h-8 w-8 p-0"
          >
            {refreshing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            <span className="sr-only">Refresh</span>
          </Button>
        </div>
        <CardDescription>Your operation credit balance and usage</CardDescription>
      </CardHeader>
      
      <CardContent>
        {loading ? (
          <div className="flex justify-center items-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : error ? (
          <div className="bg-destructive/10 text-destructive p-3 rounded-md flex items-start gap-2">
            <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium">Error loading credit information</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        ) : (
          <>
            {/* Credit Balance Display */}
            <div className={cn(
              "rounded-lg p-4 mb-4",
              isLowBalance 
                ? "bg-warning/10 border border-warning/20" 
                : "bg-primary/10 border border-primary/20"
            )}>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium text-muted-foreground">Current Balance</span>
                {isLowBalance && (
                  <div className="flex items-center text-warning text-xs font-medium">
                    <AlertCircle className="h-3 w-3 mr-1" />
                    Low Balance
                  </div>
                )}
              </div>
              
              <div className="text-3xl font-bold mb-2">
                {creditData.balance} <span className="text-base font-normal text-muted-foreground">credits</span>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1 text-success" />
                  <span className="text-muted-foreground">Total Purchased: </span>
                  <span className="ml-1 font-medium">{creditData.totalPurchased}</span>
                </div>
                <div className="flex items-center">
                  <TrendingDown className="h-3 w-3 mr-1 text-destructive" />
                  <span className="text-muted-foreground">Total Used: </span>
                  <span className="ml-1 font-medium">{creditData.totalUsed}</span>
                </div>
              </div>
            </div>
            
            {/* Recent Transactions */}
            {showTransactions && transactions.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium flex items-center">
                    <History className="h-4 w-4 mr-1" />
                    Recent Activity
                  </h4>
                  <Button 
                    variant="link" 
                    size="sm" 
                    className="h-auto p-0 text-xs"
                    onClick={() => navigate('/credits/history')}
                  >
                    View All
                  </Button>
                </div>
                
                <div className="space-y-2">
                  {transactions.map(transaction => (
                    <div 
                      key={transaction._id} 
                      className="flex justify-between items-center p-2 text-sm rounded-md bg-background border"
                    >
                      <div>
                        <div className="font-medium">
                          {formatTransactionType(transaction.type)}
                          {transaction.operation && (
                            <span className="text-muted-foreground"> - {transaction.metadata?.operationName || transaction.operation}</span>
                          )}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {new Date(transaction.createdAt).toLocaleDateString()}
                        </div>
                      </div>
                      <div className={cn(
                        "font-medium",
                        transaction.amount > 0 ? "text-success" : "text-destructive"
                      )}>
                        {transaction.amount > 0 ? "+" : ""}{transaction.amount}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
      
      <CardFooter>
        <Button 
          onClick={handlePurchase} 
          className="w-full" 
          variant={isLowBalance ? "default" : "outline"}
        >
          <Plus className="h-4 w-4 mr-2" />
          Purchase Credits
        </Button>
      </CardFooter>
    </Card>
  );
};

export default CreditDisplay;
