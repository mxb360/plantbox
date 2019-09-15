from app.server import config
from app.server import tools

# 日志记录
def write_logs(log, t=True):
    if t:
        if log[0] == '\n':
            log = '\n' + tools.get_current_time() + log[1:]
        else:
            log = tools.get_current_time() + log
    try:
        print(log)
    except OSError:
        pass
    if config.save_log:
        tools.write_file(config.log_file, log + '\n', 'a')


# 清除日志
def clear_log():
    open(config.log_file, 'w').close()


# 切割命令
def split_cmd(cmd):
    try:
        cmd, data = cmd.split(config.cmds['data_split'])
    except ValueError:
        return cmd
    try:
        user_id, user_passworld = data.split(config.cmds['id_pwd_split'])
    except ValueError:
        return cmd, data
    return  cmd, user_id, user_passworld

# 接收指定字节数的socket数据
def get_all_socket_data(sock, size):
    data = b''
    while size > len(data):
        data += sock.recv(1024)
    return data