# Migration Guide: Username to Email Authentication

This guide will help you migrate from username-based authentication to email-based authentication.

## ⚠️ Important Warnings

1. **This is a breaking change** - All existing users will need to use their email address to log in
2. **Backup your database** before proceeding
3. **Test in a development environment first**
4. **Existing users without email addresses** will get placeholder emails that need to be updated

## Prerequisites

- Django 5.2+
- Database backup completed
- All code changes have been committed

## Step-by-Step Migration Process

### Step 1: Create Database Migrations

Django will automatically detect the custom User model and create the necessary migrations:

```bash
python manage.py makemigrations finance
```

This will create a migration file (likely `0014_custom_user_model.py`) that:
- Creates the new custom User model
- Migrates data from the old `auth_user` table to the new `finance_user` table
- Updates all foreign key relationships

### Step 2: Review the Migration

**IMPORTANT**: Before running the migration, review the generated migration file to ensure it looks correct.

The migration should:
- Create the `finance_user` table
- Copy data from `auth_user` to `finance_user`
- Update all foreign keys to point to the new table

### Step 3: Run the Migration

```bash
python manage.py migrate
```

**Note**: This may take some time if you have many users or a large database.

### Step 4: Migrate User Data to Email

After the database migration is complete, run the data migration command:

```bash
# First, preview what will change (recommended)
python manage.py migrate_to_email_auth --dry-run

# Then apply the changes
python manage.py migrate_to_email_auth
```

This command will:
- Check all users for email addresses
- If username is already a valid email, use it
- If username is not an email, create `username@migrated.local`
- If no username exists, create `user_ID@migrated.local`
- Handle email conflicts automatically

### Step 5: Verify Migration

1. **Check that all users have emails**:
   ```bash
   python manage.py shell
   ```
   ```python
   from finance.models import User
   users_without_email = User.objects.filter(email__isnull=True) | User.objects.filter(email='')
   print(f"Users without email: {users_without_email.count()}")
   ```

2. **Test login with email**:
   - Try logging in with an existing user's email address
   - Verify authentication works

3. **Check admin panel**:
   - Go to `/admin/`
   - Verify users are displayed correctly
   - Check that email is shown as the primary identifier

### Step 6: Update User Email Addresses

Users with `@migrated.local` emails need to update their email addresses:

1. **Option A**: Users can update via the application (if you add a profile edit feature)
2. **Option B**: Admin can update via Django admin panel
3. **Option C**: Run a script to update emails in bulk

## Troubleshooting

### Issue: Migration fails with "table already exists"

**Solution**: You may have already run the migration. Check your migration status:
```bash
python manage.py showmigrations finance
```

### Issue: Users can't log in after migration

**Possible causes**:
1. User's email wasn't set correctly
2. User is trying to use old username instead of email

**Solution**:
- Check user's email in admin: `/admin/finance/user/`
- User should log in with their email address, not username
- If email is `@migrated.local`, they need to update it first

### Issue: Email conflicts during migration

**Solution**: The migration script automatically handles conflicts by adding user ID:
- If `user@example.com` conflicts, it becomes `user_123@migrated.local`

### Issue: Foreign key constraint errors

**Solution**: This shouldn't happen if migrations are run in order, but if it does:
1. Check that all migrations are applied: `python manage.py migrate`
2. Verify foreign keys in the database
3. You may need to manually fix foreign key references

## Rollback Plan

If you need to rollback (not recommended after users start using email):

1. **Restore database backup**
2. **Revert code changes** (remove custom User model, revert AUTH_USER_MODEL)
3. **Run migrations again**

**Note**: Rollback is complex and may cause data loss. Always test in development first.

## Post-Migration Tasks

1. **Notify users** about the change:
   - They now log in with email instead of username
   - Users with `@migrated.local` emails need to update their email

2. **Update documentation**:
   - Update any user guides or help documentation
   - Update API documentation if applicable

3. **Monitor for issues**:
   - Check error logs for authentication failures
   - Monitor user feedback

## Verification Checklist

- [ ] Database backup completed
- [ ] Migrations created successfully
- [ ] Migrations applied successfully
- [ ] Data migration command run successfully
- [ ] All users have email addresses
- [ ] Login works with email addresses
- [ ] Admin panel shows users correctly
- [ ] Existing functionality still works
- [ ] New user registration works with email
- [ ] Users notified about the change

## Support

If you encounter issues during migration:
1. Check Django migration documentation
2. Review error messages carefully
3. Check database constraints
4. Verify all code changes are correct

