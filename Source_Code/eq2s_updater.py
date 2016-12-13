# this module is made for download some data into local databases
from threading import Thread
import json
import requests
import sqlite3
import time


# icons crawler
def load_icons_from_dbcensus():
    sql_con = sqlite3.connect('eq2localdb.sqlite')
    sql_cmd = sql_con.cursor()
    try:
        sql_cmd.execute('create table itemicons(id integer primary key not null, icon blob not null)')
    except sqlite3.OperationalError:
        pass
    try:
        sql_cmd.execute('create table spellicons(id integer primary key not null, icon blob not null)')
    except sqlite3.OperationalError:
        pass
    try:
        sql_cmd.execute('create table achieveicons(id integer primary key not null, icon blob not null)')
    except sqlite3.OperationalError:
        pass
    sql_itemcount = int(sql_cmd.execute('select count(id) from itemicons').fetchall()[0][0])
    sql_spellcount = int(sql_cmd.execute('select count(id) from spellicons').fetchall()[0][0])
    sql_achievecount = int(sql_cmd.execute('select count(id) from achieveicons').fetchall()[0][0])

    t1 = Thread(target=icon_insert, args=(sql_itemcount, 'item', 'itemicons'))
    t1.setDaemon(True)
    t1.start()

    t2 = Thread(target=icon_insert, args=(sql_spellcount, 'spell', 'spellicons'))
    t2.setDaemon(True)
    t2.start()

    t3 = Thread(target=icon_insert, args=(sql_achievecount, 'achievement', 'achieveicons'))
    t3.setDaemon(True)
    t3.start()


    t1.join()
    t2.join()
    t3.join()

    sql_con.close()


# intend to be a thread function
def icon_insert(start, icontype, insert_table):
    sqldb = sqlite3.connect('eq2localdb.sqlite')
    sqlcmd = sqldb.cursor().execute
    while True:
        url = 'https://census.daybreakgames.com/s:fyang/img/eq2/icons/{}/{}'.format(start, icontype)
        if requests.head(url).ok:
            try_times = 1
            try:
                icon = requests.get(url).content
                icon_id = url.split('/')[-2]
                print('Downloading icon No.{}, trying {} time(s).'.format(url, try_times))
                sqlcmd('insert into {} values(?, ?)'.format(insert_table), (icon_id, sqlite3.Binary(icon)))
            except sqlite3.OperationalError as err:
                print(err)
            except ConnectionError as err:
                print(url, err)
                time.sleep(1)
                try_times += 1
            sqldb.commit()
            start += 1
        else:
            break


# alternate advancement downloader:
def aaTree_download():
    url = 'http://census.daybreakgames.com/s:fyang/get/eq2/alternateadvancement'
    start_id = 0
    end_id = 99
    aa_list = []
    while True:
        aaObj = json.loads(requests.get(url + '?c:limit=100&id=>{}&id=[{}'.format(start_id, end_id)).text)
        aa_list.extend(aaObj['alternateadvancement_list'])
        if aaObj['returned']:
            start_id += end_id
            end_id += end_id
        else:
            break
    return aa_list


def aaSpell_download():
    allAAspell = []
    allAAspellID = []
    for aacrc in aaTree_download():
        for spl in aacrc['alternateadvancementnode_list']:
            allAAspellID.append(spl['spellcrc'])
    max = len(allAAspellID)
    for n, spl in enumerate(allAAspellID):
        url = 'http://census.daybreakgames.com/s:fyang/get/eq2/spell?crc=' + str(spl) + '&c:limit=100'
        print('({}/{}) {}'.format(n + 1, max, url))
        aaSpell = []
        while True:
            try:
                aaSpell = json.loads(requests.get(url, timeout=5).text)['spell_list']
                break
            except BaseException as err:
                print(err)
                time.sleep(2)
        allAAspell.extend(aaSpell)

    crc_group = {}
    for e in allAAspell:
        crc = e.pop('crc')
        if crc in crc_group.keys():
            crc_group[crc].append(e)
        else:
            crc_group[crc] = [e, ]

    with open('crcGroupedAAspells', 'w') as f:
        f.write(json.dumps(crc_group))


def aa_insert():
    sql_con = sqlite3.connect('eq2localdb.sqlite')
    sql_cmd = sql_con.cursor()
    try:
        sql_cmd.execute('create table aaspells(id integer primary key not null, crc int not null, data text)')
    except sqlite3.OperationalError:
        pass
    with open('aaSpellDB.txt', 'r') as f:
        aas = json.loads(f.read())

    for e in aas:
        sql_cmd.execute('insert into aaspells values(?,?,?)', (e['id'], e['crc'], json.dumps[e]))

# test
if __name__ == '__main__':
    load_icons_from_dbcensus()