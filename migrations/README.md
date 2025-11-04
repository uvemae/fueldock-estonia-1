# Database Migrations

This folder contains SQL migration files for the FuelDock Estonia application.

## How to Apply Migrations

### Method 1: Supabase Dashboard (Easiest)

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor** in the left sidebar
3. Click **+ New Query**
4. Copy the entire contents of the migration file (e.g., `001_create_favorites_table.sql`)
5. Paste it into the query editor
6. Click **Run** to execute the migration

### Method 2: Supabase CLI (If you have it installed)

```bash
supabase db push
```

### Method 3: Using psql (Direct database connection)

If you have the database connection string:

```bash
psql "your-database-connection-string" -f migrations/001_create_favorites_table.sql
```

## Migration Files

- **001_create_favorites_table.sql** - Creates the favorites table with Row Level Security policies
  - Allows users to save favorite marinas
  - Stores personal notes and tags
  - Ensures data privacy with RLS policies
