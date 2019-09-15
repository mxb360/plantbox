import time, threading


# 读取文本文件
def read_file(file_name):
    try:
        f = open(file_name)
    except FileNotFoundError:
        return None
    data = f.read()
    f.close()
    return data
    
    
# 写入内容到文件
def write_file(file_name, data, t='w'):
    try:
        f = open(file_name, t)
    except FileNotFoundError:
        f = open(file_name, 'w')
    f.write(data)
    f.close()
    return 0
    
    
# 获取当前时间
def get_current_time():
    return time.strftime('[%Y-%m-%d %H:%M:%S]  '  ,time.localtime(time.time()))
    
    
# 开启一个新线程
def start_thread(_thread):
    t = threading.Thread(target=_thread)
    t.setDaemon(True)
    t.start()