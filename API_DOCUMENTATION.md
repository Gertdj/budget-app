# Finance Flow API Documentation

## Overview

The Finance Flow application now has a complete REST API built with Django REST Framework. All existing functionality is maintained, and the API provides programmatic access to all features.

## Base URL

All API endpoints are prefixed with `/api/`:
- Base URL: `http://localhost:8000/api/`

## Authentication

The API supports two authentication methods:

1. **Session Authentication** (for web browsers)
   - Uses Django's session framework
   - Automatically handled when logged in via the web interface

2. **Token Authentication** (for programmatic access)
   - Get a token: `POST /api/auth/token/`
   - Include in headers: `Authorization: Token <your-token>`

## API Endpoints

### Households

- `GET /api/households/` - List all households for the authenticated user
- `POST /api/households/` - Create a new household
- `GET /api/households/{id}/` - Get household details
- `PUT /api/households/{id}/` - Update household
- `PATCH /api/households/{id}/` - Partially update household
- `DELETE /api/households/{id}/` - Delete household

### Categories

- `GET /api/categories/` - List all categories (simplified serializer)
- `POST /api/categories/` - Create a new category
- `GET /api/categories/{id}/` - Get category details (full serializer)
- `PUT /api/categories/{id}/` - Update category
- `PATCH /api/categories/{id}/` - Partially update category
- `DELETE /api/categories/{id}/` - Delete category
- `POST /api/categories/{id}/move/` - Move category to different parent
  - Body: `{"parent_id": <id>}` or `{"parent_id": null}` for root level
- `GET /api/categories/{id}/notes/` - Get notes for a category
- `POST /api/categories/{id}/notes/` - Add a note to a category
  - Body: `{"note": "Your note text"}`

### Budgets

- `GET /api/budgets/` - List all budgets
  - Query params: `?year=2024&month=3` (optional)
- `POST /api/budgets/` - Create a new budget
- `GET /api/budgets/{id}/` - Get budget details
- `PUT /api/budgets/{id}/` - Update budget
- `PATCH /api/budgets/{id}/` - Partially update budget
- `DELETE /api/budgets/{id}/` - Delete budget
- `POST /api/budgets/update_amount/` - Update budget amount (maintains existing functionality)
  - Body: `{"category_id": <id>, "month": 3, "year": 2024, "amount": 1000.00}`
- `POST /api/budgets/{id}/toggle_payment/` - Toggle payment status
- `POST /api/budgets/open_month/` - Open/initiate a budget month
  - Body: `{"year": 2024, "month": 3}`
- `POST /api/budgets/apply_barebones/` - Apply barebones template to a month
  - Body: `{"year": 2024, "month": 3}`

### Transactions

- `GET /api/transactions/` - List all transactions
- `POST /api/transactions/` - Create a new transaction
- `GET /api/transactions/{id}/` - Get transaction details
- `PUT /api/transactions/{id}/` - Update transaction
- `PATCH /api/transactions/{id}/` - Partially update transaction
- `DELETE /api/transactions/{id}/` - Delete transaction

### Category Notes

- `GET /api/category-notes/` - List all category notes
- `POST /api/category-notes/` - Create a new note
- `GET /api/category-notes/{id}/` - Get note details
- `PUT /api/category-notes/{id}/` - Update note
- `PATCH /api/category-notes/{id}/` - Partially update note
- `DELETE /api/category-notes/{id}/` - Delete note

### Budget Templates

- `GET /api/templates/` - List all active templates
- `GET /api/templates/{id}/` - Get template details (includes categories)

### Dashboard Data

- `GET /api/dashboard/` - Get dashboard data for active month
  - Query params: `?year=2024&month=3` (optional)
  - Returns: totals, income/expense/savings breakdowns, unpaid count

### Yearly Budget Data

- `GET /api/yearly-budget/{year}/` - Get yearly budget data
  - Query params: `?month=3` (optional, for active month)
  - Returns: all categories with monthly budget amounts

### Outstanding Payments

- `GET /api/outstanding-payments/` - Get outstanding payments for current month
- `GET /api/outstanding-payments/{year}/{month}/` - Get outstanding payments for specific month
  - Returns: grouped by parent category, with totals

### Excel Exports

- `GET /api/export/yearly/{year}/` - Export yearly budget to Excel
- `GET /api/export/monthly/{year}/{month}/` - Export monthly detail to Excel
- `GET /api/export/category-summary/{year}/` - Export category summary to Excel
- `GET /api/export/transactions/` - Export all transactions to Excel
  - Query params: `?start_date=2024-01-01&end_date=2024-12-31` (optional)

## Response Formats

All endpoints return JSON by default, except Excel exports which return `.xlsx` files.

### Success Response Example

```json
{
  "id": 1,
  "name": "Groceries",
  "type": "EXPENSE",
  "household": 1,
  "is_persistent": false,
  "payment_type": "MANUAL"
}
```

### Error Response Example

```json
{
  "error": "Category not found"
}
```

## Data Isolation

All endpoints automatically filter data by the authenticated user's household. Users can only access their own household's data.

## Pagination

List endpoints are paginated with 100 items per page by default. Use query parameters:
- `?page=1` - Page number
- `?page_size=50` - Items per page

## Example Usage

### Using cURL

```bash
# Get dashboard data
curl -X GET http://localhost:8000/api/dashboard/ \
  -H "Cookie: sessionid=<your-session-id>"

# Update budget amount
curl -X POST http://localhost:8000/api/budgets/update_amount/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=<your-session-id>" \
  -d '{"category_id": 1, "month": 3, "year": 2024, "amount": 1000.00}'

# Get token for API access
curl -X POST http://localhost:8000/api/auth/token/ \
  -d "username=your_username&password=your_password"

# Use token authentication
curl -X GET http://localhost:8000/api/categories/ \
  -H "Authorization: Token <your-token>"
```

### Using JavaScript (Fetch API)

```javascript
// Get dashboard data
fetch('/api/dashboard/', {
  credentials: 'include'  // Include session cookies
})
  .then(response => response.json())
  .then(data => console.log(data));

// Update budget amount
fetch('/api/budgets/update_amount/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken()  // Get from cookie or meta tag
  },
  credentials: 'include',
  body: JSON.stringify({
    category_id: 1,
    month: 3,
    year: 2024,
    amount: 1000.00
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## Maintaining Existing Functionality

All existing Django views continue to work as before. The API is an addition, not a replacement. The web interface still uses the original views, but can now optionally use the API endpoints for AJAX requests.

## Next Steps

1. **Frontend Integration**: Update JavaScript in templates to use API endpoints for AJAX calls
2. **Mobile App**: Use the API to build a mobile application
3. **Third-party Integration**: Allow external services to access budget data via API
4. **Webhooks**: Add webhook support for budget updates

