#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: giorgos
# @Date:   2013-11-16 16:44:10
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-18 18:55:36
import sqlite3
import logging
import random
import string
import datetime

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
                 `last_modified` DATETIME)
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

    def _generate_random_uid(self, length=8):
        charset = string.ascii_letters + string.digits
        return ''.join(random.choice(charset) for _ in xrange(length))

    def insert(self, dt, dur, he, com):
        sql = '''INSERT INTO `appointments`
                (`uid`, `datetime`, `duration`, `header`,
                 `comment`, `last_modified`)
                VALUES(?, ?, ?, ?, ?, ?)'''

        params = (self._generate_random_uid(), dt, dur, he, com,
                  datetime.datetime.now().isoformat()
                  )
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params)
        except:
            self.log.exception('Exception inserting: %s: %s', sql, str(params))
            raise
        else:
            self.conn.commit()
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

    def update(self, uid, dt, hea, com, ):
        pass

    def delete(self, uid):
        pass

    def get_one(self, uid):
        pass

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
