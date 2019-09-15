"""
    植物盒子 - 微生态管家 服务器后端逻辑代码

    实现树多莓派与多用户的实时通信

    版本 V2.0
    阿里云服务器 Django框架 uWSGI+Nginx服务器

    By 西华师范大学 电子信息工程学院 实验室 微生态管家团队
    2018-5
"""

import os, socket, time
from app.server import tools
from app.server import config
from app.server import func


USER_ENV_APP       = 0  # Android APP
USER_ENV_WX        = 1  # 微信小程序
USER_ENV_PC        = 2  # 电脑端软件
USER_ENV_WEB       = 3  # 网页端
USER_ENV_PY_ADMIN  = 4  # Python脚本管理员
USER_ENV_WEB_ADMIN = 5  # Python网页管理员


# 用户环境
class UserEnv(object):
    str = ['Android App', '微信小程序','电脑端软件', '网页端', 'Python脚本管理员', 'Python网页管理员']

    def __init__(self, env):
        self.env = env

    def __str__(self):
        return self.str[self.env]


# 用户连接守护
# 在Django views.py中创建，且只创建一个该对象
class UserConnect(object):
    def __init__(self):
        func.write_logs('创建UserConnect对象！')
        self.online_user = []  # 在线的用户
        self.pi_connect = None

    # 建立连接，用户登录
    def connect(self, user_id, user_password, user_env):
        func.write_logs('用户请求连接！')
        user_info = UserInfo.get_user_info_by_id(user_id)
        if user_info:
            if user_info.password == user_password:
                user = User(user_id, user_env)
                user.user_info = user_info
                user.is_online = True
                user.pi = self.pi_connect.get_pi(user_info.pi_id)
                if user.pi:
                    user.is_pi_connected = True
                    user.pi.is_user_connected = True
                    user.pi.user = user
                self.add_user(user)
                return user

    # 用户注销
    def logout(self, user_id):
        user = self.get_user(user_id)
        if user:
            self.online_user.remove(user)
            return True

    # 通过id获取User对象
    def get_user(self, user_id):
        for user in self.online_user:
            if user.id == user_id:
                return user

    # 添加用户
    def add_user(self, user):
        if not self.is_user_online(user.id):
            self.online_user.append(user)

    # 判断用户是否已经在线
    def is_user_online(self, user_id):
        for user in self.online_user:
            if user.id == user_id:
                return True

    # 获取所有的在线用户
    def get_all_online_user(self):
        return self.online_user

    def set_pi_connect(self, pi_connect):
        self.pi_connect = pi_connect


# 用户，当用户登录成功后，该对象会被创建，并存放于online_user变量中
class User(object):
    def __init__(self, user_id, env):
        self.id = user_id
        self.env = env
        self.is_online = False
        self.user_info = None
        self.is_pi_connected = False
        self.pi = None

    def __str__(self):
        return ('用户状态信息(编号：%s 环境：%s 用户是否在线：%s 用户信息：(%s) 树莓派是否已连接：%s)'
                % (self.id, self.env, self.is_online, self.user_info, self.is_pi_connected))


# 用户信息
class UserInfo(object):
    id = ""  # ID编号，此编号唯一，用来区分不同用户
    password = ""  # 用户密码
    name = ""  # 用户昵称
    pi_id = None  # 用户对应的树莓派ID

    def __str__(self):
        return '编号：%s 密码：%s  昵称：%s 树莓派编号：%s' % (self.id, self.password, self.name, self.pi_id)

    # 根据user_id返回UserInfo对象，前提是该用户存在
    @staticmethod
    def get_user_info_by_id(user_id):
        file = os.path.join(config.user_info_path, user_id)
        # 确认该用户存在
        if os.path.exists(file):
            user_info = UserInfo()
            user_info.id = user_id
            user_info.password = tools.read_file(file, config.user_info_list['password'])
            user_info.name = tools.read_file(file, config.user_info_list['name'])
            user_info.pi_id = tools.read_file(file, config.user_info_list['pi_id'])
            return user_info

    # 判断该用户是否存在
    @staticmethod
    def is_user_exists(user_id):
        return os.path.exists(os.path.join(config.user_info_path, user_id))

    # 获取所有的在线用户
    @staticmethod
    def get_all_userInfo():
        users = []
        files = [f for f in os.listdir(config.user_info_path)
                 if os.path.isfile(os.path.join(config.user_info_path, f))]
        for user_id in files:
            users.append(UserInfo.get_user_info_by_id(user_id))
        return users


