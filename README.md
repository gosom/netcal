netcal
======

simple calendar tool that allows the synchronizaton of appointments between different hosts.

It is created for the needs of the course High Perfomance Networks
University of Bonn Winter Semester 2013

Usage
======
```
python netcal_app.py
```

then an interactive shell starts with promt ==>

Use ```help``` to see the available commands:

**Netcall commands**:

1. init
2. connect
2. list
3. view
4. add
5. delete
6. edit
7. debug
8. quit

To see the options in each command use `command -h`

Here is an example:

`==>init -b localhost:12345 -d test.sqlite`

the above command start a calendar instance on localhost:port using
the database test.sqlite

`==>list`

+-----+----------+----------+--------+---------+---------------+
| uid | datetime | duration | header | comment | last_modified |
+-----+----------+----------+--------+---------+---------------+
+-----+----------+----------+--------+---------+---------------+



