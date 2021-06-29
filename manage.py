import pymongo
import datetime
import os
import math
import numpy as np
from scipy.fftpack import fft

# 数据库管理类
class Manage:
    def __init__(self, IP = 'localhost', port = 27017, db = 'runboo', col = 'testDB'):
        self.Client = pymongo.MongoClient(IP, port)
        self.DB = self.Client[db]
        self.Col = self.DB[col]

    # 读txt
    def read_txt(self, filename):
        sample = []
        #print(filename)
        time = filename.split("-",1)[-1].split("-",2)[0]+filename.split("-",1)[-1].split("-",2)[1]
        #print(time)
        time = datetime.datetime.strptime(time, "%Y%m%d%H%M%S")
        
        with open(filename, encoding='utf-8') as f:
            content = f.readlines()
        
        time_l = []
        sample_l = []
        channel1_l = []
        channel2_l = []
        amplitude_l = []
        frequency_l = []

        for c in content:
            c = c.split()
            sec = (int(c[0]) - 1) // 1024
            sample_l.append((int(c[0]) - 1) % 1024)
            channel1_l.append(float(c[1]))
            channel2_l.append(float(c[2]))
            amplitude_l.append(math.sqrt(float(c[1]) * float(c[1]) + float(c[2]) * float(c[2])))
            time_l.append(time + datetime.timedelta(seconds=sec))
        
        for i in range(32): # 每1024个点做FFT
            tmp = np.array(amplitude_l[i * 1024:(i + 1) *1024])
            frequency_i = list(np.log(np.abs(fft(tmp))))
            # print(frequency_i)
            frequency_l = frequency_l + frequency_i

        for i in range(32768): # 32 * 1024
            sample.append({
                "time": time_l[i],              # 采样时间
                "sample": sample_l[i],          # 采样点
                "channel1": channel1_l[i],      # 信道1
                "channel2": channel2_l[i],      # 信道2
                "amplitude": amplitude_l[i],    # 时域
                "frequency": frequency_l[i],    # 频域 取对数
            })
        self.Col.insert_many(sample)
        return sample
    
    # 读一个文件返回是否需要替换等后续操作
    # 处理替换，默认replace为否
    # 时间空窗的填补
    def read_one(self, filename, replace = False):
        
        time = filename.split("_",1)[-1].split("_",2)[0]
        
        time = datetime.datetime.strptime(time, "%Y%m%d%H%M%S")
        
        end_time = time + datetime.timedelta(seconds=32)

        # 填充时间空窗
        try:
            time1 = self.Col.find_one(
                {
                    "time": {
                        "$lt": time
                    }
                },
                sort=[("time", -1)])["time"]
            dummy = (time - time1).seconds
            tmp = []
            for i in range(1, dummy):
                for j in range(1024):
                    tmp.append({
                        "time": time1 + datetime.timedelta(seconds=i),              # 采样时间
                        "sample": j,
                        "channel1": 0,
                        "channel2": 0,
                        "amplitude": 0,
                        "frequency": 0,
                    })
            self.Col.insert_many(tmp)
        except:
            pass

        overlap = self.Col.find({"time": {
            "$gte": time,
            "$lt": end_time
        }})

        if len(list(overlap)) != 0 and not replace:
            return True
        
        if replace:
            self.Col.remove({"time": {
                "$gte": time,
                "$lt": end_time
            }})

        sample = self.read_txt(filename)

        self.Col.insert_many(sample)

        return False
    
    # 读文件列表，目前无用
    def read_many(self, filelist):
        for f in filelist:
            self.read_one(f)
    
    # 读文件夹，目前无用
    def read_folder(self, folder):
        filelist = os.listdir(folder)
        # print("total file: ", len(filelist))
        for i in range(len(filelist)):
            filelist[i] = folder + "/" + filelist[i]
        self.read_many(filelist)

    # 清空集合，调试用
    def clear_db(self):
        self.Col.remove()

    # 截取数据，开始时间->结束时间，sample排序
    def search_by_time(self, start_time, end_time):
        res = list(self.Col.find(
            {"time": {
                "$gte": start_time,
                "$lte": end_time
                }
            },
            sort=[("time", 1), ("sample", 1)]
        ))
        time = [x["time"] for x in res]
        sample = [x['sample'] for x in res]
        channel1 = [x["channel1"] for x in res]
        channel2 = [x["channel2"] for x in res]
        amplitude = [x["amplitude"] for x in res]
        return time, sample, channel1, channel2, amplitude

    # 获取数据库起止时间
    def get_db_start_end_time(self):
        try:
            db_start_time = self.Col.find_one(sort=[("time", 1)])["time"]
            db_end_time = self.Col.find_one(sort=[("time", -1)])["time"]
            return db_start_time, db_end_time
        except:
            return datetime.datetime.now(), datetime.datetime.now()
    
    # 获取brush内数据
    def get_brush_data(self, coord1, coord2):
        res = list(self.Col.find(sort=[("time", 1), ("sample", 1)]))[coord1:coord2]
        return res

# 实例化
DBManage = Manage()
