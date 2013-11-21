#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: giorgos
# @Date:   2013-11-16 16:44:10
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-21 09:01:34
import sqlite3
import logging
import random
import string
import datetime

import netcal.utils as utils

class DB(object):

    def __init__(self, fname):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Initializing sqlite database')
        self.conn = sqlite3.connect(fname, check_same_thread=False)

        self.__create_table()


    def __create_table(self):
        self.log.debug('Creating table if not exists')
        sql = '''CREATE TABLE IF NOT EXISTS
                `appointments`
                (`uid` TEXT,
                 `datetime` DATETIME,
                 `duration` FLOAT,
                 `header`   TEXT,
                 `comment`  TEXT,
                 `last_modified` DATETIME,
                 `deleted` INTEGER)
                '''
        create_index = '''CREATE UNIQUE INDEX IF NOT EXISTS
                            uid_index ON appointments (uid)'''
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            cur.execute(create_index)
        except:
            self.log.exception('Exception creating table')
            raise
        else:
            self.conn.commit()
        finally:
            cur.close()

    def insert(self, dt, dur, he, com, uid=None, rowid=None, last_modified=None):
        if not uid:
            uid = utils.generate_random_uid()
        if not last_modified:
            last_modified = datetime.datetime.now().isoformat()
        item = {'uid': uid,
                'datetime': dt,
                'duration': dur,
                'header': he,
                'comment': com,
                'last_modified': last_modified}
        sql = '''INSERT INTO `appointments`
                (`uid`, `datetime`, `duration`, `header`,
                 `comment`, `last_modified`)
                VALUES(?, ?, ?, ?, ?, ?)'''
        print 'OK'
        params = (uid, dt, dur, he, com, last_modified)
        cur = self.conn.cursor()
        try:
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

    def get_max_timestamp(self):
        sql = '''SELECT MAX(`last_modified`) FROM
                `appointments` LIMIT 1'''
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
        except:
            self.log.exception('exception selecting max ts')
            raise
        else:
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            cur.close()

    def get_updated(self, ts):
        """returns all rows updated after ts"""
        cur = self.conn.cursor()
        sql = '''SELECT `uid`, `datetime`, `duration`, `header`, `comment`,
        `last_modified` FROM appointments'''
        params = None
        if ts:
            sql += ''' WHERE `last_modified` > ?'''
            params = (ts,)
        try:
            if params:
                cur.execute(sql, params)
            else:
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
        if not things_to_edit.get('last_modified', None):
            things_to_edit['last_modified'] = datetime.datetime.now().isoformat()
        sql = '''UPDATE `appointments`
                SET '''
        in_sql, params = [], []
        for k, v in things_to_edit.iteritems():
            in_sql.append('%s = ?' % k)
            params.append(v)
        sql += ','.join(in_sql)
        sql += ' WHERE `uid` = ?'
        params.append(uid)
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

    def delete(self, uid):
        sql = 'DELETE FROM  `appointments` WHERE `uid` = ?'
        cur = self.conn.cursor()
        try:
            cur.execute(sql, (uid,))
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
        sql = '''SELECT `uid`, `datetime`, `duration`, `header`, `comment`,
                `last_modified`
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
                item = {'uid': r[0],
                         'datetime': r[1],
                         'duration': r[2],
                         'header': r[3],
                         'comment': r[4],
                         'last_modified': r[5]}
            return item
        finally:
            cur.close()

    def get_all(self):
        sql = '''SELECT `uid`, `datetime`, `duration`, `header`, `comment`,
                `last_modified`
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
        sql = '''REPLACE INTO appointments(`uid`, `datetime`, `duration`, `header`,
                                           `comment`, `last_modified`)
                VALUES (?, ?, ?, ?, ?, ?)'''
        params = [(r['uid'], r['datetime'], r['duration'], r['header'],
                   r['comment'], r['last_modified']) for r in upd_list ]
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
            to_return.append({'uid': r[0],
                             'datetime': r[1],
                             'duration': r[2],
                             'header': r[3],
                             'comment': r[4],
                             'last_modified': r[5]})
        return to_return

if __name__ == '__main__':

    db = DB('test.db')
    dt = datetime.datetime.now().isoformat()
    dur = 1
    he = 'HALLO4'
    com = 'heys'
    #db.insert(dt, dur, he, com)

    print db.get_updated(dt)

