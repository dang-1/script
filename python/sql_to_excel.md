```python
#!/usr/bin/env python
#coding:utf-8
'''
#author:tang
#date:2017-07-12
#version:1.1
#next version: none
#descriptions: exe sql to excel
'''

import datetime
import sys
try:
    import xlwt
    import pymysql
except:
    print('import error, check packages "xlwt, pymysql"')

class MysqlToExcel:
    def __init__(self):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.sql = sql
        self.excel_name = excel_name
    def conn_db(self):
        '''
        connect mysql
        execute select
        save data to excel
        '''
        excel_1 = xlwt.Workbook()
        sheet_name = excel_1.add_sheet('sheet_name')
        try:
            #connect mysql and get data
            conn = pymysql.connect(host=self.host, user=self.user, port=self.port, password=self.password, database=self.database)
            cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
            cur.execute(self.sql)
            data = cur.fetchall()

            #save data to excel
            if len(data) != 0:
                raw = list(data[0].keys())
                x = len(raw)
                y = len(data)
                for t in range(x):
                    sheet_name.write(0, t, raw[t])
                for m in range(1, y+1):
                    for n in range(x):
                        ori_data = data[m-1][raw[n]]
                        if type(ori_data) == bytes:
                            raw_data = ori_data.decode()
                        else:
                            raw_data = ori_data
                        sheet_name.write(m, n, raw_data)
        except:
            print('error')
            sys.exit(1)
        finally:
            excel_1.save(self.excel_name)
    def run(self):
        self.conn_db()

if __name__ == '__main__':
    #basic info
    sql = 'select * from mysql.user'
    user = 'root'
    database = 'mysql'
    host =  '127.0.0.1'
    password=''
    port = 3306
    file_path = '/data/django11/'

    #main exe
    now = datetime.datetime.now()
    excel_name = "{}{}_{}{}{}_{}{}{}.xls".format(file_path, database, now.year, now.month, now.day, now.hour, now.minute, now.second)
    print(excel_name)
    start = MysqlToExcel()
    start.run()




```
