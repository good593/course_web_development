-- 07장: RLS와 서버 측 접근 제어 실습 스키마
-- Supabase SQL Editor에서 전체 파일을 실행합니다.
-- IF NOT EXISTS와 DROP POLICY IF EXISTS를 사용하므로 반복 실행할 수 있습니다.

-- ── 1. 서비스 테이블 ──────────────────────────────────────────────────

-- Supabase Auth 사용자의 서비스용 추가 정보를 저장합니다.
-- id는 기본 키이면서 auth.users(id)를 참조하므로 사용자와 프로필이 1:1로 연결됩니다.
create table if not exists public.profiles (
  -- Auth 사용자가 삭제되면 연결된 프로필도 함께 삭제됩니다.
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  display_name text not null,
  created_at timestamptz not null default now(),
  -- 현재는 생성 시각만 기본값으로 넣습니다. 자동 갱신에는 별도 트리거가 필요합니다.
  updated_at timestamptz not null default now()
);

-- 사용자별 대화방을 저장합니다.
create table if not exists public.chat_conversations (
  -- gen_random_uuid()가 대화방의 UUID를 자동으로 생성합니다.
  id uuid primary key default gen_random_uuid(),
  -- owner_id가 대화방 소유자를 나타내며 RLS 정책의 기준이 됩니다.
  owner_id uuid not null references auth.users(id) on delete cascade,
  title text not null default '새 대화',
  created_at timestamptz not null default now()
);

-- 각 대화방에 속한 메시지를 저장합니다.
create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  -- 대화방 삭제 시 해당 대화방의 메시지도 함께 삭제됩니다.
  conversation_id uuid not null references public.chat_conversations(id) on delete cascade,
  -- 메시지에도 소유자를 저장하여 사용자별 조회와 RLS 검사를 단순하게 만듭니다.
  owner_id uuid not null references auth.users(id) on delete cascade,
  -- 허용된 메시지 역할 외의 값은 DB 제약조건으로 차단합니다.
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  created_at timestamptz not null default now()
);

-- ── 2. 조회 성능을 위한 인덱스 ────────────────────────────────────────

-- 사용자별 대화방 목록 조회의 owner_id 조건을 빠르게 처리합니다.
create index if not exists idx_chat_conversations_owner_id
  on public.chat_conversations(owner_id);

-- 특정 대화방의 메시지를 생성 순서로 조회할 때 사용하는 복합 인덱스입니다.
create index if not exists idx_chat_messages_conversation_id_created_at
  on public.chat_messages(conversation_id, created_at);

-- 사용자별 메시지 조회와 owner_id 기반 RLS 검사에 사용합니다.
create index if not exists idx_chat_messages_owner_id
  on public.chat_messages(owner_id);

-- ── 3. RLS 활성화 ─────────────────────────────────────────────────────

-- RLS를 켠 뒤에는 허용 정책이 있는 작업만 anon/authenticated 역할로 수행할 수 있습니다.
-- service_role 키를 사용하는 admin_client()는 RLS를 우회하므로 서버의 소유자 필터가 필요합니다.
alter table public.profiles enable row level security;
alter table public.chat_conversations enable row level security;
alter table public.chat_messages enable row level security;

-- ── 4. profiles 정책 ──────────────────────────────────────────────────

-- 정책을 다시 생성할 수 있도록 같은 이름의 기존 정책을 먼저 제거합니다.
drop policy if exists "profiles_select_own" on public.profiles;
drop policy if exists "profiles_update_own" on public.profiles;
drop policy if exists "profiles_insert_own" on public.profiles;

-- auth.uid()는 요청 JWT의 사용자 UUID를 반환합니다.
-- USING은 SELECT처럼 기존 행을 읽을 수 있는지 검사합니다.
create policy "profiles_select_own"
on public.profiles for select
to authenticated
using ((select auth.uid()) = id);

-- WITH CHECK는 새로 입력할 행의 id가 현재 사용자 UUID와 같은지 검사합니다.
create policy "profiles_insert_own"
on public.profiles for insert
to authenticated
with check ((select auth.uid()) = id);

-- UPDATE는 기존 행 접근에 USING, 변경 결과 검증에 WITH CHECK를 모두 사용합니다.
create policy "profiles_update_own"
on public.profiles for update
to authenticated
using ((select auth.uid()) = id)
with check ((select auth.uid()) = id);

-- ── 5. chat_conversations 정책 ────────────────────────────────────────

drop policy if exists "conversations_select_own" on public.chat_conversations;
drop policy if exists "conversations_insert_own" on public.chat_conversations;
drop policy if exists "conversations_update_own" on public.chat_conversations;
drop policy if exists "conversations_delete_own" on public.chat_conversations;

-- 현재 사용자는 owner_id가 자신의 UUID인 대화방만 조회할 수 있습니다.
create policy "conversations_select_own"
on public.chat_conversations for select
to authenticated
using ((select auth.uid()) = owner_id);

-- 새 대화방의 owner_id를 다른 사용자의 UUID로 지정할 수 없습니다.
create policy "conversations_insert_own"
on public.chat_conversations for insert
to authenticated
with check ((select auth.uid()) = owner_id);

-- 자신의 대화방만 수정할 수 있고, 수정 후에도 소유자를 바꿀 수 없습니다.
create policy "conversations_update_own"
on public.chat_conversations for update
to authenticated
using ((select auth.uid()) = owner_id)
with check ((select auth.uid()) = owner_id);

-- 자신의 대화방만 삭제할 수 있습니다.
create policy "conversations_delete_own"
on public.chat_conversations for delete
to authenticated
using ((select auth.uid()) = owner_id);

-- ── 6. chat_messages 정책 ─────────────────────────────────────────────

drop policy if exists "messages_select_own" on public.chat_messages;
drop policy if exists "messages_insert_own" on public.chat_messages;

-- 현재 사용자는 owner_id가 자신의 UUID인 메시지만 조회할 수 있습니다.
create policy "messages_select_own"
on public.chat_messages for select
to authenticated
using ((select auth.uid()) = owner_id);

-- 메시지 owner_id가 현재 사용자와 같고, 대상 대화방도 현재 사용자의 소유여야 합니다.
-- EXISTS 검사가 다른 사용자의 대화방에 자신의 owner_id로 메시지를 넣는 우회를 차단합니다.
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

-- UPDATE와 DELETE 정책은 만들지 않았으므로 authenticated 사용자는 메시지를
-- 수정하거나 삭제할 수 없습니다. 필요한 기능이 생기면 별도 정책을 추가합니다.
