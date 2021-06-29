import  socket
import  struct
import  os
ip = "192.168.1.105"
port = 8080


filepath = 'send'
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ip_port=(ip,port)
input_code_flag = 0
fileList = os.listdir(filepath)
while True:
    for files in fileList:
        filepath_current = os.path.join(filepath,files)
        if os.path.isfile(filepath_current):
            while(input_code_flag != 1):
                input_code_flag = int(input("输入'1'发送一个码元文件："))
                client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                if(client.connect_ex(ip_port) == 0):
                    print("reconnected")
                else:
                    print("reconnect fail")
            input_code_flag = 0
            fileinfo_size = struct.calcsize('128sl')
            filepath_current = os.path.join(filepath,files)
            # 定义文件头信息，包含文件名和文件大小
            fhead = struct.pack('128sl',os.path.basename(filepath_current).encode('utf-8'), os.stat(filepath_current).st_size)
            # 发送文件名称与文件大小
            client.send(fhead)
            # 将传输文件以二进制的形式分多次上传至服务器
            with open(os.path.join(filepath,files),"rb") as fp:
                while True:
                    data = fp.read(1024)
                    if not data:
                        print ('%s file send over...' % (os.path.basename(filepath)))
                        break
                    client.send(data)
                    
                # 关闭当期的套接字对象, 需等待传输完毕
                fp.close()
                #print(client.recv(1024))
                #client.close()