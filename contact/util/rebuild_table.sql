insert into contact_contactusmessage
    (id, url_refer, user_agent, name, email, 
    subject, message, open, type_of_issue, status, category, priority,
    assigned_group, source, `release`, dependencies, next_steps,
    created_at, updated_at
    )
    select
    c.id, c.url_refer, c.user_agent, c.name, c.email,
    c.subject, c.message, 1, c.type_of_issue, c.status, c.category, c.priority,
    c.assigned_group, c.source, c.release, c.dependencies, c.next_steps,
    c.created_at, c.updated_at
    from contact_temp as c;

update contact_contactusmessage set open=0 where status='C';