# 检测树莓派的连接
class PiConnect(object):
    def __init__(self):
        self.online_pi = []
        self.user_connect = None

    # 与树莓派建立连接
    def connect(self):
        func.write_logs('树莓派连接正在准备中 ... ')
        # 连接检验线程
        def __thread(pi_info):
            func.write_logs('验证通过，与树莓派建立tcp连接中 ...')
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_socket.settimeout(config.connect_timeout)
            tcp_socket.bind(('', config.ali_tcp_port))
            tcp_socket.listen(3)
            try:
                cmd_socket, addr = tcp_socket.accept()
                cmd_socket.sendall(config.cmds['server_ok'])
                img_socke, addr = tcp_socket.accept()
                img_socke.sendall(config.cmds['server_ok'])
                connect_socket, addr = tcp_socket.accept()
                connect_socket.sendall(config.cmds['server_ok'])
            except socket.timeout:
                print('TCP连接超时，树莓派连接失败！')
                return
            func.write_logs('TCP连接创建成功！')
            pi = Pi(pi_info.id)
            pi.pi_info = pi_info
            pi.cmd_socket = cmd_socket
            pi.img_socket = img_socke
            pi.connect_socket = connect_socket
            pi.user = self.user_connect.get_user(pi_info.user_id)
            pi.is_online = True
            self.add_pi(pi)
            if pi.user:
                pi.is_user_connected = True
                pi.user.is_pi_connected = True
                pi.user.pi = pi
            self.keep_pi_connect(pi)
            func.write_logs('树莓派%s与服务器连接成功。' % pi.id)

        # 接收树莓派请求线程
        def _thread():
            func.write_logs('树莓派连接线程已启动！')
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.bind(('', config.ali_udp_port))

            while True:
                try:
                    info, addr = udp_socket.recvfrom(config.max_cmds_length)
                    func.write_logs('接收到树莓派连接：' + str(addr))
                    func.write_logs('验证树莓派信息：%s ...' % info)
                    try:
                        pi_info = PiInfo.get_pi_info_by_id(info.decode())
                    except UnicodeDecodeError:
                        pi_info = None
                    if pi_info:
                        udp_socket.sendto(config.cmds['server_ok'], addr)
                        tools.start_thread(__thread, (pi_info, ))
                    else:
                        udp_socket.sendto(config.cmds['server_error'], addr)
                        func.write_logs('树莓派信息失败！没有匹配！ ' + str(info))
                except Exception as e:
                    func.write_logs('树莓派连接线程检测出异常：' + str(e))
        tools.start_thread(_thread)

    # 保持连接
    def keep_pi_connect(self, pi):
        def _thread():
            try:
                func.write_logs('启动树莓派%s的连接检测线程' % pi.id)
                while pi.is_online:
                    try:
                        pi.connect_socket.sendall(b'pi')
                        time.sleep(3)
                    except ConnectionResetError:
                        func.write_logs('树莓派%s关掉了一个现有连接... <ConnectionReset>' % pi.id)
                        self.disconnect(pi)
                    except Exception as e:
                        func.write_logs('树莓派连接异常中断， 已断开连接！<%s>' % str(e))
                        raise
            except Exception as e:
                func.write_logs('异常：' + str(e) + ' [检测与树莓派的连接状态]线程退出')
                self.disconnect(pi)
            func.write_logs('树莓派%s的连接守护线程退出' % pi.id)
        tools.start_thread(_thread)

    # 树莓派pi下线
    def disconnect(self, pi):
        if not self.get_pi(pi.id):
            return
        if pi.user:
            pi.user.is_pi_connected = False
            pi.user.pi = None
        pi.is_online = False
        self.online_pi.remove(pi)
        try:
            pi.connect_socket.close()
            pi.cmd_socket.close()
            pi.img_socket.close()
        except Exception as e:
            func.write_logs('断开树莓派%s时 Exception: %s' %(pi.id, str(e)))
        func.write_logs('树莓派%s已下线。' % pi.id)


    # UserConnect对象的引用
    def set_user_connect(self, user_connect):
        self.user_connect = user_connect

    # 添加在线用户
    def add_pi(self, pi):
        _pi = self.get_pi(pi.id)
        if _pi:
            func.write_logs('该树莓派已经连接，先断开之前的连接 ... ')
            self.disconnect(_pi)
        self.online_pi.append(pi)


    # 通过id获取在线的pi对象
    def get_pi(self, pi_id):
        for pi in self.online_pi:
            if pi.id == pi_id:
                return pi

    # 获取所有的在线用户
    def get_all_online_pi(self):
        return self.online_pi


