-- 3교시 실습 스키마: Supabase Auth 사용자와 서비스 데이터 연결
-- 1~2교시의 conversations/messages와 충돌하지 않도록 chat_ prefix를 사용합니다.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  display_name text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.chat_conversations (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  title text not null default '새 대화',
  created_at timestamptz not null default now()
);

create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.chat_conversations(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_chat_conversations_owner_id
  on public.chat_conversations(owner_id);

create index if not exists idx_chat_messages_conversation_id_created_at
  on public.chat_messages(conversation_id, created_at);

create index if not exists idx_chat_messages_owner_id
  on public.chat_messages(owner_id);

alter table public.profiles enable row level security;
alter table public.chat_conversations enable row level security;
alter table public.chat_messages enable row level security;

drop policy if exists "profiles_select_own" on public.profiles;
drop policy if exists "profiles_update_own" on public.profiles;
drop policy if exists "profiles_insert_own" on public.profiles;

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
  (select auth.uid()) = owner_id
  and exists (
    select 1
    from public.chat_conversations c
    where c.id = conversation_id
      and c.owner_id = (select auth.uid())
  )
);
