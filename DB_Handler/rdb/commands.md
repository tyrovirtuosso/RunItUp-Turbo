# To run postgres in mac

brew services run postgresql

# To stop postgres in mac

brew services stop postgresql

# To Connect to the PostgreSQL server

psql postgres

# To get usernames

SELECT u.usename AS "User Name" FROM pg_catalog.pg_user u;
or
\du

# To get databases

\l
