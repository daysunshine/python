#!/usr/bin/python3

#Oracle连通性检测timeout为2s，每2s判断一次目标Oracle网络是否连通
#如不通，则开始进行计数，每次2s，当持续3次不通则通过微信进行报警
#如检测到Oracle网络恢复，也会通过微信发送信息



import threading
import logging
from models.weixin import WeiXin
import subprocess
import datetime
from queue import Queue
from conf import admin

FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
 
class Network_Detect:
    username = admin.username #username for oracle
    password = admin.password #password for username
    lst = {}
    ip_flag = {}
    def __init__(self, counts=2, *args):
        self.event = threading.Event()
        self.dstip = args
        self.count = counts
        self.subprocess = subprocess
        self.q = Queue()
        self.wx = WeiXin()
        self.command = "/bin/bash /home/python/bin/oracle_detect_conn.sh {} {} {} {} {}"
    def startup(self):
        threading.Thread(target=self.global_queue).start()
        for i in self.dstip:
            ip,port,orcl = i.split(',')
            threading.Thread(target=self.check, args=(ip.strip(),port.strip(),orcl.strip())).start()
            self.ip_flag[ip] = True
    def global_queue(self):
        with open('/home/python/logs/detect_conn4ora.log','a+') as f:
            while True:
                if not self.q.empty():
                    f.write(self.q.get())
                    f.flush()
                self.event.wait(3)
    def ip_count(self,ip,port,orcl):
        count_num = 0
        for _ in range(self.count):
            _,ret_result = self.subprocess.getstatusoutput(self.command.format(self.username,self.password,ip,port,orcl))
            if ret_result != 'true':
                count_num += 1
            self.event.wait(2)
        if count_num == 0:
            interrupt_time = '[2~4)s'
        elif count_num == 1:
            interrupt_time = '[4~6)s'
        else:
            interrupt_time = '>6s'  
        self.q.put("{} IP:{} count={} interrupt_time:{}\n".format(" "*21,ip,count_num,interrupt_time))
        if count_num == self.count:
            self.ip_flag[ip] = False
            try:
                print("网络中断", "连接至-Oracle:{}网络中断\n中断时间:{}\n重试次数:{}".format(ip, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.count))
                #self.wx.send("网络中断", "连接至-Oracle:{}网络中断\n中断时间:{}\n重试次数:{}".format(ip, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.count))
            except Exception as e:
                logging.info(e)
    def check(self,ip,port,orcl):
        while True:
            _, ret_result = self.subprocess.getstatusoutput(self.command.format(self.username,self.password,ip,port,orcl))  # return status and result
            if self.ip_flag.get(ip) == True and ret_result == 'false':
                self.recode(ip)
                self.ip_count(ip,port,orcl)  # count
            if self.ip_flag.get(ip) == False and ret_result == 'true':
                self.recode(ip,status='recover')
                try:
                    print("网络恢复", "网络恢复Ora IP:{}\n恢复时间:{}".format(ip,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    #self.wx.send("网络恢复", "网络恢复Ora IP:{}\n恢复时间:{}".format(ip,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                except Exception as e:
                    logging.info(e)
                self.ip_flag[ip] = True
            self.event.wait(2)
    def recode(self, ip, status='down'):
        self.q.put("{} INFO {}\tMessage: The target host network is {}\n".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ip,status))
def main():
    ip = []
    with open('/home/python/conf/ip.conf','r',encoding='utf-8') as f:
        for i in f.readlines():
            if i.startswith('#'):
                continue
            else:
                ip.append(i.rstrip('\n'))
    if not ip:
        exit(1)
    net_detect = Network_Detect(2, *ip)
    net_detect.startup()
 
if __name__ == "__main__":
    main()
