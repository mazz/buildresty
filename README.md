buildresty
==========
Python script that generates a database-driven RESTy web application. Based on pyramid, cornice and alembic.

Requirements:
-------------

    * Python 3.5
    * virtualenv
    * pip

Linux:
------
```
sudo apt-get install libpq-dev python-dev python3-dev
```

QUICKSTART
----------
```
cd buildresty

python buildresty.py build -d ~ -n restyapp --migrations sqlite -p /usr/local/bin/python3.5 # deploy a virtualenv called restyapp_env in your home folder

open a web browser to http://localhost:6543/tasks # empty task list

open a terminal and enter:
curl -H "Content-Type: application/json" -X POST -d \'{"description": "empty the trashcan and put the bag in the outside trashcan, dont forget to put a new bag in!", "name": "take_out_the_trash"}\' http://localhost:6543/tasks

reload web browser at http://localhost:6543/tasks # one task called take_out_the_trash
```

More Information:
-----------------
[Art & Logic](http://artandlogic.com/2014/03/cornice-and-sqlalchemy/ "Art & Logic")  
[Cornice Docs](https://cornice.readthedocs.io/en/latest/ "Cornice Docs")

