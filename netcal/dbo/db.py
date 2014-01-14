#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import logging
import random
import string
import datetime
import sys


import netcal.utils as utils

class DB(object):
    """This class contains methods to perform CRUD operations in an sqlite
    database"""

    def __init__(self, fname):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Initializing sqlite database')
        self.conn = sqlite3.connect(fname, check_same_thread=False)

        self.__create_table()


    def __create_table(self):
        self.log.debug('Creating table if not exists')
        sql = '''CREATE TABLE IF NOT EXISTS
                `appointments`
                (`uid` INTEGER,
                 `date` TEXT,
                 `time` TEXT,
                 `duration` TEXT,
                 `header`   TEXT,
                 `comment`  TEXT)
                '''
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
        except:
            self.log.exception('Exception creating table')
            raise
        else:
            self.conn.commit()
        finally:
            cur.close()

    def insert(self, dt,tm, dur, he, com, uid=None, rowid=None):
        item = {'uid': uid,
                'date': dt,
                'time': tm,
                'duration': dur,
                'header': he,
                'comment': com}
        sql = '''INSERT INTO `appointments`
                (`uid`, `date`, `time`, `duration`, `header`,
                 `comment`)
                VALUES(?, ?, ?, ?, ?, ?)'''
        params = (uid, dt, tm, dur, he, com)
        cur = self.conn.cursor()
        try:
            # new uid is max_id + 1
            rowsQuery = "SELECT * FROM `appointments` WHERE uid = (SELECT MAX(uid) FROM `appointments`);"
            cur.execute(rowsQuery)
            rowdata = cur.fetchone()
            if rowdata:
                maxid = rowdata[0]
                uid = int(maxid) + 1
            else:
                uid = 1
            params = (int(uid), dt, tm, dur, he, com)
            cur.execute(sql, params)
            rowid = cur.lastrowid
        except:
            self.log.exception('Exception inserting: %s: %s', sql, str(params))
            raise
        else:
            self.conn.commit()
            item['rowid'] = rowid
            return item
        finally:
            cur.close()

    def get_updated(self):
        """returns all rows updated after ts"""
        cur = self.conn.cursor()
        sql = '''SELECT `uid`, `date`, `time`, `duration`, `header`, `comment`
        FROM appointments'''
        params = None
        try:
            cur.execute(sql)
        except:
            self.log.exception('cannot get updated rows')
            raise
        else:
            to_return = self.__create_return_list(cur.fetchall())
            return to_return
        finally:
            cur.close()

    def update(self, uid, things_to_edit):
        sql = '''UPDATE `appointments`
                SET '''
        in_sql, params = [], []
        for k, v in things_to_edit.iteritems():
            in_sql.append('%s = ?' % k)
            params.append(v)
        sql += ','.join(in_sql)
        sql += ' WHERE `uid` = ?'
        params.append(int(uid))
        cur = self.conn.cursor()
        try:
            cur.execute(sql, (params))
        except:
            self.log.exception('exception while updating table: %s :%s',
                               sql, str(params))
            raise
        else:
            self.conn.commit()
            affected_rows = cur.rowcount
            self.log.debug('updated %d rows', affected_rows)
            return self.get(uid)
        finally:
            cur.close()

    def edit(self, uid, date, time, duration, header, comment):
        sql = '''UPDATE `appointments`
                SET '''
        in_sql, params = [], []
        things_to_edit = {'date': date,
                          'time': time,
                          'duration': duration,
                          'header': header,
                          'comment': comment}
        for t in things_to_edit.keys():
            if not things_to_edit[t]:
                del things_to_edit[t]
        for k, v in things_to_edit.iteritems():
            in_sql.append('%s = ?' % k)
            params.append(v)
        sql += ','.join(in_sql)
        sql += ' WHERE `uid` = ?'
        params.append(int(uid))
        cur = self.conn.cursor()
        try:
            cur.execute(sql, (params))
        except:
            self.log.exception('exception while updating table: %s :%s',
                               sql, str(params))
            raise
        else:
            self.conn.commit()
            affected_rows = cur.rowcount
            self.log.debug('updated %d rows', affected_rows)
            return self.get(uid)
        finally:
            cur.close()

    def delete_all(self):
        sql = 'DELETE FROM  `appointments`'
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
        except:
            self.log.exception('Cannot delete appointments: %s :%s',
                               sql)
            raise
        else:
            self.conn.commit()
        finally:
            cur.close()

    def delete(self, uid):
        sql = 'DELETE FROM  `appointments` WHERE `uid` = ?'
        cur = self.conn.cursor()
        try:
            cur.execute(sql, (int(uid),))
        except:
            self.log.exception('Cannot delete appointments: %s :%s',
                               sql, str(uid))
            raise
        else:
            self.conn.commit()
            deleted_rows = cur.rowcount
            return deleted_rows
        finally:
            cur.close()

    def get(self, uid=None, rowid=None):
        sql = '''SELECT `uid`, `date`, `time`, `duration`, `header`, `comment`
                FROM appointments WHERE '''
        if uid:
            sql += '`uid` = ?'
            params = (uid,)
        elif rowid:
            sql += '`rowid` = ?'
            params = (rowid,)
        else:
            self.log.error('You must provide uid or rowid!')
            raise Exception('You must provide uid or rowid!')
        cur = self.conn.cursor()
        item = None
        try:
            cur.execute(sql, (uid,))
        except:
            self.log.exception('Cannot select appointment')
            raise
        else:
            r = cur.fetchone()
            if r:
                item = {'uid': int(r[0]),
                         'date': r[1],
                         'time': r[2],
                         'duration': r[3],
                         'header': r[4],
                         'comment': r[5]}
            return item
        finally:
            cur.close()

    def get_all(self):
        sql = '''SELECT `uid`, `date`, `time`, `duration`, `header`, `comment`
                FROM appointments WHERE 1'''
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
        except:
            self.log.exception('Cannot select appointments')
            raise
        else:
            to_return = self.__create_return_list(cur.fetchall())
            return to_return
        finally:
            cur.close()

    def apply_updates(self, upd_list):
        sql = '''REPLACE INTO appointments(`uid`, `date`, `time`, `duration`, `header`,
                                           `comment`)
                VALUES (?, ?, ?, ?, ?, ?)'''
        r = upd_list
        count = len(upd_list)/6

        params = [(r[i*6], r[i*6+1], r[i*6+2], r[i*6+3], r[i*6+4],
                 r[i*6+5] ) for i in xrange(count)]

        cur = self.conn.cursor()
        try:
            cur.executemany(sql, params)
        except:
            self.log.exception('cannot apply updates')
            raise
        else:
            self.conn.commit()
        finally:
            cur.close()

    def __create_return_list(self, rows):
        to_return = []
        for r in rows:
            to_return.append({'uid': str(r[0]),
                             'date': r[1],
                             'time': r[2],
                             'duration': r[3],
                             'header': r[4],
                             'comment': r[5]})
        return to_return

if __name__ == '__main__':

    db = DB('test.db')
    dt = datetime.datetime.now().isoformat()
    dur = 1
    he = 'HALLO4'
    com = 'heys'

    print db.get_updated(dt)

