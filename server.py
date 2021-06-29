import socket
import random
import  pymongo
import  struct
import  os
from manage import DBManage


sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ip_port = ("192.168.1.112", 8080)
sk.bind(ip_port)
sk.listen(5)
i = 0
while True:
    print("正在进行等待接受数据...")
    conn, address = sk.accept()
    # 申请相同大小的空间存放发送过来的文件名与文件大小信息Z
    fileinfo_size = struct.calcsize('128sl')
    buf1 = conn.recv(fileinfo_size)
    #print(len(buf1))
    buf2 = conn.recv(fileinfo_size-len(buf1))
    buf = buf1 + buf2
    #print(fileinfo_size)
    #print(buf)
    if buf:
         # 获取文件名和文件大小
        filename, filesize = struct.unpack('128sl', buf)
        print(filesize)
        fn = filename.strip(b'\00')
        fn = fn.decode()
        recvd_size = 0  # 定义已接收文件的大小
        # 存储在该脚本所在目录下面
        #fp = open('./receive/' + str(fn), 'wb')
        fp = open(str(fn), 'wb') 
        while not recvd_size == filesize:
            if filesize - recvd_size > 1024:
                    data,address_client = conn.recvfrom(1024)
                    recvd_size += len(data)
                    print(len(data))
            else:
                data,address_client = conn.recvfrom(filesize - recvd_size)
                recvd_size = filesize
            fp.write(data)
            #i+=1
            #print(len(data))
            #print(i)
        fp.close()   
        print ('end receive...') 
        DBManage.read_txt(str(fn))
        os.remove(str(fn))
        conn.close()