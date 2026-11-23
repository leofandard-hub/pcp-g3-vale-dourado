-- R2 · Banco na nuvem — rodar uma vez no Supabase (SQL Editor → New query → Run)
create table if not exists lancamentos (
  id         bigserial primary key,
  tabela     text not null,              -- ex.: 15_rdo_mao_de_obra
  dados      jsonb not null,             -- a linha lançada, com as mesmas colunas do CSV
  autor      text,                       -- quem lançou (semana de campo: mínimo 3 integrantes)
  criado_em  timestamptz default now()
);

alter table lancamentos enable row level security;
create policy "leitura"  on lancamentos for select using (true);
create policy "inclusao" on lancamentos for insert with check (true);
create policy "exclusao" on lancamentos for delete using (true);

-- Acesso da chave anon pela Data API (necessário em projetos novos do Supabase)
grant select, insert, delete on lancamentos to anon;
grant usage, select on sequence lancamentos_id_seq to anon;
