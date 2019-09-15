"""
config.py
树莓派 与 阿里云服务器 的数据传输客户端的 配置文件
"""

import os

#################   阿里云服务器部分 #####################

# 阿里云服务器IP
ali_host = '120.79.12.45'

# 阿里云服务器端口号（用于网页访问）
ali_web_port = '443'

# 阿里云服务器端口号 （用于建立TCP连接）
ali_tcp_port = 51423

# 阿里云UDP端口号
ali_udp_port = 52488

# 阿里云服务器域名
#ali_url = 'http://120.79.12.45:51430'
ali_url = 'https://www.zyklql.site'

# 与阿里云交互的命令
ali_cmds = {
    'app_to_server': 'ats',          # ats：表示APP给服务器的命令
    'app_to_pi': 'atp',              # atp：表示APP给树莓派的命令
    'cmd_split': '-',                # -：命令头与命令内容的分割符

    'stop_pi_stream': 'spps',        # spps：请求停止传输图片流
    'start_pi_stream': 'stps',       # stps：请求开始传输图片流
    'get_pi_data': 'data',           # data：请求获取数据
    'get_pi_log': 'log',             # log：日志请求
    'server_ok': b'ok',              # ok：服务器正常接收到请求
    'server_error': b'err',          # err：相关请求出错
    'ali_heart': 'pi'                # pi:  阿里云服务器心跳包
}

connect_timeout = 5

###################### 摄像头部分 #############################

# 摄像头局域网URL
stream_url = 'http://192.168.1.119:8081'

# 摄像头本地URL
stream_locate_url = 'http://127.0.0.1:8081'

# 是否使用摄像头
use_camera = True

# 摄像头与树莓派客户端是否是同一个机子
same_machine = True

# 摄像头每一次发送的图片大小
img_size = 1024

###################### 客户端部分 ################################

# 数据文件目录
file_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))

#允许的最大命令长度
max_cmds_length = 50

# 存放服务器发送到树莓派的命令的文件
cmd_file = os.path.join(file_dir, 'appcmd')

# 存放要从树莓派方向服务器的数据文件
data_file = os.path.join(file_dir, 'pidata')

# 存放客户端日志的文件
log_file = os.path.join(file_dir, 'logs')

# 存放树莓派信息文件
pi_info_file = os.path.join(file_dir, 'piinfo')

# 是否存放日志
save_log = True
