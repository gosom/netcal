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
9. sync
10. quit

To see the options in each command use `command -h`

Here is an example:

`==>init -b localhost:12345 -d test.sqlite`

the above command start a calendar instance on localhost:port using
the database test.sqlite

`==>list`

You should get a table with the appointments(empty if the db is empty :) )

To connect to another node you can:
1. ``==>init -b localhost:12345 -d test.sqlite -c ip:port`
    or
2. after calling init to call the connect method `==>connect -c ip:port`

*add* command:

`==>add -h` to see help

example:
`add -t 2013-11-26 -d 2 -e "HPN exercise" -c ":)"`

if you run the list command you will see the newly inserted entry.
The entry contains a uid
*edit* command:
`edit -i uid -e "HPN 1st exercise"`

*delete* command:
`delete -i uid`

*view* command:
`view -i uid`

*sync* command:
the sync command is used to synchronize the local database with one
of the remote nodes. You should not call it manually in normal situations.
