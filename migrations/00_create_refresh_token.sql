create table refresh_token
(
  id         serial               not null,
  token      varchar(255)         null,
  user_id    int                  not null,
  valid      boolean default TRUE not null,
  created_at datetime             not null,

  constraint refresh_token_pk
    primary key (id)
);