# KasaDaka-Voice Service Development Kit

Pull (restore locally):
heroku pg:pull postgresql-polished-18873 kasadaka_db --app arcane-island-15098
OR
1. get dump from heroku => latest.dump
	heroku pg:backups:capture --app arcane-island-15098
	heroku pg:backups:download --app arcane-island-15098
2. drop current db 
	 dropdb -U dbadmin kasadaka_db
3. recreate db
	 createdb -U dbadmin kasadaka_db 
4. restore locally
	pg_restore --verbose -h localhost -U dbadmin -d kasadaka_db latest.dump


Push (restore on heroku):
heroku pg:reset
heroku pg:push kasadaka_db postgresql-polished-18873 --app arcane-island-15098
OR
1. get local dump
	pg_dump -Fc --no-acl --no-owner -h localhost -U dbadmin kasadaka_db > local.dump
2. import to Heroku Postgres using AWS
	https://devcenter.heroku.com/articles/heroku-postgres-import-export#restore-to-local-database

Push/pull doc:
https://devcenter.heroku.com/articles/heroku-postgresql

