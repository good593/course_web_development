-- Supabase SQL Editor에서 실행하며, Redis 세션과 캐시는 이 스키마에 포함하지 않습니다.

-- Auth 사용자와 1:1로 연결되는 영구 프로필입니다.
-- Auth 사용자가 삭제되면 ON DELETE CASCADE로 프로필도 함께 삭제됩니다.
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  display_name text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 사용자가 만든 대화방의 제목과 생성 시각을 영구 보관합니다.
create table if not exists public.chat_conversations (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  title text not null default '새 대화',
  created_at timestamptz not null default now()
);

-- 전체 메시지 원본입니다. Redis recent_history는 이 테이블의 최근 N개 캐시입니다.
-- 대화방이 삭제되면 연결된 메시지도 함께 삭제됩니다.
create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.chat_conversations(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  created_at timestamptz not null default now()
);

-- 사용자별 대화방 목록 조회를 빠르게 합니다.
create index if not exists idx_chat_conversations_owner_id
  on public.chat_conversations(owner_id);

-- 특정 대화방의 전체 메시지를 생성 시각순으로 조회하는 패턴을 지원합니다.
create index if not exists idx_chat_messages_conversation_id_created_at
  on public.chat_messages(conversation_id, created_at);

-- 사용자 소유 메시지를 필터링하는 조회를 지원합니다.
create index if not exists idx_chat_messages_owner_id
  on public.chat_messages(owner_id);

-- anon/authenticated 클라이언트가 테이블에 직접 접근할 때 소유자 데이터만 허용합니다.
-- main.py의 service_role 클라이언트는 RLS를 우회하므로 코드에서도 owner_id를 검증해야 합니다.
alter table public.profiles enable row level security;
alter table public.chat_conversations enable row level security;
alter table public.chat_messages enable row level security;

-- 스크립트를 반복 실행할 수 있도록 기존 프로필 정책을 먼저 제거합니다.
drop policy if exists "profiles_select_own" on public.profiles;
drop policy if exists "profiles_insert_own" on public.profiles;
drop policy if exists "profiles_update_own" on public.profiles;

create policy "profiles_select_own"
on public.profiles for select
to authenticated
using ((select auth.uid()) = id);

create policy "profiles_insert_own"
on public.profiles for insert
to authenticated
with check ((select auth.uid()) = id);

create policy "profiles_update_own"
on public.profiles for update
to authenticated
using ((select auth.uid()) = id)
with check ((select auth.uid()) = id);

-- 대화방은 로그인 사용자가 자신의 행만 조회, 생성, 수정, 삭제할 수 있습니다.
drop policy if exists "conversations_select_own" on public.chat_conversations;
drop policy if exists "conversations_insert_own" on public.chat_conversations;
drop policy if exists "conversations_update_own" on public.chat_conversations;
drop policy if exists "conversations_delete_own" on public.chat_conversations;

create policy "conversations_select_own"
on public.chat_conversations for select
to authenticated
using ((select auth.uid()) = owner_id);

create policy "conversations_insert_own"
on public.chat_conversations for insert
to authenticated
with check ((select auth.uid()) = owner_id);

create policy "conversations_update_own"
on public.chat_conversations for update
to authenticated
using ((select auth.uid()) = owner_id)
with check ((select auth.uid()) = owner_id);

create policy "conversations_delete_own"
on public.chat_conversations for delete
to authenticated
using ((select auth.uid()) = owner_id);

-- 현재 실습 API가 사용하는 메시지 조회와 생성 권한만 정의합니다.
drop policy if exists "messages_select_own" on public.chat_messages;
drop policy if exists "messages_insert_own" on public.chat_messages;

create policy "messages_select_own"
on public.chat_messages for select
to authenticated
using ((select auth.uid()) = owner_id);

create policy "messages_insert_own"
on public.chat_messages for insert
to authenticated
with check (
  -- owner_id 변조를 막고, 해당 대화방도 같은 사용자의 소유인지 함께 확인합니다.
  (select auth.uid()) = owner_id
  and exists (
    select 1
    from public.chat_conversations c
    where c.id = conversation_id
      and c.owner_id = (select auth.uid())
  )
);
