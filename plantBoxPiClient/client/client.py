import os

try:
    import config, tools
except ImportError:
    from plantBoxPiClient.client import config, tools

import socket, urllib.request, urllib.error, sys

is_camera_useful = False
is_send_image = False
is_cmd_thread_start = False
cmd_socket = None
img_socket = None
connect_socket = None

class Camera(object):
    def __init__(self):
        pass

    # 连接摄像头
    @staticmethod
    def connect_camera():
        global is_camera_useful
        write_logs('\n检测摄像头是否有效 ...')
        if is_camera_useful:
            write_logs('摄像头已经在工作！')
            return
        if not config.use_camera:
            is_camera_useful = False
            write_logs('未使用摄像头！')
            return
        if config.same_machine:
            url = config.stream_locate_url
        else:
            url = config.stream_url

        write_logs('url： ' + url)
        try:
            stream = urllib.request.urlopen(url)
        except urllib.error.URLError:
            write_logs('摄像头连接失败！摄像头未打开！')
            print('请在摄像头服务器上键入： sudo motion  开启摄像头。')
            return
        write_logs('', False)
        for key, value in stream.getheaders():
            write_logs(key + '：' + value, False)
        write_logs('', False)
        stream.close()
        is_camera_useful = True
        write_logs('检测完成，摄像头正常工作。\n')
        return False

    # 开始发送图片
    @staticmethod
    def start_send_img():
        if not is_camera_useful:
            write_logs('摄像头不可用！', t=False)
            return -1
        if config.same_machine:
            url = config.stream_locate_url
        else:
            url = config.stream_url
        try:
            stream = urllib.request.urlopen(url)
        except urllib.error.URLError:
            write_logs('摄像头未打开！', t=False)
            return -1
        cmd_socket.sendall(config.ali_cmds['server_ok'])
        def _thread():
            global is_send_image
            write_logs('开始发送图片 ...', t=False)
            is_send_image = True
            while is_send_image:
                try:
                    img_socket.sendall(stream.read(config.img_size))
                except Exception as e:
                    write_logs('一个异常导致图片发送已停止！<' + str(e) + '>', t=False)
                    is_send_image = False
            stream.close()
            write_logs('图片发送已停止', t=False)

        tools.start_thread(_thread)
        return 0


# 连接服务器
def connect_server():
    global cmd_socket, img_socket, connect_socket
    write_logs('\n正在连接服务器 ...')
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.settimeout(config.connect_timeout)
    pi_id = tools.read_file(config.pi_info_file)
    if pi_id is not None:
        udp_socket.sendto(pi_id.encode(), (config.ali_host, config.ali_udp_port))
        try:
            if udp_socket.recv(config.max_cmds_length) == config.ali_cmds['server_ok']:
                write_logs('服务器接受了树莓派的连接请求，正在创建TCP连接 ...')
                cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cmd_socket.connect((config.ali_host, config.ali_tcp_port))
                write_logs('来自服务器的响应：' + cmd_socket.recv(config.max_cmds_length).decode())
                img_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                img_socket.connect((config.ali_host, config.ali_tcp_port))
                write_logs('来自服务器的响应：' + img_socket.recv(config.max_cmds_length).decode())
                connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                connect_socket.connect((config.ali_host, config.ali_tcp_port))
                write_logs('来自服务器的响应：' + connect_socket.recv(config.max_cmds_length).decode())
                config_info()
                write_logs('\n服务器连接成功，等待服务器的命令 ... \n')
            else:
                write_logs('服务器拒绝了树莓派的连接请求！')
                sys.exit()
        except (socket.timeout, TimeoutError):
            write_logs('服务器连接超时！')
            sys.exit()
        except ConnectionResetError:
            write_logs('连接被拒绝！')
            sys.exit()
    else:
        write_logs('错误：树莓派信息获取失败！不能打开文件：' + config.pi_info_file)


