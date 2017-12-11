#!/usr/bin/env python
# -*-coding:utf-8-*-
#user: tang
#date: 2017-12-11

#from zabbix_api import ZabbixAPI
import requests
import json
import sys
import time

class ZabbixMaintenance():
    def __init__(self, api_server, user, password, maintenance_name, ips, active_since, active_till):
        self.api_server = api_server
        self.user = user
        self.password = password
        self.maintenance_name = maintenance_name
        self.ips = ips
        self.hostids = []
        self.active_since = active_since
        self.active_till = active_till
    def post_data(self, method, params, auth_data=""):
        pst_data = {}
        pst_data['id'] = 1
        pst_data['jsonrpc'] = "2.0"
        pst_data['params'] = params
        pst_data['method'] = method
        if method != 'user.login':
            pst_data['auth'] = auth_data
        data_all = json.dumps(pst_data)
        headers = {'Content-Type': 'application/json',
                   'User-Agent': 'python/tang_sdk'}
        ret = requests.post(self.api_server, data=data_all, headers=headers)
        return ret
    def login(self):
        params = {'password': self.password, 'user': self.user}
        method = 'user.login'
        ret = self.post_data(method, params)
        #{"jsonrpc": "2.0", "result": "0424bd59b807674191e7d77572075f33", "id": 1}
        return json.loads(ret.text)
    def get_server_ids(self, auth_data):
        for i in self.ips:
            method = 'host.get'
            params = {"output": ["hostid"],"selectGroups": "extend",
                      "filter": {"ip": [i]}}
            ret = self.post_data(method, params, auth_data)
            host_one = json.loads(ret.text)
            #{'jsonrpc': '2.0', 'id': 1,
            # 'result': [{'groups': [{'groupid': '100100000000009', 'internal': '0', 'flags': '0', 'name': 'KE'}],
            # 'hostid': '100100000012931'}]}
            host_id_one = host_one['result'][0]['hostid']
            self.hostids.append(host_id_one)
    def create_maintenance(self, auth_data):
        params = {}
        params['name'] = self.maintenance_name #维护的名字
        start_time_sec = int(time.mktime(time.strptime(self.active_since, '%Y-%m-%d %H:%M:%S')))
        end_time_sec = int(time.mktime(time.strptime(self.active_till, '%Y-%m-%d %H:%M:%S')))
        params['active_since'] = start_time_sec #start 时间戳
        params['active_till'] = end_time_sec #stop 时间戳
        params['hostids'] = self.hostids
        #params['timeperiods'] = [{'timeperiod_type':0, 'every':1,"dayofweek":64, "start_time":64800,"period":3600}]
        params['timeperiods'] = [
            {'timeperiod_type': 0, 'start_date': start_time_sec,
             "period": end_time_sec - start_time_sec}]
        ret = self.post_data("maintenance.create", params, auth_data)
        ret_data = json.loads(ret.text)
        return ret_data
    def run(self):
        data_login = self.login() #test ok
        #{'result': 'b3d36ee03c4d5ed83d144a145b3f9d4c', 'jsonrpc': '2.0', 'id': 1}
        auth_id = data_login['result']
        print('login ok')
        self.get_server_ids(auth_id)
        print("get server ids ok")
        #print(self.hostids)
        #print(data_login)
        create_data = self.create_maintenance(auth_id)
        try:
            create_result = create_data['result']
        except Exception as e:
            print("error as \033[31m {}\033[0m".format(e))
            sys.exit(1)
        return create_data
        #print(create_data)
        #data_create_maintenance_data = self.create_maintenance(data_login['result'])



if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("\033[31m error: lost some things\033[0m")
        print("\033[31m useage: python {} {} '{}' {} {}\033[0m".format(sys.argv[0], 'maintenance_name','ip1,ip2', "start_time", "end_time"))
        print("eg: python {} 'ke_merge_20171211' '1.1.1.1,2.2.2.2' '2017-12-12 12:00:00' '2017-12-12 20:00:00'".format(sys.argv[0]))
        sys.exit(1)
    maintenance_name, ips, start_time, end_time = sys.argv[1:]
    zabbix_now = ZabbixMaintenance('https://zabbix.txxxn.com/api_jsonrpc.php',
                                   'user_name',
                                   'user_password',
                                   maintenance_name,
                                   ips.split(','),
                                   start_time,
                                   end_time)
    zabbix_now.run()
