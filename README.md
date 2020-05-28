# KasaDaka-Voice Service Development Kit

Pull (restore locally):
heroku pg:pull postgresql-slippery-06690 kasadaka_db --app still-hollows-94505
OR
1. get dump from heroku => latest.dump
	heroku pg:backups:capture --app still-hollows-94505
	heroku pg:backups:download --app still-hollows-94505
2. drop current db 
	 dropdb -U dbadmin kasadaka_db
3. recreate db
	 createdb -U dbadmin kasadaka_db 
4. restore locally
	pg_restore --verbose -h localhost -U dbadmin -d kasadaka_db latest.dump


Push (restore on heroku):
heroku pg:reset --app still-hollows-94505
set PGUSER=dbadmin 
heroku pg:push kasadaka_db postgresql-slippery-06690 --app still-hollows-94505
OR
1. get local dump
	pg_dump -Fc --no-acl --no-owner -h localhost -U dbadmin kasadaka_db > local.dump
2. import to Heroku Postgres using AWS
	https://devcenter.heroku.com/articles/heroku-postgres-import-export#restore-to-local-database
	
	heroku pg:backups:restore "http://www.dropbox.com/s/7z1lwdhkb9rm0j6/local.dump" DATABASE_URL --app still-hollows-94505 --confirm still-hollows-94505

heroku pg:backups:info r009 --app still-hollows-94505

Push/pull doc:
https://devcenter.heroku.com/articles/heroku-postgresql

-------------------------------------MIGRATE--DB-------------------------------------

> heroku config:set  SFTP_PASS=”T:5^4[nd7SP?B2v3”
> heroku config:set  SFTP_USER=group6
> heroku config:set  SFTP_HOST=ict4d.saadittoh.com
> heroku config:set  SFTP_PORT=22
> heroku config:set  HEROKU=True

Push to Heroku: > git push heroku HEAD:master

Whenever data models changed in your project, run the following to create/update the code and the database structure:
> heroku run bash
> python manage.py showmigrations
> python manage.py makemigrations service_development
> python manage.py migrate (to run migrations)

Create superuser account
> python manage.py createsuperuser

Settings variables:
https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-MEDIA_ROOT