# 或取来自服务器命令的线程
def get_cmd_thread():
    if is_cmd_thread_start:
        return

    def _thread():
        global is_send_image, is_cmd_thread_start
        is_cmd_thread_start = True
        while True:
            data = (cmd_socket.recv(config.max_cmds_length).decode())
            if not data:
                write_logs('无法收到服务器的信息，服务器可能已经停止工作!\n线程终止。', t=False)
                is_cmd_thread_start = False
                sys.exit()
                pass
            write_logs('来自服务器：' + data, t=False)
            # 开始发送图片
            if data == config.ali_cmds['start_pi_stream']:
                if Camera.start_send_img() == -1:
                    cmd_socket.sendall(config.ali_cmds['server_error'])
            # 停止发送图片
            elif data == config.ali_cmds['stop_pi_stream']:
                is_send_image = False
            # 服务器向树莓派发送的命令，根源来自用户APP
            elif data.find(config.ali_cmds['app_to_pi'] + config.ali_cmds['cmd_split']) == 0:
                cmd = data[len(config.ali_cmds['app_to_pi']) + len(config.ali_cmds['cmd_split']):]
                write_logs("来自APP的命令：" + cmd, t=False)
                save_cmd(cmd)
                write_logs('命令：[%s]成功写入文件。' % cmd, t=False)
                cmd_socket.sendall(config.ali_cmds['server_ok'])
            # 向服务器传送树莓派数据
            elif data == config.ali_cmds['get_pi_data']:
                write_logs("服务器请求获得数据", t=False)
                data = get_pi_data()
                cmd_socket.sendall(str(len(data)).encode())
                cmd_socket.sendall(data.encode())
            # 服务器请求日志
            elif data == config.ali_cmds['get_pi_log']:
                write_logs("服务器请求获取日志", t=False)
                f = open(config.log_file, 'rb')
                data = f.read()
                f.close()
                cmd_socket.sendall(str(len(data)).encode())
                cmd_socket.sendall(data)
            else:
                write_logs('无法识别的命令：' + data, t=False)

    tools.start_thread(_thread)

# 显示配置信息
def config_info():
    write_logs('当前配置信息：')
    write_logs('    树莓派ID：%s' % tools.read_file(config.pi_info_file), False)
    write_logs('    阿里云服务器IP：' + config.ali_host, False)
    write_logs('    阿里云服务器web端口号：' + config.ali_web_port, False)
    write_logs('    阿里云服务器tcp端口号：' + str(config.ali_tcp_port), False)
    write_logs('    阿里云服务器域名：%s' % config.ali_url, False)
    write_logs('    摄像头局域网URL：' + config.stream_url, False)
    write_logs('    摄像头本地URL：%s' % config.stream_locate_url, False)
    write_logs('    是否使用摄像头：' + str(config.use_camera), False)
    write_logs('    允许的最大命令长度：%d' % config.max_cmds_length, False)
    write_logs('    一次性发送的图片大小：%d' % config.img_size, False)
    write_logs('    摄像头与树莓派客户端是否是同一个机子：%s' % config.same_machine, False)
    write_logs('    数据文件目录：' + config.file_dir, False)
    write_logs('    存放命令的文件：' + config.cmd_file, False)
    write_logs('    存放树莓派的数据文件：' + config.data_file, False)
    write_logs('    存放客户端日志的文件：' + config.log_file, False)
    write_logs('    是否记录日志：' + str(config.save_log), False)


# 获取来自树莓派的数据
def get_pi_data():
    return tools.read_file(config.data_file)


# 写入来自服务器的命令
def save_cmd(data):
    if tools.write_file(config.cmd_file, data):
        write_logs('命令写入文件时发生错误！', t=False)


# 获取配置文件
def get_config_file():
    return tools.read_file('config.py')


# 日志记录
def write_logs(log, t=True, p=True):
    if t:
        if log[0] == '\n':
            log = '\n' + tools.get_current_time() + log[1:]
        else:
            log = tools.get_current_time() + log
    if p:
        try:
            print(log)
        except OSError:
            pass
    if config.save_log:
        tools.write_file(config.log_file, log + '\n', 'a')


# 清除日志
def clear_log():
    open(config.log_file, 'w').close()


# 访问服务器测试
def check_server():
    write_logs('尝试访问服务器 ... ')
    write_logs('url： ' + config.ali_url)
    try:
        url = urllib.request.urlopen(config.ali_url)
    except (urllib.error.URLError, TimeoutError):
        write_logs('错误：服务器无法访问！(连接超时)')
        sys.exit()
    url.close()
    write_logs('服务器正常工作。')

def run_client():
    clear_log()
    check_server()
    Camera.connect_camera()
    connect_server()

    pid = os.fork()
    if pid:
        print('<进程ID：%d>' % pid)
        sys.exit()

    get_cmd_thread()
    while True:
        try:
            d = connect_socket.recv(config.max_cmds_length)
            if not d:
                raise Exception('接收到空内容')
        except KeyboardInterrupt:
            print('\nCtrl+C\n程序已退出！')
            return
        except Exception as e:
            print('与服务器的连接中断！ <' + str(e) + '>')
            connect_socket.close()
            img_socket.close()
            cmd_socket.close()
            return

if __name__ == '__main__':
    run_client()

