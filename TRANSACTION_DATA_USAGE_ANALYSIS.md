# Transaction Data Usage Analysis

## Summary
**YES**, we are actively utilizing the `transactions.json` data file throughout the application.

## Where Transaction Data is Used

### 1. **Data Loader** (`dataconnectors/json_loader.py`)
- **Method:** `get_transactions(vendor_id, status, limit)`
- **Purpose:** Load and filter invoices from transactions.json
- **Features:**
  - Filter by vendor_id
  - Filter by status (current, overdue, paid)
  - Limit results
  - Caching for performance

### 2. **Tools** (`tools/tools.py`)

#### A. Invoice Search Tools
- **`search_invoices()`** - Search invoices with optional filters
  - Calls: `json_loader.get_transactions()`
  - Returns: Filtered invoice list
  
- **`get_vendor_invoices()`** - Get all invoices for a specific vendor
  - Calls: `json_loader.get_transactions(vendor_id=vendor_id)`
  - Returns: Vendor's invoices
  
- **`get_overdue_invoices()`** - Get overdue invoices
  - Calls: `json_loader.get_transactions(status="overdue")`
  - Returns: Overdue invoices only

#### B. Time-Based Analysis Tools
- **`get_recent_invoices()`** - Get invoices from last N days
  - Calls: `json_loader.get_transactions(limit=1000)`
  - Filters by date range
  - Returns: Recent invoices with days_since_invoice
  
- **`get_vendor_outstanding_by_period()`** - Vendors with invoices in last N days
  - Calls: `json_loader.get_transactions(limit=1000)`
  - Groups by vendor
  - Calculates outstanding amounts
  - Returns: Vendor summary with totals
  
- **`get_invoices_by_date_range()`** - Invoices between specific dates
  - Calls: `json_loader.get_transactions(limit=1000)`
  - Filters by date range
  - Returns: Invoices in date range

#### C. Status Analysis Tools
- **`get_invoice_status_summary()`** - Invoice status breakdown
  - Calls: `json_loader.get_transactions(limit=1000)`
  - Groups by status
  - Calculates percentages
  - Returns: Status distribution

#### D. Aggregation Tools
- **`get_vendor_invoice_totals()`** - Total invoices by vendor
  - Calls: `json_loader.get_transactions(limit=1000)`
  - Groups by vendor
  - Calculates totals and averages
  - Returns: Vendor totals

#### E. Summary Tools
- **`get_vendor_summary()`** - Comprehensive vendor summary
  - Calls: `json_loader.get_transactions(vendor_id=vendor_id, limit=10)`
  - Returns: Recent invoices for vendor

### 3. **UI** (`streamlit_app.py`)

#### A. Dashboard Rendering
- **Line 508:** `transactions = json_loader.get_transactions()`
  - Gets all transactions for metrics calculation
  - Counts overdue invoices
  
- **Line 675:** `transactions = json_loader.get_transactions()`
  - Gets top overdue invoices for dashboard display
  - Filters for overdue status
  - Sorts by amount_due

#### B. Data Visualization
- Displays invoice details in tables
- Shows invoice status breakdown
- Renders invoice amounts in charts

## Data Fields Used from transactions.json

```json
{
  "invoice_id": "INV-2026-001",
  "vendor_id": "vend_001",
  "vendor_name": "TechSupply Solutions",
  "invoice_date": "2026-02-10T00:00:00Z",
  "due_date": "2026-03-12T00:00:00Z",
  "invoice_amount": 12000.00,
  "amount_paid": 0.00,
  "amount_due": 12000.00,
  "status": "current",
  "payment_status": "unpaid",
  "description": "Software licenses and server equipment",
  "invoice_category": "IT Equipment",
  "payment_method": "ACH",
  "days_overdue": 18
}
```

