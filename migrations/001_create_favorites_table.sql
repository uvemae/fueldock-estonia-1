-- Create favorites table for storing user's favorite marinas
-- This table stores which marinas each user has marked as favorites
-- along with personal notes and tags

create table if not exists public.favorites (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  station_id text not null,
  name text not null,
  location text not null,
  coordinates double precision[] not null,
  station_type text,
  fuel_level int,
  capacity int,
  fuels jsonb,
  notes text,
  tags text[],
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now(),

  -- Ensure a user can't favorite the same station twice
  constraint unique_user_station unique(user_id, station_id)
);

-- Create index for faster queries by user_id
create index if not exists favorites_user_id_idx on public.favorites(user_id);

-- Create index for faster queries by station_id
create index if not exists favorites_station_id_idx on public.favorites(station_id);

-- Enable Row Level Security
alter table public.favorites enable row level security;

-- Policy: Users can view their own favorites
create policy "Users can view own favorites"
  on public.favorites
  for select
  using (auth.uid() = user_id);

-- Policy: Users can insert their own favorites
create policy "Users can insert own favorites"
  on public.favorites
  for insert
  with check (auth.uid() = user_id);

-- Policy: Users can update their own favorites
create policy "Users can update own favorites"
  on public.favorites
  for update
  using (auth.uid() = user_id);

-- Policy: Users can delete their own favorites
create policy "Users can delete own favorites"
  on public.favorites
  for delete
  using (auth.uid() = user_id);

-- Function to automatically update updated_at timestamp
create or replace function public.handle_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- Trigger to update updated_at on row update
create trigger set_updated_at
  before update on public.favorites
  for each row
  execute function public.handle_updated_at();