# 树莓派，当用户登录成功后，该对象会被创建，并存放于online_pi变量中
class Pi(object):
    def __init__(self, pi_id):
        self.id = pi_id
        self.is_online = False
        self.connect_socket = None
        self.pi_info = None
        self.cmd_socket = None
        self.img_socket = None
        self.is_user_connected = False
        self.is_send_stream = False
        self.is_check_stream_start = False
        self.user = None

    # 发送图片流
    def send_stream(self):
        while self.is_online:
            self.is_send_stream = True
            try:
                yield self.img_socket.recv(config.img_size)
            except Exception as e:
                func.write_logs('图片传输异常：' + str(e))
                yield b''
        return b''

    # 图片发送检测
    def check_stream(self):
        if self.is_check_stream_start:
            return
        self.is_check_stream_start = True
        func.write_logs('开始运行图片发送检测线程')

        def _thread():
            while True:
                if self.is_send_stream:
                    self.is_send_stream = False
                    time.sleep(4)
                    if not self.is_send_stream:
                        self.cmd_socket.sendall(config.cmds['stop_pi_stream'])
                        func.write_logs('停止转发图片')
                        #break
            self.is_check_stream_start = False
            func.write_logs('图片发送检测线程退出')
        tools.start_thread(_thread)

    def __str__(self):
        return '编号：%s 是否在线：%s 是否与用户连接：%s' % (self.id, self.is_online, self.is_user_connected)


# 树莓派信息
class PiInfo(object):
    id = ""              # ID编号，此编号唯一，用来区分不同树莓派
    user_id = None       # 树莓派对应的用户ID

    # 根据提供的pi_id在数据库中拉取与树莓派信息，前提是该树莓派用户存在
    @staticmethod
    def get_pi_info_by_id(pi_id):
        file = os.path.join(config.pi_info_path, pi_id)
        # 确认该树莓派存在
        if os.path.exists(file):
            pi_info = PiInfo()
            pi_info.id = tools.read_file(file, config.pi_info_list['id'])
            pi_info.user_id = tools.read_file(file, config.pi_info_list['user_id'])
            return pi_info

    # 判断树莓派是否存在
    @staticmethod
    def is_pi_exist(pi_id):
        return os.path.exists(os.path.join(config.pi_info_path, pi_id))


