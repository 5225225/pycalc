flake8 --max-line-length=99 *.py

coverage run --omit='*/site-packages/*' test.py ; coverage report -m --fail-under 100 --include="*.py"
