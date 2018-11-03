#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import getopt
import time
import os
import yaml
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


need_print = True
need_stop = False
need_start = False
need_reset = False

class AliyunRequest(CommonRequest):
    def __init__(self):
        CommonRequest.__init__(self)
        self.set_domain('ecs.aliyuncs.com')
        self.set_version('2014-05-26')
        self.add_query_param('PageNumber', '1')
        self.add_query_param('PageSize', '30')

class AliyunClient:
    def __init__(self, key_id, key_secret, region_id):
        self.client = AcsClient(key_id, key_secret, region_id)

    def GetInstances(self):
        request = AliyunRequest()
        request.set_action_name('DescribeInstances')
        response = self.client.do_action_with_exception(request)
        return json.loads(response)

    def GetSysDiskIds(self):
        request = AliyunRequest()
        request.set_action_name('DescribeDisks')
        response = self.client.do_action_with_exception(request)
        return json.loads(response)

    def GetSnapShotIds(self):
        request = AliyunRequest()
        request.set_action_name('DescribeSnapshots')
        response = self.client.do_action_with_exception(request)
        return json.loads(response)

    def GetDiskByInstanceId(self, instance_id):
        request = AliyunRequest()
        request.set_action_name('DescribeDisks')
        request.add_query_param('InstanceId', instance_id)
        response = self.client.do_action_with_exception(request)
        return json.loads(response)

    def GetSnapShotByDiskId(self, disk_id):
        request = AliyunRequest()
        request.set_action_name('DescribeSnapshots')
        # 设置实例ID或者磁盘ID
        #request.add_query_param('InstanceId', '')
        request.add_query_param('DiskId', disk_id)
        response = self.client.do_action_with_exception(request)
        return json.loads(response)

    def StopInstance(self, instance_id):
        request = AliyunRequest()
        request.set_action_name('StopInstance')
        request.add_query_param('ForceStop', 'true')
        request.add_query_param('InstanceId', instance_id)
        response = self.client.do_action_with_exception(request)
        return json.loads(response)

    def StartInstance(self, instance_id):
        request = AliyunRequest()
        request.set_action_name('StartInstance')
        request.add_query_param('InstanceId', instance_id)
        response = self.client.do_action_with_exception(request)
        return json.loads(response)

    def RsetDiskBySnapShot(self, disk_id, snapshot_id):
        request = AliyunRequest()
        request.set_action_name('ResetDisk')
        request.add_query_param('DiskId',     disk_id)
        request.add_query_param('SnapshotId', snapshot_id)
        response = self.client.do_action_with_exception(request)
        return json.loads(response)


def GetConfigInstancesInfo(aliyun_client, hosts):
    instances = []
    resp = aliyun_client.GetInstances()
    for instance in resp.get('Instances').get('Instance'):
        if instance.get('InstanceName') in hosts:
            instances.append(instance)
    return instances

def GetInstanceSysDiskInfo(aliyun_client, instance_id):
    resp = aliyun_client.GetDiskByInstanceId(instance_id)
    for disk in resp.get('Disks').get('Disk'):
        if disk.get('Type') == 'system':
            return disk
    return None

def GetFilterSnapShot(aliyun_client, disk_id, filter):
    resp = aliyun_client.GetSnapShotByDiskId(disk_id)
    for ss in resp.get('Snapshots').get('Snapshot'):
        if filter in ss.get('SnapshotName'):
            return ss


def PrintResetInfo(reset_infos):
    print "Instance list:"
    if not need_print:
        return
    for info in reset_infos:
        print "  Instance[Id:%s  Name:%7s  Status:%s]   SysDiskId:%s   Snapshot[Id:%s Name:%s]" % (
            info.get('InstanceId'), info.get('InstanceName'), info.get('Status'),
            info.get('DiskId'),
            info.get('SnapshotId'), info.get('SnapshotName'))

def ProcessInstances(aliyun_client, reset_infos, wait_time):
    if need_stop or need_reset:
        print "Stop VMs:"
        for info in reset_infos:
            print "  stop instance: %s" % (info.get('InstanceId'))
            #aliyun_client.StopInstance(info.InstanceId)
    if need_start:
        time.sleep(2)
        print "Start VMs:"
        for info in reset_infos:
            print "  start instance: %s" % (info.get('InstanceId'))
            #aliyun_client.StartInstance(info.InstanceId)
    if need_reset:
        for i in range(1, wait_time):
            time.sleep(1)
            print "wait %d sec." % i
        print "Reset VMs:"
        for info in reset_infos:
            print "  reset DiskId:%s <<< SnapshotId:%s" % (info.get('DiskId'), info.get('SnapshotId'))
            #aliyun_client.RsetDiskBySnapShot(info.DiskId, info.SnapshotId)

def Usage():
    print '''Usage:
  aliyun_client.py print the vm instances which we will process.
  aliyun_client.py -h help
  aliyun_client.py -s stop the vm instances
  aliyun_client.py -r reset the vm instances'''
    exit(0)


def main():
    global need_print
    global need_stop
    global need_start
    global need_reset

    opts, args = getopt.getopt(sys.argv[1:], "hpsr", ["reset","stop","start"])
    for op, value in opts:
        if op == "-h":
            Usage()
        elif op == "-s":
            need_stop = True
        elif op == "-r":
            need_reset = True
        elif op == "--stop":
            need_stop = True
        elif op == "--start":
            need_start = True
        elif op == "--reset":
            need_stop = True
            need_reset = True

    yml_file = os.path.dirname(os.path.realpath(__file__)) + '/config.yml'
    yml = open('config.yml')
    config = yaml.load(yml)
    key_id     = config.get('key_id')
    key_secret = config.get('key_secret')
    region_id  = config.get('region_id')
    hosts      = config.get('hosts')
    filter     = config.get('filter')
    wait_time  = config.get('wait_time')

    reset_infos = []
    aliyun_client = AliyunClient(key_id, key_secret, region_id)
    instances = GetConfigInstancesInfo(aliyun_client, hosts)
    for i in instances:
        disk = GetInstanceSysDiskInfo(aliyun_client, i.get('InstanceId'))
        if disk is None:
            continue
        snapshot = GetFilterSnapShot(aliyun_client, disk.get('DiskId'), filter)
        if snapshot is None:
            continue
        reset_infos.append({'InstanceId': i.get('InstanceId'),
                            'InstanceName': i.get('InstanceName'),
                            'InstanceStatus': i.get('Status'),
                            'DiskId': disk.get('DiskId'),
                            'SnapshotId': snapshot.get('SnapshotId'),
                            'SnapshotName': snapshot.get('SnapshotName')})
    PrintResetInfo(reset_infos)
    ProcessInstances(aliyun_client, reset_infos, wait_time)

if __name__ == "__main__":
    main()
