-- 2교시는 1교시와 같은 스키마를 사용합니다.
-- 이미 1교시에서 실행했다면 다시 실행하지 않아도 됩니다.

create table if not exists public.app_users (
  id uuid primary key default gen_random_uuid(),
  username text not null unique,
  display_name text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.app_users(id) on delete cascade,
  title text not null default '새 대화',
  created_at timestamptz not null default now()
);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_conversations_user_id
  on public.conversations(user_id);

create index if not exists idx_messages_conversation_id_created_at
  on public.messages(conversation_id, created_at);

alter table public.app_users enable row level security;
alter table public.conversations enable row level security;
alter table public.messages enable row level security;
