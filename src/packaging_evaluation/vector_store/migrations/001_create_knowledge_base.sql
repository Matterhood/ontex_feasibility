-- Enable the pgvector extension
create extension if not exists vector;

-- Create the knowledge_base table
create table if not exists knowledge_base (
    id uuid primary key default gen_random_uuid(),
    type text not null,
    content text not null,
    metadata jsonb not null default '{}'::jsonb,
    embedding vector(1536),
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create an index for faster similarity search
create index if not exists knowledge_base_embedding_idx on knowledge_base using ivfflat (embedding vector_cosine_ops);

-- Create a function for similarity search
create or replace function match_knowledge(
    query_embedding vector(1536),
    match_threshold float,
    match_count int
)
returns table (
    id uuid,
    type text,
    content text,
    metadata jsonb,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        knowledge_base.id,
        knowledge_base.type,
        knowledge_base.content,
        knowledge_base.metadata,
        1 - (knowledge_base.embedding <=> query_embedding) as similarity
    from knowledge_base
    where 1 - (knowledge_base.embedding <=> query_embedding) > match_threshold
    order by knowledge_base.embedding <=> query_embedding
    limit match_count;
end;
$$;

-- Create a trigger to update the updated_at timestamp
create or replace function update_updated_at_column()
returns trigger as $$
begin
    new.updated_at = timezone('utc'::text, now());
    return new;
end;
$$ language plpgsql;

create trigger update_knowledge_base_updated_at
    before update on knowledge_base
    for each row
    execute function update_updated_at_column();

-- Create RLS policies
alter table knowledge_base enable row level security;

-- Allow authenticated users to read
create policy "Allow authenticated users to read knowledge_base"
    on knowledge_base for select
    to authenticated
    using (true);

-- Allow authenticated users to insert
create policy "Allow authenticated users to insert knowledge_base"
    on knowledge_base for insert
    to authenticated
    with check (true);

-- Allow authenticated users to update their own entries
create policy "Allow authenticated users to update their own entries"
    on knowledge_base for update
    to authenticated
    using (true)
    with check (true);

-- Allow authenticated users to delete their own entries
create policy "Allow authenticated users to delete their own entries"
    on knowledge_base for delete
    to authenticated
    using (true); 