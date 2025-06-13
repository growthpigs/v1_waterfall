import React, { useState, useEffect } from "react";
import axios from "axios";
import { 
  Settings, 
  Package, 
  Tag, 
  Edit, 
  Trash2, 
  Plus,
  Save,
  X,
  AlertCircle,
  Loader2,
  CreditCard,
  DollarSign,
  Percent,
  Check,
  RefreshCw
} from "lucide-react";

// Import shadcn/ui components
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../ui/card";

// Utility functions
import { cn, formatCurrency } from "../../lib/utils";

/**
 * AdminCreditControls - Component for administrators to manage operation costs and credit packages
 * 
 * Features:
 * - View and edit operation costs
 * - View and edit credit packages
 * - Add new operations and packages
 * - Delete operations and packages
 */
const AdminCreditControls = () => {
  // Tab state
  const [activeTab, setActiveTab] = useState("operations");
  
  // Operations state
  const [operations, setOperations] = useState([]);
  const [operationsLoading, setOperationsLoading] = useState(true);
  const [operationsError, setOperationsError] = useState(null);
  
  // Packages state
  const [packages, setPackages] = useState([]);
  const [packagesLoading, setPackagesLoading] = useState(true);
  const [packagesError, setPackagesError] = useState(null);
  
  // Edit states
  const [editingOperation, setEditingOperation] = useState(null);
  const [editingPackage, setEditingPackage] = useState(null);
  
  // New item states
  const [showNewOperation, setShowNewOperation] = useState(false);
  const [newOperation, setNewOperation] = useState({
    operationId: "",
    displayName: "",
    category: "content",
    creditCost: 1,
    description: "",
    isActive: true
  });
  
  const [showNewPackage, setShowNewPackage] = useState(false);
  const [newPackage, setNewPackage] = useState({
    name: "",
    creditAmount: 100,
    basePrice: 1000,
    currency: "EUR",
    bonusCredits: 0,
    sortOrder: 0,
    isActive: true,
    isFeatured: false,
    description: ""
  });
  
  // Delete confirmation states
  const [deleteConfirmation, setDeleteConfirmation] = useState({
    show: false,
    type: null, // "operation" or "package"
    id: null,
    name: ""
  });
  
  // Form errors
  const [formErrors, setFormErrors] = useState({});
  
  // Action states
  const [saving, setSaving] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch operations and packages on component mount
  useEffect(() => {
    fetchOperations();
    fetchPackages();
  }, []);

  // Fetch operations
  const fetchOperations = async () => {
    try {
      setOperationsLoading(true);
      setOperationsError(null);
      const response = await axios.get('/api/credits/operations');
      setOperations(response.data);
    } catch (error) {
      console.error('Error fetching operations:', error);
      setOperationsError('Failed to load operations. Please try again.');
    } finally {
      setOperationsLoading(false);
    }
  };

  // Fetch packages
  const fetchPackages = async () => {
    try {
      setPackagesLoading(true);
      setPackagesError(null);
      const response = await axios.get('/api/credits/packages');
      setPackages(response.data);
    } catch (error) {
      console.error('Error fetching packages:', error);
      setPackagesError('Failed to load credit packages. Please try again.');
    } finally {
      setPackagesLoading(false);
    }
  };

  // Refresh data
  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([fetchOperations(), fetchPackages()]);
    setRefreshing(false);
  };

  // Handle tab change
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    // Reset editing and new item states
    setEditingOperation(null);
    setEditingPackage(null);
    setShowNewOperation(false);
    setShowNewPackage(false);
    setFormErrors({});
  };

  // Handle operation edit
  const handleEditOperation = (operation) => {
    setEditingOperation({ ...operation });
    setShowNewOperation(false);
    setFormErrors({});
  };

  // Handle package edit
  const handleEditPackage = (pkg) => {
    setEditingPackage({ ...pkg });
    setShowNewPackage(false);
    setFormErrors({});
  };

  // Handle operation input change
  const handleOperationChange = (field, value) => {
    setEditingOperation(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error for this field if exists
    if (formErrors[field]) {
      setFormErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // Handle new operation input change
  const handleNewOperationChange = (field, value) => {
    setNewOperation(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error for this field if exists
    if (formErrors[field]) {
      setFormErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // Handle package input change
  const handlePackageChange = (field, value) => {
    setEditingPackage(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error for this field if exists
    if (formErrors[field]) {
      setFormErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // Handle new package input change
  const handleNewPackageChange = (field, value) => {
    setNewPackage(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error for this field if exists
    if (formErrors[field]) {
      setFormErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // Validate operation form
  const validateOperationForm = (operation) => {
    const errors = {};
    
    if (!operation.operationId.trim()) {
      errors.operationId = "Operation ID is required";
    } else if (!/^[a-z0-9_]+$/.test(operation.operationId)) {
      errors.operationId = "Operation ID can only contain lowercase letters, numbers, and underscores";
    }
    
    if (!operation.displayName.trim()) {
      errors.displayName = "Display name is required";
    }
    
    if (operation.creditCost < 0) {
      errors.creditCost = "Credit cost cannot be negative";
    }
    
    return errors;
  };

  // Validate package form
  const validatePackageForm = (pkg) => {
    const errors = {};
    
    if (!pkg.name.trim()) {
      errors.name = "Name is required";
    }
    
    if (pkg.creditAmount <= 0) {
      errors.creditAmount = "Credit amount must be positive";
    }
    
    if (pkg.basePrice < 0) {
      errors.basePrice = "Price cannot be negative";
    }
    
    if (pkg.bonusCredits < 0) {
      errors.bonusCredits = "Bonus credits cannot be negative";
    }
    
    return errors;
  };

  // Save operation changes
  const handleSaveOperation = async () => {
    const errors = validateOperationForm(editingOperation);
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    
    try {
      setSaving(true);
      
      await axios.put(`/api/credits/admin/operations/${editingOperation.operationId}`, {
        displayName: editingOperation.displayName,
        creditCost: Number(editingOperation.creditCost),
        description: editingOperation.description,
        isActive: editingOperation.isActive
      });
      
      // Update local state
      setOperations(prev => 
        prev.map(op => 
          op.operationId === editingOperation.operationId ? editingOperation : op
        )
      );
      
      // Reset editing state
      setEditingOperation(null);
      setFormErrors({});
    } catch (error) {
      console.error('Error saving operation:', error);
      setFormErrors({
        submit: error.response?.data?.message || "Failed to save changes. Please try again."
      });
    } finally {
      setSaving(false);
    }
  };

  // Create new operation
  const handleCreateOperation = async () => {
    const errors = validateOperationForm(newOperation);
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    
    // Check if operation ID already exists
    if (operations.some(op => op.operationId === newOperation.operationId)) {
      setFormErrors({
        operationId: "Operation ID already exists"
      });
      return;
    }
    
    try {
      setSaving(true);
      
      const response = await axios.post('/api/credits/admin/operations', {
        operationId: newOperation.operationId,
        displayName: newOperation.displayName,
        category: newOperation.category,
        creditCost: Number(newOperation.creditCost),
        description: newOperation.description,
        isActive: newOperation.isActive
      });
      
      // Update local state
      setOperations(prev => [...prev, response.data]);
      
      // Reset form
      setShowNewOperation(false);
      setNewOperation({
        operationId: "",
        displayName: "",
        category: "content",
        creditCost: 1,
        description: "",
        isActive: true
      });
      setFormErrors({});
    } catch (error) {
      console.error('Error creating operation:', error);
      setFormErrors({
        submit: error.response?.data?.message || "Failed to create operation. Please try again."
      });
    } finally {
      setSaving(false);
    }
  };

  // Save package changes
  const handleSavePackage = async () => {
    const errors = validatePackageForm(editingPackage);
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    
    try {
      setSaving(true);
      
      await axios.put(`/api/credits/admin/packages/${editingPackage._id}`, {
        name: editingPackage.name,
        creditAmount: Number(editingPackage.creditAmount),
        basePrice: Number(editingPackage.basePrice),
        bonusCredits: Number(editingPackage.bonusCredits),
        sortOrder: Number(editingPackage.sortOrder),
        isActive: editingPackage.isActive,
        isFeatured: editingPackage.isFeatured,
        description: editingPackage.description
      });
      
      // Update local state
      setPackages(prev => 
        prev.map(pkg => 
          pkg._id === editingPackage._id ? editingPackage : pkg
        )
      );
      
      // Reset editing state
      setEditingPackage(null);
      setFormErrors({});
    } catch (error) {
      console.error('Error saving package:', error);
      setFormErrors({
        submit: error.response?.data?.message || "Failed to save changes. Please try again."
      });
    } finally {
      setSaving(false);
    }
  };

  // Create new package
  const handleCreatePackage = async () => {
    const errors = validatePackageForm(newPackage);
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    
    try {
      setSaving(true);
      
      const response = await axios.post('/api/credits/admin/packages', {
        name: newPackage.name,
        creditAmount: Number(newPackage.creditAmount),
        basePrice: Number(newPackage.basePrice),
        currency: newPackage.currency,
        bonusCredits: Number(newPackage.bonusCredits),
        sortOrder: Number(newPackage.sortOrder),
        isActive: newPackage.isActive,
        isFeatured: newPackage.isFeatured,
        description: newPackage.description
      });
      
      // Update local state
      setPackages(prev => [...prev, response.data]);
      
      // Reset form
      setShowNewPackage(false);
      setNewPackage({
        name: "",
        creditAmount: 100,
        basePrice: 1000,
        currency: "EUR",
        bonusCredits: 0,
        sortOrder: 0,
        isActive: true,
        isFeatured: false,
        description: ""
      });
      setFormErrors({});
    } catch (error) {
      console.error('Error creating package:', error);
      setFormErrors({
        submit: error.response?.data?.message || "Failed to create package. Please try again."
      });
    } finally {
      setSaving(false);
    }
  };

  // Show delete confirmation
  const confirmDelete = (type, id, name) => {
    setDeleteConfirmation({
      show: true,
      type,
      id,
      name
    });
  };

  // Cancel delete
  const cancelDelete = () => {
    setDeleteConfirmation({
      show: false,
      type: null,
      id: null,
      name: ""
    });
  };

  // Execute delete
  const executeDelete = async () => {
    try {
      setSaving(true);
      
      if (deleteConfirmation.type === "operation") {
        // In a real implementation, you would call an API endpoint to delete the operation
        // For now, we'll just update the local state
        setOperations(prev => prev.filter(op => op.operationId !== deleteConfirmation.id));
      } else if (deleteConfirmation.type === "package") {
        // In a real implementation, you would call an API endpoint to delete the package
        // For now, we'll just update the local state
        setPackages(prev => prev.filter(pkg => pkg._id !== deleteConfirmation.id));
      }
      
      // Reset confirmation state
      cancelDelete();
    } catch (error) {
      console.error('Error deleting item:', error);
      // Show error message
    } finally {
      setSaving(false);
    }
  };

  // Cancel editing
  const cancelEditing = () => {
    setEditingOperation(null);
    setEditingPackage(null);
    setFormErrors({});
  };

  // Cancel new item
  const cancelNewItem = () => {
    setShowNewOperation(false);
    setShowNewPackage(false);
    setFormErrors({});
  };

  // Render loading state
  const renderLoading = () => (
    <div className="flex justify-center items-center py-12">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  );

  // Render error state
  const renderError = (message) => (
    <div className="bg-destructive/10 text-destructive p-4 rounded-md flex items-start gap-3">
      <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
      <div>
        <p className="font-medium">Error</p>
        <p>{message}</p>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleRefresh} 
          className="mt-2"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Try Again
        </Button>
      </div>
    </div>
  );

  // Render operations tab
  const renderOperationsTab = () => {
    if (operationsLoading) {
      return renderLoading();
    }
    
    if (operationsError) {
      return renderError(operationsError);
    }
    
    return (
      <div className="space-y-6">
        {/* New Operation Form */}
        {showNewOperation && (
          <Card className="border-primary/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Add New Operation</CardTitle>
              <CardDescription>Create a new operation cost configuration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="new-operation-id">Operation ID *</Label>
                  <Input
                    id="new-operation-id"
                    value={newOperation.operationId}
                    onChange={(e) => handleNewOperationChange("operationId", e.target.value)}
                    placeholder="e.g. seo_blog_post"
                    className={formErrors.operationId ? "border-destructive" : ""}
                  />
                  {formErrors.operationId && (
                    <p className="text-xs text-destructive">{formErrors.operationId}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    Unique identifier, lowercase with underscores
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="new-operation-name">Display Name *</Label>
                  <Input
                    id="new-operation-name"
                    value={newOperation.displayName}
                    onChange={(e) => handleNewOperationChange("displayName", e.target.value)}
                    placeholder="e.g. SEO Blog Post"
                    className={formErrors.displayName ? "border-destructive" : ""}
                  />
                  {formErrors.displayName && (
                    <p className="text-xs text-destructive">{formErrors.displayName}</p>
                  )}
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="new-operation-category">Category</Label>
                  <select
                    id="new-operation-category"
                    value={newOperation.category}
                    onChange={(e) => handleNewOperationChange("category", e.target.value)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  >
                    <option value="cia">CIA</option>
                    <option value="seo">SEO</option>
                    <option value="content">Content</option>
                    <option value="social">Social</option>
                    <option value="analysis">Analysis</option>
                    <option value="export">Export</option>
                  </select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="new-operation-cost">Credit Cost *</Label>
                  <Input
                    id="new-operation-cost"
                    type="number"
                    min="0"
                    value={newOperation.creditCost}
                    onChange={(e) => handleNewOperationChange("creditCost", parseInt(e.target.value) || 0)}
                    className={formErrors.creditCost ? "border-destructive" : ""}
                  />
                  {formErrors.creditCost && (
                    <p className="text-xs text-destructive">{formErrors.creditCost}</p>
                  )}
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="new-operation-description">Description</Label>
                <textarea
                  id="new-operation-description"
                  value={newOperation.description}
                  onChange={(e) => handleNewOperationChange("description", e.target.value)}
                  placeholder="Describe what this operation does"
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="new-operation-active"
                  checked={newOperation.isActive}
                  onChange={(e) => handleNewOperationChange("isActive", e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                />
                <Label htmlFor="new-operation-active" className="text-sm font-normal">
                  Active (available for use)
                </Label>
              </div>
              
              {formErrors.submit && (
                <div className="text-sm text-destructive">
                  {formErrors.submit}
                </div>
              )}
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button
                variant="ghost"
                onClick={cancelNewItem}
              >
                <X className="h-4 w-4 mr-2" />
                Cancel
              </Button>
              <Button
                onClick={handleCreateOperation}
                disabled={saving}
              >
                {saving ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Plus className="h-4 w-4 mr-2" />
                )}
                Create Operation
              </Button>
            </CardFooter>
          </Card>
        )}
        
        {/* Operations List */}
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium">Operations</h3>
            {!showNewOperation && (
              <Button
                onClick={() => {
                  setShowNewOperation(true);
                  setEditingOperation(null);
                }}
                size="sm"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Operation
              </Button>
            )}
          </div>
          
          {operations.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No operations found. Add your first operation to get started.
            </div>
          ) : (
            <div className="space-y-4">
              {operations.map((operation) => (
                <Card 
                  key={operation.operationId}
                  className={cn(
                    editingOperation?.operationId === operation.operationId && "border-primary/50",
                    !operation.isActive && "opacity-60"
                  )}
                >
                  {editingOperation?.operationId === operation.operationId ? (
                    // Edit Mode
                    <>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg">Edit Operation</CardTitle>
                        <CardDescription>
                          Operation ID: {operation.operationId}
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor={`edit-name-${operation.operationId}`}>Display Name</Label>
                          <Input
                            id={`edit-name-${operation.operationId}`}
                            value={editingOperation.displayName}
                            onChange={(e) => handleOperationChange("displayName", e.target.value)}
                            className={formErrors.displayName ? "border-destructive" : ""}
                          />
                          {formErrors.displayName && (
                            <p className="text-xs text-destructive">{formErrors.displayName}</p>
                          )}
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor={`edit-cost-${operation.operationId}`}>Credit Cost</Label>
                          <Input
                            id={`edit-cost-${operation.operationId}`}
                            type="number"
                            min="0"
                            value={editingOperation.creditCost}
                            onChange={(e) => handleOperationChange("creditCost", parseInt(e.target.value) || 0)}
                            className={formErrors.creditCost ? "border-destructive" : ""}
                          />
                          {formErrors.creditCost && (
                            <p className="text-xs text-destructive">{formErrors.creditCost}</p>
                          )}
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor={`edit-desc-${operation.operationId}`}>Description</Label>
                          <textarea
                            id={`edit-desc-${operation.operationId}`}
                            value={editingOperation.description}
                            onChange={(e) => handleOperationChange("description", e.target.value)}
                            className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                          />
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id={`edit-active-${operation.operationId}`}
                            checked={editingOperation.isActive}
                            onChange={(e) => handleOperationChange("isActive", e.target.checked)}
                            className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                          />
                          <Label htmlFor={`edit-active-${operation.operationId}`} className="text-sm font-normal">
                            Active (available for use)
                          </Label>
                        </div>
                        
                        {formErrors.submit && (
                          <div className="text-sm text-destructive">
                            {formErrors.submit}
                          </div>
                        )}
                      </CardContent>
                      <CardFooter className="flex justify-between">
                        <Button
                          variant="ghost"
                          onClick={cancelEditing}
                        >
                          <X className="h-4 w-4 mr-2" />
                          Cancel
                        </Button>
                        <Button
                          onClick={handleSaveOperation}
                          disabled={saving}
                        >
                          {saving ? (
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          ) : (
                            <Save className="h-4 w-4 mr-2" />
                          )}
                          Save Changes
                        </Button>
                      </CardFooter>
                    </>
                  ) : (
                    // View Mode
                    <>
                      <CardHeader className="pb-3">
                        <div className="flex justify-between">
                          <div>
                            <CardTitle className="flex items-center">
                              {operation.displayName}
                              {!operation.isActive && (
                                <span className="ml-2 text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full">
                                  Inactive
                                </span>
                              )}
                            </CardTitle>
                            <CardDescription>
                              ID: {operation.operationId} | Category: {operation.category}
                            </CardDescription>
                          </div>
                          <div className="text-2xl font-bold">
                            {operation.creditCost}
                            <span className="text-xs font-normal text-muted-foreground ml-1">credits</span>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        {operation.description && (
                          <p className="text-sm text-muted-foreground mb-2">
                            {operation.description}
                          </p>
                        )}
                      </CardContent>
                      <CardFooter className="flex justify-end space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => confirmDelete("operation", operation.operationId, operation.displayName)}
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Delete
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditOperation(operation)}
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          Edit
                        </Button>
                      </CardFooter>
                    </>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Render packages tab
  const renderPackagesTab = () => {
    if (packagesLoading) {
      return renderLoading();
    }
    
    if (packagesError) {
      return renderError(packagesError);
    }
    
    return (
      <div className="space-y-6">
        {/* New Package Form */}
        {showNewPackage && (
          <Card className="border-primary/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Add New Credit Package</CardTitle>
              <CardDescription>Create a new credit package for users to purchase</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="new-package-name">Package Name *</Label>
                  <Input
                    id="new-package-name"
                    value={newPackage.name}
                    onChange={(e) => handleNewPackageChange("name", e.target.value)}
                    placeholder="e.g. Starter Pack"
                    className={formErrors.name ? "border-destructive" : ""}
                  />
                  {formErrors.name && (
                    <p className="text-xs text-destructive">{formErrors.name}</p>
                  )}
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="new-package-credits">Credit Amount *</Label>
                  <Input
                    id="new-package-credits"
                    type="number"
                    min="1"
                    value={newPackage.creditAmount}
                    onChange={(e) => handleNewPackageChange("creditAmount", parseInt(e.target.value) || 0)}
                    className={formErrors.creditAmount ? "border-destructive" : ""}
                  />
                  {formErrors.creditAmount && (
                    <p className="text-xs text-destructive">{formErrors.creditAmount}</p>
                  )}
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="new-package-price">Base Price (in cents) *</Label>
                  <Input
                    id="new-package-price"
                    type="number"
                    min="0"
                    value={newPackage.basePrice}
                    onChange={(e) => handleNewPackageChange("basePrice", parseInt(e.target.value) || 0)}
                    className={formErrors.basePrice ? "border-destructive" : ""}
                  />
                  {formErrors.basePrice && (
                    <p className="text-xs text-destructive">{formErrors.basePrice}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {formatCurrency(newPackage.basePrice / 100, newPackage.currency === 'EUR' ? '€' : '$')}
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="new-package-currency">Currency</Label>
                  <select
                    id="new-package-currency"
                    value={newPackage.currency}
                    onChange={(e) => handleNewPackageChange("currency", e.target.value)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  >
                    <option value="EUR">EUR (€)</option>
                    <option value="USD">USD ($)</option>
                    <option value="GBP">GBP (£)</option>
                  </select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="new-package-bonus">Bonus Credits</Label>
                  <Input
                    id="new-package-bonus"
                    type="number"
                    min="0"
                    value={newPackage.bonusCredits}
                    onChange={(e) => handleNewPackageChange("bonusCredits", parseInt(e.target.value) || 0)}
                    className={formErrors.bonusCredits ? "border-destructive" : ""}
                  />
                  {formErrors.bonusCredits && (
                    <p className="text-xs text-destructive">{formErrors.bonusCredits}</p>
                  )}
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="new-package-sort">Sort Order</Label>
                  <Input
                    id="new-package-sort"
                    type="number"
                    value={newPackage.sortOrder}
                    onChange={(e) => handleNewPackageChange("sortOrder", parseInt(e.target.value) || 0)}
                  />
                  <p className="text-xs text-muted-foreground">
                    Lower numbers appear first
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="new-package-description">Description</Label>
                  <textarea
                    id="new-package-description"
                    value={newPackage.description}
                    onChange={(e) => handleNewPackageChange("description", e.target.value)}
                    placeholder="Brief description of this package"
                    className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  />
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="new-package-active"
                    checked={newPackage.isActive}
                    onChange={(e) => handleNewPackageChange("isActive", e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <Label htmlFor="new-package-active" className="text-sm font-normal">
                    Active (available for purchase)
                  </Label>
                </div>
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="new-package-featured"
                    checked={newPackage.isFeatured}
                    onChange={(e) => handleNewPackageChange("isFeatured", e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <Label htmlFor="new-package-featured" className="text-sm font-normal">
                    Featured Package (highlighted)
                  </Label>
                </div>
              </div>
              
              {formErrors.submit && (
                <div className="text-sm text-destructive">
                  {formErrors.submit}
                </div>
              )}
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button
                variant="ghost"
                onClick={cancelNewItem}
              >
                <X className="h-4 w-4 mr-2" />
                Cancel
              </Button>
              <Button
                onClick={handleCreatePackage}
                disabled={saving}
              >
                {saving ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Plus className="h-4 w-4 mr-2" />
                )}
                Create Package
              </Button>
            </CardFooter>
          </Card>
        )}
        
        {/* Packages List */}
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium">Credit Packages</h3>
            {!showNewPackage && (
              <Button
                onClick={() => {
                  setShowNewPackage(true);
                  setEditingPackage(null);
                }}
                size="sm"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Package
              </Button>
            )}
          </div>
          
          {packages.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No credit packages found. Add your first package to get started.
            </div>
          ) : (
            <div className="space-y-4">
              {packages.sort((a, b) => a.sortOrder - b.sortOrder).map((pkg) => (
                <Card 
                  key={pkg._id}
                  className={cn(
                    editingPackage?._id === pkg._id && "border-primary/50",
                    !pkg.isActive && "opacity-60",
                    pkg.isFeatured && !editingPackage && "border-primary/30"
                  )}
                >
                  {editingPackage?._id === pkg._id ? (
                    // Edit Mode
                    <>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg">Edit Package</CardTitle>
                        <CardDescription>
                          Package ID: {pkg._id}
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor={`edit-name-${pkg._id}`}>Package Name</Label>
                            <Input
                              id={`edit-name-${pkg._id}`}
                              value={editingPackage.name}
                              onChange={(e) => handlePackageChange("name", e.target.value)}
                              className={formErrors.name ? "border-destructive" : ""}
                            />
                            {formErrors.name && (
                              <p className="text-xs text-destructive">{formErrors.name}</p>
                            )}
                          </div>
                          
                          <div className="space-y-2">
                            <Label htmlFor={`edit-credits-${pkg._id}`}>Credit Amount</Label>
                            <Input
                              id={`edit-credits-${pkg._id}`}
                              type="number"
                              min="1"
                              value={editingPackage.creditAmount}
                              onChange={(e) => handlePackageChange("creditAmount", parseInt(e.target.value) || 0)}
                              className={formErrors.creditAmount ? "border-destructive" : ""}
                            />
                            {formErrors.creditAmount && (
                              <p className="text-xs text-destructive">{formErrors.creditAmount}</p>
                            )}
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor={`edit-price-${pkg._id}`}>Base Price (in cents)</Label>
                            <Input
                              id={`edit-price-${pkg._id}`}
                              type="number"
                              min="0"
                              value={editingPackage.basePrice}
                              onChange={(e) => handlePackageChange("basePrice", parseInt(e.target.value) || 0)}
                              className={formErrors.basePrice ? "border-destructive" : ""}
                            />
                            {formErrors.basePrice && (
                              <p className="text-xs text-destructive">{formErrors.basePrice}</p>
                            )}
                            <p className="text-xs text-muted-foreground">
                              {formatCurrency(editingPackage.basePrice / 100, editingPackage.currency === 'EUR' ? '€' : '$')}
                            </p>
                          </div>
                          
                          <div className="space-y-2">
                            <Label htmlFor={`edit-bonus-${pkg._id}`}>Bonus Credits</Label>
                            <Input
                              id={`edit-bonus-${pkg._id}`}
                              type="number"
                              min="0"
                              value={editingPackage.bonusCredits}
                              onChange={(e) => handlePackageChange("bonusCredits", parseInt(e.target.value) || 0)}
                              className={formErrors.bonusCredits ? "border-destructive" : ""}
                            />
                            {formErrors.bonusCredits && (
                              <p className="text-xs text-destructive">{formErrors.bonusCredits}</p>
                            )}
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor={`edit-sort-${pkg._id}`}>Sort Order</Label>
                            <Input
                              id={`edit-sort-${pkg._id}`}
                              type="number"
                              value={editingPackage.sortOrder}
                              onChange={(e) => handlePackageChange("sortOrder", parseInt(e.target.value) || 0)}
                            />
                          </div>
                          
                          <div className="space-y-2">
                            <Label htmlFor={`edit-desc-${pkg._id}`}>Description</Label>
                            <textarea
                              id={`edit-desc-${pkg._id}`}
                              value={editingPackage.description}
                              onChange={(e) => handlePackageChange("description", e.target.value)}
                              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                            />
                          </div>
                        </div>
                        
                        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id={`edit-active-${pkg._id}`}
                              checked={editingPackage.isActive}
                              onChange={(e) => handlePackageChange("isActive", e.target.checked)}
                              className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                            />
                            <Label htmlFor={`edit-active-${pkg._id}`} className="text-sm font-normal">
                              Active (available for purchase)
                            </Label>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id={`edit-featured-${pkg._id}`}
                              checked={editingPackage.isFeatured}
                              onChange={(e) => handlePackageChange("isFeatured", e.target.checked)}
                              className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                            />
                            <Label htmlFor={`edit-featured-${pkg._id}`} className="text-sm font-normal">
                              Featured Package
                            </Label>
                          </div>
                        </div>
                        
                        {formErrors.submit && (
                          <div className="text-sm text-destructive">
                            {formErrors.submit}
                          </div>
                        )}
                      </CardContent>
                      <CardFooter className="flex justify-between">
                        <Button
                          variant="ghost"
                          onClick={cancelEditing}
                        >
                          <X className="h-4 w-4 mr-2" />
                          Cancel
                        </Button>
                        <Button
                          onClick={handleSavePackage}
                          disabled={saving}
                        >
                          {saving ? (
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          ) : (
                            <Save className="h-4 w-4 mr-2" />
                          )}
                          Save Changes
                        </Button>
                      </CardFooter>
                    </>
                  ) : (
                    // View Mode
                    <>
                      <CardHeader className="pb-3">
                        <div className="flex justify-between">
                          <div>
                            <CardTitle className="flex items-center">
                              {pkg.name}
                              {pkg.isFeatured && (
                                <span className="ml-2 text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">
                                  Featured
                                </span>
                              )}
                              {!pkg.isActive && (
                                <span className="ml-2 text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full">
                                  Inactive
                                </span>
                              )}
                            </CardTitle>
                            <CardDescription>
                              {formatCurrency(pkg.basePrice / 100, pkg.currency === 'EUR' ? '€' : '$')}
                              {pkg.sortOrder !== undefined && ` • Sort: ${pkg.sortOrder}`}
                            </CardDescription>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold">
                              {pkg.creditAmount}
                              <span className="text-xs font-normal text-muted-foreground ml-1">credits</span>
                            </div>
                            {pkg.bonusCredits > 0 && (
                              <div className="text-sm text-success">
                                +{pkg.bonusCredits} bonus
                              </div>
                            )}
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        {pkg.description && (
                          <p className="text-sm text-muted-foreground mb-2">
                            {pkg.description}
                          </p>
                        )}
                      </CardContent>
                      <CardFooter className="flex justify-end space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => confirmDelete("package", pkg._id, pkg.name)}
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Delete
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditPackage(pkg)}
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          Edit
                        </Button>
                      </CardFooter>
                    </>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Render delete confirmation dialog
  const renderDeleteConfirmation = () => {
    if (!deleteConfirmation.show) return null;
    
    return (
      <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div className="bg-background border rounded-lg shadow-lg max-w-md w-full p-6">
          <h3 className="text-lg font-medium mb-2">Confirm Delete</h3>
          <p className="mb-4">
            Are you sure you want to delete <strong>{deleteConfirmation.name}</strong>? This action cannot be undone.
          </p>
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={cancelDelete}
              disabled={saving}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={executeDelete}
              disabled={saving}
            >
              {saving ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4 mr-2" />
              )}
              Delete
            </Button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Ops Credits Management</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={refreshing}
        >
          {refreshing ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4 mr-2" />
          )}
          Refresh
        </Button>
      </div>
      
      {/* Tab Navigation */}
      <div className="flex border-b">
        <button
          className={cn(
            "px-4 py-2 font-medium text-sm flex items-center",
            activeTab === "operations"
              ? "border-b-2 border-primary text-primary"
              : "text-muted-foreground hover:text-foreground"
          )}
          onClick={() => handleTabChange("operations")}
        >
          <Tag className="h-4 w-4 mr-2" />
          Operation Costs
        </button>
        <button
          className={cn(
            "px-4 py-2 font-medium text-sm flex items-center",
            activeTab === "packages"
              ? "border-b-2 border-primary text-primary"
              : "text-muted-foreground hover:text-foreground"
          )}
          onClick={() => handleTabChange("packages")}
        >
          <Package className="h-4 w-4 mr-2" />
          Credit Packages
        </button>
      </div>
      
      {/* Tab Content */}
      <div>
        {activeTab === "operations" ? renderOperationsTab() : renderPackagesTab()}
      </div>
      
      {/* Delete Confirmation Dialog */}
      {renderDeleteConfirmation()}
    </div>
  );
};

export default AdminCreditControls;
