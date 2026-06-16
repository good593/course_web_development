-- 4교시 실습 스키마 (2교시와 동일)
-- Supabase SQL Editor에서 실행합니다.

drop table if exists public.messages;
drop table if exists public.conversations;
drop table if exists public.app_users;

create table if not exists public.app_users (
  id           uuid        primary key default gen_random_uuid(),
  username     text        not null unique,
  display_name text        not null,
  created_at   timestamptz not null default now()
);

create table if not exists public.conversations (
  id         uuid        primary key default gen_random_uuid(),
  user_id    uuid        not null references public.app_users(id) on delete cascade,
  title      text        not null default '새 대화',
  created_at timestamptz not null default now()
);

create table if not exists public.messages (
  id              uuid        primary key default gen_random_uuid(),
  conversation_id uuid        not null references public.conversations(id) on delete cascade,
  role            text        not null check (role in ('user', 'assistant', 'system')),
  content         text        not null,
  created_at      timestamptz not null default now()
);

create index if not exists idx_conversations_user_id
  on public.conversations(user_id);

create index if not exists idx_messages_conversation_id_created_at
  on public.messages(conversation_id, created_at);

alter table public.app_users enable row level security;
alter table public.conversations enable row level security;
alter table public.messages enable row level security;
