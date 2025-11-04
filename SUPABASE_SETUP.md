# Supabase Setup Guide for FuelDock Estonia

## 1. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up / Log in
3. Click "New Project"
4. Fill in:
   - Project name: `fueldock-estonia`
   - Database password: (choose a strong password)
   - Region: Europe (closest to Estonia)
5. Wait for project to be created (~2 minutes)

## 2. Get API Credentials

1. Go to Project Settings → API
2. Copy these values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key

3. Create `.env` file in project root:
```bash
VITE_SUPABASE_URL=your_project_url_here
VITE_SUPABASE_ANON_KEY=your_anon_key_here
```

## 3. Enable Email Authentication

1. Go to Authentication → Providers
2. Enable "Email" provider
3. Configure email templates (optional):
   - Go to Authentication → Email Templates
   - Customize "Confirm Signup" template

## 4. Create Database Schema (Optional - For Future)

Currently, marina data is stored in `stations.json`. To migrate to Supabase database:

### SQL Schema

```sql
-- Create marinas table
CREATE TABLE marinas (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  location TEXT NOT NULL,
  coordinates POINT NOT NULL,
  has_station BOOLEAN DEFAULT true,
  station_type TEXT,
  fuel_level INTEGER DEFAULT 0 CHECK (fuel_level >= 0 AND fuel_level <= 100),
  capacity INTEGER DEFAULT 0,
  fuels JSONB DEFAULT '{}',
  payment TEXT[] DEFAULT ARRAY['card'],
  hours TEXT DEFAULT '24/7',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE marinas ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can read marinas (public data)
CREATE POLICY "Public marinas are viewable by everyone"
  ON marinas FOR SELECT
  USING (true);

-- Policy: Only authenticated users can see full details
CREATE POLICY "Authenticated users can view all marina details"
  ON marinas FOR SELECT
  USING (auth.role() = 'authenticated');

-- Policy: Only admins can insert/update/delete
CREATE POLICY "Admins can insert marinas"
  ON marinas FOR INSERT
  WITH CHECK (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admins can update marinas"
  ON marinas FOR UPDATE
  USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admins can delete marinas"
  ON marinas FOR DELETE
  USING (auth.jwt() ->> 'role' = 'admin');

-- Create index for location queries
CREATE INDEX marinas_location_idx ON marinas USING GIST(coordinates);
```

### Migrate Existing Data

Run this in SQL Editor after creating the table:

```sql
-- Insert your stations.json data here
-- Example:
INSERT INTO marinas (name, location, coordinates, has_station, station_type, fuel_level, capacity, fuels, payment, hours)
VALUES
  ('DIRHAMI SADAM', 'Lääne maakond', POINT(59.21003692279346, 23.49896192760152), true, 'Olerex', 23, 3000,
   '{"diesel": {"available": true, "price": 1.54}, "e95": {"available": true, "price": 1.69}, "e98": {"available": true, "price": 1.79}}'::jsonb,
   ARRAY['card', 'qr'], '24/7');
-- ... repeat for all marinas
```

## 5. Set Admin User

After creating your admin account through the app:

1. Go to Authentication → Users
2. Find your user
3. Edit user metadata:
   ```json
   {
     "role": "admin"
   }
   ```

Or set the first user email as admin in code (already configured in `useAuth.js`):
```javascript
user.email === 'admin@fueldock.ee'
```

## 6. Configure Email Settings (Production)

For production, configure SMTP settings:

1. Go to Project Settings → Auth
2. Scroll to "SMTP Settings"
3. Configure your email provider (SendGrid, Mailgun, etc.)

## 7. Security Best Practices

1. **Enable RLS** (Row Level Security) on all tables
2. **Use service_role key** only on server-side
3. **Never commit** `.env` file to git
4. **Enable MFA** for admin accounts
5. **Monitor Auth logs** regularly

## 8. Testing

1. Start dev server: `npm run dev`
2. Sign up with a test email
3. Check email for confirmation link
4. Login and test features
5. Promote user to admin via Supabase dashboard
6. Test admin panel features

## Current Implementation Status

✅ Authentication (Email + Password)
✅ User Management
✅ Admin Panel UI
✅ Marina CRUD (JSON-based)
⏳ Database Migration (optional for future)
⏳ Payment Integration (future)

## Troubleshooting

### Email confirmation not received?
- Check spam folder
- Verify SMTP settings
- Check Supabase logs

### Can't access admin panel?
- Check user metadata has `role: "admin"`
- Or set your email in `useAuth.js`

### API errors?
- Verify `.env` file exists and has correct values
- Check Supabase project is running
- Verify API keys are correct

## Next Steps

1. Deploy to production (Vercel/Netlify)
2. Set up custom domain
3. Configure production SMTP
4. Migrate marina data to database (optional)
5. Add payment integration (Stripe)
6. Set up monitoring and analytics
