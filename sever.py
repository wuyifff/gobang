# -*- coding:utf-8 -*-
#  === TCP 服务端程序 server.py ， 支持多客户端 ===

# 导入socket 库
import numpy as np
from socket import *
from threading import Thread

mapRecord = np.zeros((15, 15))
mapsize = 15
IP = ''
PORT = 3333
BUFLEN = 512
ready1 = False
ready2 = False
g_index = 0                 #轮到谁落子
g_chess = 1                 #落子颜色
client_list = []
listenSocket = None


def sever_init():
    global listenSocket
    # 实例化一个socket对象 用来监听客户端连接请求
    listenSocket = socket(AF_INET, SOCK_STREAM)

    # socket绑定地址和端口
    listenSocket.bind((IP, PORT))

    listenSocket.listen(8)
    print(f'服务端启动成功，在{PORT}端口等待客户端连接...')


def clear():
    global mapRecord
    mapRecord = np.zeros((15,15))
    print(mapRecord)

#判断是否有五子
def Is_over(mapRecord):
    global mapsize
    for i in range(mapsize):
        for j in range(mapsize):
            if(mapRecord[i, j] != 0):
                count_right = count_down = count_right_down = count_left_down = 0
                for k in range(5):
                    if j+k <= 14:
                        count_right += mapRecord[i, j + k]
                    if i+k <= 14:
                        count_down += mapRecord[i + k, j]
                    if j+k <= 14 and i+k <= 14:
                        count_right_down += mapRecord[i + k, j + k]
                    if i+k <= 14 and j-k >= 0:
                        count_left_down += mapRecord[i + k, j - k]
                if(count_right == 5 or count_right == -5 or count_down == 5 or count_down == -5
                        or count_right_down == 5 or count_right_down == -5 or count_right_down == 5
                            or count_right_down == -5 or count_left_down == 5 or count_left_down == -5):
                    over = 1
                else:
                    over = 0
            else:
                over = 0
    return over

# 这是新线程执行的函数，每个线程负责和一个客户端进行通信
def clientHandler(client,addr):
    global ready1,ready2
    global g_chess,g_index
    global client_list
    while True:
        try:
            msg = client.recv(BUFLEN)
            if not msg:
                client_list.remove(client)
                client.close()
                print(f'客户端{addr} 关闭了连接,剩余在线客户端为{len(client_list)}')
                break
            elif msg.decode() == '1':
                print(f"player {str(addr)} is OK")
                if ready1 == True:
                    ready2 = True
                    num = 1
                else:
                    ready1 = True
                    num = 0
                break
        except Exception:
            client_list.remove(client)
            client.close()
            clear()
            print(f'客户端{addr} 关闭了连接,剩余在线客户端为{len(client_list)}')

    while ready1 == False or ready2 == False or len(client_list) != 2:
        pass
    while True:
        try:
            if g_index == num:
                client.send('1'.encode())
                msg = client.recv(BUFLEN)
                # 当对方关闭连接的时候，返回空字符串
                if not msg:
                    client_list.remove(client)
                    client.close()
                    print(f'客户端{addr} 关闭了连接,剩余在线客户端为{len(client_list)}' )
                    break
        #考虑一个关闭全部清空

                info = msg.decode()
                print(f'收到{addr}信息： {info}')

                # client.send(f'服务端接收到了信息 {info}'.encode())
                mapRecord[int(info.split()[0]), int(info.split()[1])] = g_chess
                if g_index == 0:
                    g_index = 1
                    g_chess = -1
                else:
                    g_index = 0
                    g_chess = 1
                toSend = [str(info.split()[0]), str(info.split()[1]), str(g_chess)]
                S = ' '.join(toSend)
                client_list[g_index].send(S.encode())
                if Is_over(mapRecord) == 1:
                    clear()
        except Exception:
            client_list.remove(client)
            client.close()
            clear()
            print(f'客户端{addr} 关闭了连接,剩余在线客户端为{len(client_list)}')




def accept_client():
    while True:
       # 在循环中，一直接受新的连接请求
       client, addr = listenSocket.accept()
       addr = str(addr)
       client_list.append(client)
       print(f'一个客户端 {addr} 连接成功,序号为{len(client_list)}' )

       # 创建新线程处理和这个客户端的消息收发
       th = Thread(target=clientHandler,args=(client,addr))
       # th.setDaemon(True)
       th.start()



if __name__ == '__main__':
    sever_init()
    # 新开一个线程，用于接收新连接
    thread = Thread(target=accept_client)
    thread.setDaemon(True)
    thread.start()
    # 主线程逻辑
    while True:
        cmd = input("""--------------------------
输入1:查看当前在线人数
输入2:打印棋盘
输入3:关闭服务端
""")
        if cmd == '1':
            print("--------------------------")
            print("当前在线人数：", len(client_list))
        elif cmd == '2':
            print(mapRecord)
        elif cmd == '3':
            exit()