### Fields Actively Used:
- ✅ `invoice_id` - Identification
- ✅ `vendor_id` - Vendor filtering
- ✅ `vendor_name` - Display
- ✅ `invoice_date` - Date filtering and calculations
- ✅ `due_date` - Display
- ✅ `invoice_amount` - Totals and aggregations
- ✅ `amount_due` - Outstanding amount calculations
- ✅ `status` - Filtering (current, overdue, paid)
- ✅ `payment_status` - Filtering (paid, unpaid, partial)
- ✅ `invoice_category` - Categorization
- ✅ `payment_method` - Analysis
- ✅ `days_overdue` - Aging analysis

## Query Examples Using Transaction Data

### 1. "List all vendors which raised invoices in last 1 month"
- **Data Used:** transactions.json
- **Tool:** `get_vendor_outstanding_by_period(days_back=30)`
- **Process:**
  1. Load all invoices from transactions.json
  2. Filter by invoice_date (last 30 days)
  3. Group by vendor_id
  4. Calculate totals from invoice_amount and amount_due
  5. Return vendor summary

### 2. "What percentage of invoices are overdue?"
- **Data Used:** transactions.json
- **Tool:** `get_invoice_status_summary()`
- **Process:**
  1. Load all invoices from transactions.json
  2. Group by status field
  3. Count invoices per status
  4. Calculate percentages
  5. Return status distribution

### 3. "Show me invoices from the last 2 weeks"
- **Data Used:** transactions.json
- **Tool:** `get_recent_invoices(days_back=14)`
- **Process:**
  1. Load all invoices from transactions.json
  2. Filter by invoice_date (last 14 days)
  3. Calculate days_since_invoice
  4. Return recent invoices

### 4. "Show the distribution of total invoice amount for all vendors"
- **Data Used:** transactions.json
- **Tool:** `get_vendor_invoice_totals()`
- **Process:**
  1. Load all invoices from transactions.json
  2. Group by vendor_id
  3. Sum invoice_amount per vendor
  4. Calculate averages
  5. Return vendor totals

## Data Flow

```
transactions.json
    ↓
json_loader.get_transactions()
    ↓
Tools (search, filter, aggregate)
    ↓
Agent (analyze, decide visualization)
    ↓
UI (render charts and tables)
    ↓
User sees results
```

## Performance Considerations

### Current Implementation:
- **Limit:** 1000 invoices max per query
- **Caching:** Data cached in memory after first load
- **Filtering:** Done in Python (not database)
- **Aggregation:** Done in Python

### Current Data Size:
- **Invoices in transactions.json:** 44 invoices
- **Load time:** Minimal (small JSON file)
- **Memory usage:** Negligible

## Usage Statistics

### Tools Using Transaction Data:
1. `search_invoices` ✅
2. `get_vendor_invoices` ✅
3. `get_overdue_invoices` ✅
4. `get_recent_invoices` ✅
5. `get_vendor_outstanding_by_period` ✅
6. `get_invoices_by_date_range` ✅
7. `get_invoice_status_summary` ✅
8. `get_vendor_invoice_totals` ✅
9. `get_vendor_summary` ✅
10. Dashboard rendering ✅

### Total Tools Using Transaction Data: **10+**

## Conclusion

**Transaction data is heavily utilized** throughout the application:

✅ **Data Loader:** Provides access to transactions.json
✅ **Tools:** 9+ tools directly use transaction data
✅ **UI:** Dashboard and visualizations display transaction data
✅ **Agent:** Analyzes transaction data for insights
✅ **Queries:** All invoice-related queries use this data

The `transactions.json` file is one of the **core data sources** for the AR Agent, providing invoice details, amounts, dates, and status information essential for all AR analysis.

## Potential Enhancements

1. **Database Migration** - Move from JSON to database for better performance
2. **Real-time Updates** - Sync with actual accounting system
3. **More Fields** - Add payment terms, discount info, tax details
4. **Historical Data** - Archive old invoices separately
5. **Audit Trail** - Track changes to invoice data
