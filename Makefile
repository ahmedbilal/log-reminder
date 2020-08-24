quality:
	pylint logreminder/logreminder logreminder/reminder

black:
	black --config black.cfg logreminder

collectstatic:
	(cd logreminder && python manage.py collectstatic)
