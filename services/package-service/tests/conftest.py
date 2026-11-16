import os
'''
testing the code with sqlite mimicking the postgres connection behaviour
in linux as this is being tested currently on a windows machine and the
postgres connection is not working on windows.
'''
os.environ.setdefault("DATABASE_URL", "sqlite://") 