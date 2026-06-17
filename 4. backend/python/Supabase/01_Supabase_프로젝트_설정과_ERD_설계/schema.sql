-- 실습 스키마: 사용자 - 대화 - 메시지
-- Supabase SQL Editor에서 실행합니다.

-- 기존 테이블이 있으면 삭제 (FK 참조 역순)
drop table if exists public.messages;
drop table if exists public.conversations;
drop table if exists public.app_users;

-- 사용자 테이블
create table if not exists public.app_users (
  id           uuid        primary key default gen_random_uuid(),
  username     text        not null unique,
  display_name text        not null,
  created_at   timestamptz not null default now()
);

-- 대화 테이블
create table if not exists public.conversations (
  id         uuid        primary key default gen_random_uuid(),
  user_id    uuid        not null references public.app_users(id) on delete cascade,
  title      text        not null default '새 대화',
  created_at timestamptz not null default now()
);

-- 메시지 테이블
create table if not exists public.messages (
  id              uuid        primary key default gen_random_uuid(),
  conversation_id uuid        not null references public.conversations(id) on delete cascade,
  role            text        not null check (role in ('user', 'assistant', 'system')),
  content         text        not null,
  created_at      timestamptz not null default now()
);

-- 조회 성능을 위한 인덱스
create index if not exists idx_conversations_user_id
  on public.conversations(user_id);

create index if not exists idx_messages_conversation_id_created_at
  on public.messages(conversation_id, created_at);

-- RLS 활성화 (service_role로만 접근)
alter table public.app_users enable row level security;
alter table public.conversations enable row level security;
alter table public.messages enable row level security;
