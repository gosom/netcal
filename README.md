Introduction
============

simple command line calendar tool that allows the synchronizaton of appointments between different hosts.
It uses XML-RPC protocol for communication between different hosts.

It is created for the needs of the course High Perfomance Networks
University of Bonn Winter Semester 2013.

Requirements
============

python 2.7

md2 with the provided patch (cmd2.patch), because of the bug :
https://bitbucket.org/catherinedevlin/cmd2/issue/9/fix-for-issue-8

pyparsing

prettytable

For convenience I have included the above modules in the project.

It is tested on Linux i686 using python 2.7.5 .

! It is not compatible with python 3 !

Usage
============
```
python netcal_app.py
```

then an interactive shell starts with promt ==>

Use

`help`

to see the available commands:

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
11. help

To see the options in each command use `<command> -h`

Here is an example:

`==>init -b localhost:12345 -d test.sqlite`

the above command start a calendar instance on localhost:port using
the database test.sqlite

`==>list`

You should get a table with the appointments(empty if the db is empty :) )

To connect to another node you can:

``==>init -b localhost:12345 -d test.sqlite -c ip:port`

    or

after calling init to call the connect method `==>connect -c ip:port`

**add** command:

`==>add -h` to see help

example:

`add -t 2013-11-26 -d 2 -e "HPN exercise" -c ":)"`

if you run the list command you will see the newly inserted entry.
The entry contains a uid

**edit** command:

`edit -i uid -e "HPN 1st exercise"`

**delete** command:

`delete -i uid`

**view** command:

`view -i uid`

**sync** command:

the sync command is used to synchronize the local database with one
of the remote nodes. You should not call it manually in normal situations.


XML-RPC methods
============

Look at the module netcal.srv.service at class NetCalService.

All the methods here (except __init__ ) are exposed via xml-rpc.

See docs/method_signatures for the xml-rpc requests needed to invoke these
methods.

A convenient way to check the xmlrpc server responses (for debugging) is to
post the xml requests.

Look at tests/manual_xmlrpc.py to see how to do it python.
```python
import sys
import requests


data = sys.stdin.read()
url = sys.argv[1]
try:
    r = requests.post(url, data=data)
except Exception as e:
    print >> sys.stderr, str(e)

print r.text
```

Here is the response:

```xml
<?xml version='1.0'?>
<methodResponse>
<params>
<param>
<value><array><data>
<value><string>localhost:12345</string></value>
</data></array></value>
</param>
</params>
</methodResponse>
```
