INSERT INTO applications (
    id,
    job_id,
    cv_id,
    status,
    cover_letter,
    created_at
  )
VALUES (
    id:integer,
    job_id:integer,
    cv_id:integer,
    'status:character varying',
    'cover_letter:text',
    'created_at:timestamp with time zone'
  );