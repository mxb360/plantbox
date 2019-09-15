import time, sys, urllib.request, urllib.error

#url = 'https://www.zyklql.site'
url = 'http://120.79.12.45:51430'
user = '106+c106'

print('测试连接服务器 ...')
print('<%s>\n' % url)
try:
    s = urllib.request.urlopen(url)
    s.close()
except urllib.error.URLError as e:
    print('错误：服务器连接失败！<%s>' % e)
    sys.exit()

print('服务器正常工作。')

print('登录：' + user)
cmd_url = url + '/py_admin/user-login:' + user
print('<%s>\n' % cmd_url)
s = urllib.request.urlopen(cmd_url)
print(s.read().decode())
s.close()

while True:
    try:
        cmd = input('>>> ')
        if cmd:
            cmd_url = url + '/py_admin/' + cmd
            print('<%s>\n' % cmd_url)
            s = urllib.request.urlopen(cmd_url)
            print(s.read().decode())
            s.close()
    except urllib.error.URLError as e:
        print('服务器出现内部错误！<%s>' % e)
    except KeyboardInterrupt:
        print('\nCtrl+C\n程序已退出。')
        break
