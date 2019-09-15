import time
from django.http import HttpResponse, StreamingHttpResponse, FileResponse
from django.shortcuts import render
from app.server import plantbox as pb

user_connect = pb.UserConnect()
pi_connect = pb.PiConnect()
user_connect.set_pi_connect(pi_connect)
pi_connect.set_user_connect(user_connect)
pi_connect.connect()
pb.func.clear_log()

# (假)数据
data_base = {
    'temperature': 25,
    'water_deep': 126,
    'fish_status': '活跃',
    'water_tmd': '非常清澈',
}

# Create your views here.

def index(request):
    return HttpResponse("Welcome to Electronic Ecological Estanciero!<br>欢迎访问 微生态管家！")


# 网页版用户登录
def user_connect_by_web(request, cmd):
    pb.func.write_logs('网页用户登录：' + cmd)
    try:
        user_id, user_password = cmd.split(pb.config.cmds['id_pwd_split'])
    except ValueError:
        pb.func.write_logs('登录失败！登录格式错误！')
        return HttpResponse('登录失败！登录格式错误！（ ' + cmd + ' ）')
    if user_connect.connect(user_id, user_password, pb.UserEnv(pb.USER_ENV_WEB)):
        pb.func.write_logs('登录成功!')
        return HttpResponse('登录成功！你的用户信息：<br><br>')
    else:
        pb.func.write_logs('登录失败！账号或密码错误！')
        return HttpResponse('登录失败！账号或密码错误！（账号：%s 密码：%s）' % (user_id, user_password))


# Android版用户登录
def user_connect_by_app(request, cmd):
    pb.func.write_logs('Android用户登录：' + cmd)
    try:
        user_id, user_password = cmd.split(pb.config.cmds['id_pwd_split'])
    except ValueError:
        pb.func.write_logs('登录失败！登录格式错误！')
        return HttpResponse(pb.config.cmds['server_error'])
    if user_connect.connect(user_id, user_password, pb.UserEnv(pb.USER_ENV_WEB)):
        pb.func.write_logs('登录成功!')
        return HttpResponse(pb.config.cmds['server_ok'])
    else:
        pb.func.write_logs('登录失败！账号或密码错误！')
        return HttpResponse(pb.config.cmds['server_error'])


# web管理员执行命令
def web_admin(request, cmd):
    pb.func.write_logs('(网页)管理员执行命令：' + cmd)
    return HttpResponse(pb.resolve_admin_cmd(cmd, pb.USER_ENV_WEB_ADMIN, user_connect, pi_connect))


# python脚本执行管理员命令
def py_admin(request, cmd):
    pb.func.write_logs('(Python脚本)管理员执行命令：' + cmd)
    return HttpResponse(pb.resolve_admin_cmd(cmd, pb.USER_ENV_PY_ADMIN, user_connect, pi_connect))


# Android 用户命令
def app_cmd(request, user_id, target, cmd):
    pb.func.write_logs('Androi+d App执行命令：' + cmd)
    return HttpResponse(pb.resolve_user_cmd(user_id, target, cmd, pb.USER_ENV_APP, user_connect, pi_connect))


# 微信 用户命令
def wx_cmd(request, user_id, target, cmd):
    pb.func.write_logs('微信执行命令：' + cmd)
    return HttpResponse(pb.resolve_user_cmd(user_id, target, cmd, pb.USER_ENV_WX, user_connect, pi_connect))


# 网页 用户命令
def web_cmd(request, user_id, target, cmd):
    pb.func.write_logs('网页执行命令：' + cmd)
    return HttpResponse(pb.resolve_user_cmd(user_id, target, cmd, pb.USER_ENV_WEB, user_connect, pi_connect))


# 图片流
def stream(request, user_id):
    user =  user_connect.get_user(user_id)
    if not user:
        return HttpResponse('拒绝访问！用户[%s]不存在或者未上线！' % user_id)
    if not user.is_pi_connected:
        return HttpResponse('树莓派未连接！')
    if user.pi.is_send_stream:
        user.pi.cmd_socket.sendall(pb.config.cmds['stop_pi_stream'])
        time.sleep(0.5)
    user.pi.cmd_socket.sendall(pb.config.cmds['start_pi_stream'])
    if user.pi.cmd_socket.recv(pb.config.max_cmds_length) == pb.config.cmds['server_error']:
        return HttpResponse('树莓派摄像头不可用！')

    res = StreamingHttpResponse(user.pi.send_stream())
    res['Control'] = 'no-cache, private'
    res['Pragma'] = 'cache'
    res['Content-Type'] = 'multipart/x-mixed-replace; boundary=BoundaryString'
    pb.func.write_logs("开始发送图片流")
    user.pi.check_stream()
    return res

def app_download(request):
    f = open(pb.config.app_file, 'rb')
    res = HttpResponse(f)
    f.close()
    res['Content-Type'] = 'application/octet-stream'
    res['Content-Disposition'] = 'attachment;filename="app-debug.apk"'
    return res

# (^-^) #
def tcs(request):
    return render(request, "tcs.html")


# 网页界面
def website(request, user_id):
    user = user_connect.get_user(user_id)
    if not user:
        return HttpResponse('拒绝访问！用户[%s]不存在或者未上线！' % user_id)
    data_base['user_id'] = user_id
    return render(request, "web_camera.html", data_base)
