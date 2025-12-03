# How to Access Your Previous Data

## Current Status

Your previous budget data has been preserved in the **"Default Household"**:
- **103 categories** (your original categories)
- **47 budgets** (your budget entries)
- **All transactions** (if any)

## Option 1: Transfer Data to Your User Account (Recommended)

### Step 1: Create Your User Account

If you haven't already, register your account:
1. Go to `http://localhost:8000/register/`
2. Create your account with your preferred username and password

### Step 2: Transfer Your Data

Run the transfer command:

```bash
docker-compose exec web python manage.py transfer_data_to_user <your_username>
```

For example, if your username is "gert":
```bash
docker-compose exec web python manage.py transfer_data_to_user gert
```

This will:
- Move all your categories to your household
- Move all your budgets (automatically, through categories)
- Move all your transactions
- You can optionally delete the Default Household after transfer

### Step 3: Login and Verify

1. Login with your account at `http://localhost:8000/login/`
2. Go to Dashboard - you should see all your original categories
3. Go to Budget page - you should see all your budget entries

## Option 2: Access via Default User Account

### Step 1: Login as Default User

The default user account was created during migration:
- **Username**: `default_user`
- **Password**: `changeme` (⚠️ **CHANGE THIS IMMEDIATELY**)

1. Go to `http://localhost:8000/login/`
2. Login with `default_user` / `changeme`
3. You'll see all your original data

### Step 2: Change Password (IMPORTANT)

After logging in, change the password immediately:
1. Go to Django Admin: `http://localhost:8000/admin/`
2. Go to Users → `default_user`
3. Change the password

Or use the command line:
```bash
docker-compose exec web python manage.py changepassword default_user
```

## Option 3: Use Django Admin to Transfer

If you prefer a GUI approach:

1. **Login to Admin**: `http://localhost:8000/admin/`
   - You'll need a superuser account (create one if needed: `python manage.py createsuperuser`)

2. **Transfer Categories**:
   - Go to Finance → Categories
   - Filter by Household: "Default Household"
   - Select all categories
   - Use "Bulk edit" or change household field to your user's household

3. **Transfer Transactions**:
   - Go to Finance → Transactions
   - Filter by Household: "Default Household"
   - Select all transactions
   - Change household to your user's household

## Verify Your Data

After transfer, verify everything is correct:

```bash
docker-compose exec web python manage.py shell
```

Then in the shell:
```python
from finance.models import Category, Budget, Household
from django.contrib.auth.models import User

# Get your user
user = User.objects.get(username='<your_username>')
household = user.households.first()

# Check counts
print(f"Categories: {Category.objects.filter(household=household).count()}")
print(f"Budgets: {Budget.objects.filter(category__household=household).count()}")
```

## Important Notes

1. **Data Safety**: Your original data is safe in the Default Household until you transfer it
2. **Base Template**: If you transfer data to a new account, the base template won't be applied (since you already have categories)
3. **Multiple Users**: If you want to share the data with another user, add them to your household in Django Admin
4. **Backup**: Consider backing up your database before making changes:
   ```bash
   docker-compose exec web python manage.py dumpdata finance > backup.json
   ```

## Quick Transfer Command

The easiest way is to use the transfer command:

```bash
# Replace 'your_username' with your actual username
docker-compose exec web python manage.py transfer_data_to_user your_username
```

The command will:
- Show you what will be transferred
- Ask for confirmation
- Transfer all your data
- Optionally delete the Default Household

## Troubleshooting

### "User does not exist"
- Make sure you've registered your account first
- Check the username is correct (case-sensitive)

### "No data to transfer"
- Your data might already be transferred
- Check if Default Household still has categories

### "Can't see my data after transfer"
- Make sure you're logged in with the correct account
- Check that the household has the correct member
- Verify in Django Admin that categories are in your household

## Need Help?

If you encounter any issues:
1. Check the Django Admin to see where your data is
2. Verify your user account exists and has a household
3. Check the transfer command output for any errors