# 处理管理员的命令
def resolve_admin_cmd(cmd, env, user_connect, pi_connect):
    def _str(_msg):
        if env == USER_ENV_WEB_ADMIN:
            return '（来自网页的管理员操作）<br><br>' + _msg.replace('\n', '<br>')
        if env == USER_ENV_PY_ADMIN:
            return '（来自Python脚本的管理员操作）\n\n' + _msg
        return _msg

    # 处理命令
    if not config.admin_enable:
        return _str('错误：管理员不可用！')

    # 查看存在的所有用户
    if cmd == config.admin_cmds['show_all_user_info']:
        res = '所有的用户信息：\n\n'
        all_user_info = UserInfo.get_all_userInfo()
        for user_info in all_user_info:
            res += str(user_info) + '\n'
        res += '\n 共有用户%d个' % len(all_user_info)
        return _str(res)

    # 查看已在线的所有用户
    elif cmd == config.admin_cmds['show_online_info']:
        res = '所有已在线的用户信息：\n\n'
        all_user = user_connect.get_all_online_user()
        for user in all_user:
            res += str(user) + '\n'
        res += '\n 共有用户%d个' % len(all_user)
        return _str(res)

    # 管理员登录用户
    elif cmd.find(config.admin_cmds['login_user'] + config.cmds['data_split']) >= 0:
        try:
            data = cmd.split(config.cmds['data_split'])[1]
            user_id, user_passworld = data.split(config.cmds['id_pwd_split'])
        except (ValueError, IndexError):
            return _str('错误：登录格式错误！')
        user = user_connect.connect(user_id, user_passworld, UserEnv(env))
        if user:
            return _str('登录成功！\n用户信息：' + str(user))
        else:
            return _str('登录失败！账号或密码错误！')

    # 管理员注销用户
    elif cmd.find(config.admin_cmds['logout_user'] + config.cmds['data_split']) >= 0:
        try:
            user_id = cmd.split(config.cmds['data_split'])[1]
        except (ValueError, IndexError):
            return _str('错误：用户注销格式错误！')
        if user_connect.logout(user_id):
            return _str('用户 %s 已成功注销' % user_id)
        else:
            return _str('注销失败！用户 %s 不存在或者未登录。' % user_id)

    # 查看在线的树莓派
    elif cmd == config.admin_cmds['show_online_pi']:
        res = '所有已在线的树莓派信息：\n\n'
        all_pi = pi_connect.get_all_online_pi()
        for pi in all_pi:
            res += str(pi) + '\n'
        res += '\n 共有在线树莓派%d个' % len(all_pi)
        return _str(res)
    # 以用户的身份发送命令给服务器
    elif cmd.find('user:') >= 0:
        try:
            user_id, target, _cmd = cmd[5:].split('-')
        except ValueError:
            return _str('无法识别的User命令: ' + cmd[5:])
        return _str(resolve_user_cmd(user_id, target, _cmd, env, user_connect, pi_connect))

    # 无效的命令
    else:
        return _str('错误：无法识别的管理员命令：' + cmd)


# 处理用户目命令
def resolve_user_cmd(user_id, target, cmd, env, user_connect, pi_connect):
    def _str(cmds, msg):
        if env == USER_ENV_PY_ADMIN or env == USER_ENV_WEB_ADMIN:
            return msg
        return cmds
    user = user_connect.get_user(user_id)
    if not user:
        return _str(config.cmds['user_not login'], '拒绝访问！用户[%s]未登录或者不存在！' % user_id)
    # 发向树莓派的命令
    if target == config.cmds['app_to_pi']:
        if not user.is_pi_connected:
            return _str(config.cmds['pi_not_connect'], '数据发送失败！用户[%s]对应的树莓派未连接！' % user_id)
        user.pi.cmd_socket.sendall((target + config.cmds['cmd_split'] + cmd).encode())
        if user.pi.cmd_socket.recv(config.max_cmds_length) == config.cmds['server_ok']:
            return _str(config.cmds['server_ok'].decode(), '成功向树莓派发送数据：' + cmd)
        else:
            return _str(config.cmds['server_error'].decode(), '向树莓派发送数据失败！')

    # 发向服务器的命令
    elif target == config.cmds['app_to_server']:
        # 获取树莓派数据
        if cmd == config.cmds['data']:
            func.write_logs('用户[%s]请求获取树莓派数据' % user.id)
            if not user.is_pi_connected:
                return _str(config.cmds['pi_not_connect'], '操作失败！树莓派未连接！')
            user.pi.cmd_socket.sendall(config.cmds['get_pi_data'])
            data_size = user.pi.cmd_socket.recv(10)
            try:
                size = int(data_size)
            except ValueError:
                return _str(config.cmds['server_error'].decode(), '数据请求出错，无法获取数据大小 (' + str(data_size) + ')')
            else:
                data = func.get_all_socket_data(user.pi.cmd_socket, size).decode()
                return _str(data, '树莓派的数据：\n' + data)

        # 温度数据包
        elif cmd == config.cmds['get_temperature']:
            func.write_logs('用户[%s]请求温度数据包' % user.id)
            data = tools.read_file(config.data_package_file, config.data_package['temperature'])
            return _str(data, '温度数据包：' + data)
        else:
            return _str(config.cmds['server_error'].decode(), '用户[%s]提供了无法识别的服务器命令：' % cmd)
    else:
        return _str(config.cmds['invalid_cmd'], '无法识别的APP命令头部：' + target)
