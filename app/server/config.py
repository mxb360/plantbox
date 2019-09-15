import os

#################   阿里云服务器部分 #####################

# 阿里云服务器端口号 （用于建立TCP连接）
ali_tcp_port = 51423

# 阿里云Python脚本测试端口
ali_tcp_py_port = 51428

# 阿里云UDP端口
ali_udp_port = 52488


# 与阿里云交互的命令
cmds = {
    # 命令头：区分各种命令的标记符
    'app_to_server': 'ats',          # ats：表示APP给服务器的命令
    'app_to_pi': 'atp',              # atp：表示APP给树莓派的命令
    'debug': 'd',                    # d：测试信息（Python脚本保留）
    'cmd_split': '-',                # -：命令头与命令内容的分割符
    'data_split': ':',               # :：命令与数据的分隔符
    'id_pwd_split': '+',             # +：用户名与密码的分隔符
    # DeBug
    'server_info': 'inf',            # inf: 获取服务器信息
    'server_log': 'slog',            # slog：获取服务器日志
    'pi_log': 'plog',                # plog：获得树莓派日志
    'user_info': 'uinf',             # uinf：获取用户信息
    'online_users': 'ou',            # ou： 获取在线的用户
    # APP发向服务器的命令
    'data': 'data',                  # data：请求获取数据
    'sigin_out': 'so',               # so:  APP登出
    'user_sign_up': 'usp',           # usp：用户注册
    'user_sign_in': 'usi',           # usi：用户登录
    'user_sign_out': 'uso',          # uso：用户登出
    # 数据包
    'get_temperature': 'temp',       # tem：温度数据包请求
    # 服务器方发向树莓派的命令
    'stop_pi_stream': b'spps',       # spps：请求停止传输图片流
    'start_pi_stream': b'stps',      # stps：请求开始传输图片流
    'get_pi_data': b'data',          # data：请求获取数据
    'get_pi_log': b'log',            # log：日志请求
    'ali_heart': b'pi',              # pi:  阿里云服务器心跳包
    # 服务器发向APP的命令
    'pi_not_connect': b'pnc',        # pnc：树莓派未连接（错误状态）
    'img_end': b'end',               # end：图片结束标记
    # 服务器返回的状态信息
    'server_ok': b'ok',              # ok：服务器正常处理了请求
    'server_error': b'err',          # err：相关请求出错
    'invalid_cmd': b'ic',            # ic: 无法识别（无效）的的命令
    'user_not login': b'uni',        # uni:用户未登录
}

# 管理员的命令
admin_cmds = {
    # 针对用户
    'show_all_user_info': 'all-user',
    'show_online_info': 'online-user',
    'login_user': 'user-login',
    'logout_user': 'user-logout',
    # 针对树莓派
    'show_online_pi': 'online-pi'
}

# 数据包
data_package = {
    'temperature' : 0,
}


###################### 摄像头部分 #############################

# 摄像头每一次接收的图片大小
img_size = 1024


###################### 服务器端部分 ################################

admin_enable = True

# 用户信息
user_info_list = {
    'id': 0,
    'password': 1,
    'name': 2,
    'pi_id':0
}

# 树莓派信息
pi_info_list = {
    "id": 0,
    "user_id": 0
}

# 数据文件目录
file_dir = os.path.abspath(os.path.join(os.getcwd(), '.'))

# 用户信息文件
user_info_path = os.path.join(file_dir, 'userInfo/')

# 树莓派信息文件
pi_info_path = os.path.join(file_dir, 'userInfo/')

# 最大监听数目
max_listen = 60

# 允许的最大命令长度
max_cmds_length = 50

# 存放客户端日志的文件
log_file = os.path.join(file_dir, 'logs')

# 是否存放日志
save_log = True

# 存放数据包日志的文件
data_package_file = os.path.join(file_dir, 'pipackage')

# 连接超时的时间
connect_timeout = 5

app_file = os.path.join(file_dir, 'app-debug.apk')
