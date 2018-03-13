#!/usr/bin/env python
#coding: utf-8
#date: 2018-03-09
#author: tang
#python version: 3.x

'''
eg: config.json
{
"zabbix_api_server": "123",
"zabbix_api_server_old": "https://zabbix.***.com/api_jsonrpc.php",
"user_name": "tangjianming",
"user_password": "***"
}



'''

import argparse
import sys
import json
import requests
import time
import datetime
import os

zabbix_config = '/Users/tangjianming/config.json'

def print_help():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("useage: ")
    # create maintenance by ip
    print(
        "    eg: python {0} --ip 1.21.1.1,2.2.2.2 -n 'maintenance name' -s '{1}' -e '{1}'".format(sys.argv[0], now))
    # list goroup_name and group_id
    print("    eg: python {} -g".format(sys.argv[0]))
    # create maintenance by name
    print("    eg: python {0} -p ke -n 'maintenance_name' -s '{1}' -e '{1}'".format(sys.argv[0], now))
    # list maintenance name
    print("    eg: python {} -l".format(sys.argv[0]))
    # delete maintenance by maintenance id
    print("    eg: python {} -d maintenance_id".format(sys.argv[0]))
    sys.exit(1)

class ZabbixMaintenance:
    def __init__(self,api_server, user_name, password, maintenance_name=None, ip=None, get_project=None, project=None, start_time=None, end_time=None, list_m=None, delete_m=None):
        self.api_server = api_server
        self.user_name = user_name
        self.password = password
        self.ip = ip
        self.get_project = get_project
        self.project = project
        self.start_time = start_time
        self.end_time = end_time
        self.list_m = list_m
        self.delete_m = delete_m
        self.maintenance_name = maintenance_name
        self.hostids = []

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
        #print(json.dumps(pst_data, indent=2))
        ret = requests.post(self.api_server, data=data_all, headers=headers)
        return ret

    def login(self):
        params = {'password': self.password, 'user': self.user_name}
        method = 'user.login'
        ret = self.post_data(method, params)
        #{"jsonrpc": "2.0", "result": "0424bd59b807674191e7d77572075f33", "id": 1}
        return json.loads(ret.text)

    def get_server_ids(self, auth_data):
        for i in self.ip.split(','):
            method = 'host.get'
            params = {"output": ["hostid"],"selectGroups": "extend",
                      "filter": {"ip": [i]}}
            ret = self.post_data(method, params, auth_data)
            host_one = json.loads(ret.text)
            #{'jsonrpc': '2.0', 'id': 1,
            # 'result': [{'groups': [{'groupid': '100100000000009', 'internal': '0', 'flags': '0', 'name': 'KE'}],
            # 'hostid': '100100000012931'}]}
            #print(host_one['result'])
            host_id_one = host_one['result'][0]['hostid']
            self.hostids.append(host_id_one)

    def ip_maintenance(self, auth_data):
        params = {}
        params['name'] = self.maintenance_name  # 维护的名字
        start_time_sec = int(time.mktime(time.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')))
        end_time_sec = int(time.mktime(time.strptime(self.end_time, '%Y-%m-%d %H:%M:%S')))
        params['active_since'] = start_time_sec  # start 时间戳
        params['active_till'] = end_time_sec  # stop 时间戳
        params['hostids'] = self.hostids
        # params['timeperiods'] = [{'timeperiod_type':0, 'every':1,"dayofweek":64, "start_time":64800,"period":3600}]
        params['timeperiods'] = [
            {'timeperiod_type': 0, 'start_date': start_time_sec,
             "period": end_time_sec - start_time_sec}]
        ret = self.post_data("maintenance.create", params, auth_data)
        ret_data = json.loads(ret.text)
        #print(ret_data)
        try:
            create_result = ret_data['result']
        except Exception as e:
            print("error as \033[31m {}\033[0m".format(e))
            sys.exit(1)
        print('create maintenance {} ok'.format(self.maintenance_name))
        #return ret_data

    def get_group(self, auth_data):
        params = {}
        params['output'] = ['name', 'groupids']
        ret = self.post_data("hostgroup.get", params, auth_data)
        ret_data = json.loads(ret.text)
        group_data = ret_data['result']
        print('{} {}'.format('group_name'.ljust(25), 'group_id'.ljust(25)))
        for x in group_data:
            print('{} {}'.format(x['name'].ljust(25), x['groupid'].ljust(25)))
        #print(ret_data)

    def project_maintenance(self, auth_data):
        params = {}
        params['name'] = self.maintenance_name  # 维护的名字
        start_time_sec = int(time.mktime(time.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')))
        end_time_sec = int(time.mktime(time.strptime(self.end_time, '%Y-%m-%d %H:%M:%S')))
        params['active_since'] = start_time_sec  # start 时间戳
        params['active_till'] = end_time_sec  # stop 时间戳
        params['groupids'] = self.project.split(',')
        # params['timeperiods'] = [{'timeperiod_type':0, 'every':1,"dayofweek":64, "start_time":64800,"period":3600}]
        params['timeperiods'] = [
            {'timeperiod_type': 0, 'start_date': start_time_sec,
             "period": end_time_sec - start_time_sec}]
        ret = self.post_data("maintenance.create", params, auth_data)
        ret_data = json.loads(ret.text)
        print(ret_data)
        try:
            create_result = ret_data['result']
        except Exception as e:
            print("error as \033[31m {}\033[0m".format(e))
            sys.exit(1)
        print('create maintenance {} ok'.format(self.maintenance_name))

    def list_maintenance(self, auth_data): #test ok
        '''
        according to auth_id get maintenance,
        and print active maintenance
        :param auth_data:
        :return:
        '''
        params = {}
        params['output'] = "extend"
        params['selectGroups'] = 'extend'
        params['selectTimeperiods'] = 'extend'
        ret = self.post_data("maintenance.get", params, auth_data)
        ret_data = json.loads(ret.text)
        #print(ret_data)
        #print(json.dumps(ret_data, indent=2))
        local_timestamp = time.time()
        print('{} {} {} {}'.format('maintenance_name'.ljust(30), 'maintenance_id'.ljust(20),
                                   'start_time'.ljust(25), 'end_time'.ljust(25)))
        for x in ret_data['result']:
            #timpstamp -> local time #time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int('1510894800')))
            maintenance_name = x['name']
            maintenance_id = x['maintenanceid']
            maintenance_start_time = x['active_since']
            maintenance_end_time = x['active_till']
            if float(maintenance_end_time) > float(local_timestamp):
                print('{} {} {} {}'.format(maintenance_name.ljust(30), maintenance_id.ljust(20),
                                        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(maintenance_start_time))).ljust(25),
                                        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(maintenance_end_time))).ljust(25)))
        #return ret_data
    def delete_maintenance(self, auth_data, maintenance_id): #test ok
        params = [ x for x in maintenance_id.split(",") ]
        ret = self.post_data("maintenance.delete", params, auth_data)
        ret_data = json.loads(ret.text)
        try:
            return_result = ret_data['result']['maintenanceids']
        except:
            print("delete {} return error".format(maintenance_id))
            sys.exit(1)
        for x in maintenance_id.split(','):
            if x in return_result:
                print('delete {} ok'.format(x))
            else:
                print('delete {} error'.format(x))

    def run(self):
        data_login = self.login()  # test ok
        # {'result': 'b3d36ee03c4d5ed83d144a145b3f9d4c', 'jsonrpc': '2.0', 'id': 1}
        #print(data_login)
        auth_id = data_login['result']
        #print(self.ip, self.start_time, self.end_time, self.get_project, self.maintenance_name, self.project, self.list_m, self.delete_m)
        print('login ok')
        if self.ip and not self.project and self.maintenance_name and self.start_time and self.end_time and not self.get_project and not self.list_m and not self.delete_m:
            print('will create maintenance by ip')
            self.get_server_ids(auth_id)
            self.ip_maintenance(auth_id)
        elif not self.ip and not self.project and not self.maintenance_name and not self.start_time and not self.end_time and self.get_project and not self.list_m and not self.delete_m:
            print('get project name')
            self.get_group(auth_id)
        elif not self.ip and self.project and self.maintenance_name and self.start_time and self.end_time and not self.get_project and not self.list_m and not self.delete_m:
            print('will create maintenance by group id')
            self.project_maintenance(auth_id)
        elif not self.ip and not self.project and not self.maintenance_name and not self.start_time and not self.end_time and not self.get_project and self.list_m and not self.delete_m:
            print('list maintenance_name and maintenance_id')
            self.list_maintenance(auth_id)
        elif not self.ip and not self.project and not self.maintenance_name and not self.start_time and not self.end_time and not self.get_project and not self.list_m and self.delete_m:
            print('delete maintenance by maintenance_id')
            self.delete_maintenance(auth_id, self.delete_m)
        else:
            print_help()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', dest='ip', type=str, help='give some ip eg: 1.1.1.1,2.2.2.2')
    parser.add_argument('-g', '--getgroup', action='store_true', help='display maintenance')
    parser.add_argument('-p', '--project', dest='project', type=str, help='give some project eg: ke')
    parser.add_argument('-n', '--maintenance-name', dest='maintenance_name', type=str, help='give some project eg: ke')
    parser.add_argument('-s', '--start-time', dest='start_time', type=str, help='maintenance start time')
    parser.add_argument('-e', '--end-time', dest='end_time', type=str, help='maintenance end time')
    parser.add_argument('-l', '--list', action='store_true', help='display maintenance')
    parser.add_argument('-d', '--delete', dest='delete_m', type=str, help='delete maintenance name')
    args = parser.parse_args()

    #print(args)
    #print(args.ip)
    #print(args.project)
    #print(args.start_time)
    #print(args.end_time)
    #print(args.list)
    #print(args.delete_m)
    #print(args.maintenance_name)
    #print('-----')
    #if not args.ip:
    #   print('eee')
    #
    #if args.ip and args.start_time and args.end_time and not args.list and not args.project and not args.delete_m:
    #    print('ip')
    #elif args.project and args.start_time and args.end_time and not args.ip and not args.list and not args.delete_m:
    #    print('project')
    #elif args.list and not args.ip and not args.start_time and not args.end_time and not args.project and not args.delete_m:
    #    print('list')
    #elif args.delete_m and not args.ip and not args.start_time and not args.end_time and not args.list and not args.project:
    #    print('delete')
    if len(sys.argv) == 1:
        print_help()
    if os.path.exists(zabbix_config):
        with open(zabbix_config, 'r') as f:
            zabbix_info = json.load(f)
    else:
        print("{} does not exist".format(zabbix_config))
        sys.exit(1)
    zabbix_api_server = zabbix_info['zabbix_api_server_old']
    zabbix_user_name = zabbix_info['user_name']
    zabbix_user_password = zabbix_info['user_password']

    maintenance = ZabbixMaintenance(api_server = zabbix_api_server,
                                    user_name  = zabbix_user_name,
                                    password   = zabbix_user_password,
                                    maintenance_name = args.maintenance_name,
                                    ip         = args.ip,
                                    get_project= args.getgroup,
                                    project    = args.project,
                                    start_time = args.start_time,
                                    end_time   = args.end_time,
                                    list_m     = args.list,
                                    delete_m   = args.delete_m)
