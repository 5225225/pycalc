flake8 --max-line-length=99 *.py

coverage run test.py ; coverage report -m --fail-under 100
