-- 7교시 실습 스키마: Auth 사용자 프로필
-- auth.users는 Supabase가 자동 관리합니다.
-- 이번 교시는 회원가입/로그인/토큰 검증만 다루므로
-- profiles 테이블은 참고용으로만 포함합니다.
-- (실제로 사용하는 것은 8교시부터입니다)

create table if not exists public.profiles (
  id           uuid        primary key references auth.users(id) on delete cascade,
  email        text        not null,
  display_name text        not null,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

create index if not exists idx_profiles_email
  on public.profiles(email);

alter table public.profiles enable row level security;
