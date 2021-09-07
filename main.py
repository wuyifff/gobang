import tkinter as tk
from tkinter import messagebox
import numpy as np
import pygame
from socket import *
from threading import Thread


#用tkinter定义窗口
top = tk.Tk()
top.title("五子棋")
top.geometry('800x700')                 #窗口大小
top.iconbitmap("icon.ico")              #窗口图标
frame_l = tk.Frame(top)                 #分割棋盘和按钮
frame_r = tk.Frame(top)
frame_l.pack(side = "left")
frame_r.pack(side = "right")


#定义地图尺寸
mapsize = 15
#元素尺寸
pixsize = 40
#空白编号
backcode = 0
#白棋
whitecode = 1
#黑棋
blackcode = -1
#棋子列表
childMap = []
toSend = []
#记录棋图
mapRecord = np.zeros((15, 15))


#定义白子先下
B_or_W = 1
over = 0


# 定义画布
canvas = tk.Canvas(frame_l, height=mapsize * pixsize, width=mapsize * pixsize, bg="#F2D76C")
canvas.pack(pady=10)


#设置服务器的参数
IP = '81.70.163.24'                 #服务器现在已经关闭，测试请分别把客户端ip设置为127.0.0.0  服务端 0.0.0.1
SERVER_PORT = 3333
BUFLEN = 1024                       #定义最多接受的数据长度
dataSocket = None
myTurn = False
msg = '0'


#定义ai的参数
depth = 2                       #搜索深度只能为偶数
d_click = True                  #难度设置
search_count = 0                #搜索次数
cut_count = 0                   #剪枝次数
#下面是局面估值参数
shape_score5 = [(50, (0, 1, 1, 0, 0)),(50, (-1, 1, 1, 0, 0)),(50, (0, 1, 1, 0, -1)),(50, (0, 1, 1, -1, -1)),
               (50, (0, 0, 1, 1, 0)),(50, (-1, 0, 1, 1, 0)),(50, (0, 0, 1, 1, -1)),(50, (-1, -1, 1, 1, 0)),
               (5000, (1, 1, 0, 1, 0)),(5000, (1, 1, 0, 1, -1)),
               (5000, (0, 0, 1, 1, 1)),(5000, (-1, 0, 1, 1, 1)),(3000, (0, -1, 1, 1, 1)),(3000, (-1, -1, 1, 1, 1)),
               (5000, (1, 1, 1, 0, 0)),(5000, (1, 1, 1, 0, -1)),(3000, (1, 1, 1, -1, 0)),(3000, (1, 1, 1, -1, -1)),
               (10000, (0, 1, 1, 1, 0)),
               (50000, (1, 1, 1, 0, 1)),
               (50000, (1, 1, 0, 1, 1)),
               (50000, (1, 0, 1, 1, 1)),
               (50000, (1, 1, 1, 1, 0)),
               (50000, (0, 1, 1, 1, 1)),
               (99999999, (1, 1, 1, 1, 1))]
shape_score6 = [(500000, (0, 1, 1, 1, 1, 0)),(500000, (-1, 1, 1, 1, 1, 0)),(500000, (0, 1, 1, 1, 1, -1)),
                (50000, (0, 1, 0, 1, 1, 0)),
               (50000, (0, 1, 1, 0, 1, 0))]


#定义ai的评估局面的函数
def get_score(mapRecord):
    total_score = 0
    for i in range(15):
        for j in range(15):
            if mapRecord[i][j] != 0:
                one_score = 0
                right_list = ()
                down_list = ()
                rd_list = ()
                ld_list = ()
                right_list6 = ()
                down_list6 = ()
                rd_list6 = ()
                ld_list6 = ()
                cross_list = [ 0 for t in range(8) ]                        #下面开始判断交叉
                if j + 2 <= 14 and j - 2 >= 0 :
                   right_list = (mapRecord[i][j-2],mapRecord[i][j-1],mapRecord[i][j],mapRecord[i][j+1],mapRecord[i][j+2])
                if i + 2 <= 14 and i - 2 >= 0:
                    down_list = (mapRecord[i-2][j],mapRecord[i-1][j],mapRecord[i][j],mapRecord[i+1][j],mapRecord[i+2][j])
                if i + 2 <= 14 and j + 2 <= 14 and i - 2 >= 0 and j - 2 >= 0:
                    rd_list = (mapRecord[i-2][j-2],mapRecord[i-1][j-1],mapRecord[i][j],mapRecord[i+1][j+1],mapRecord[i+2][j+2])
                if i + 2 <= 14 and j - 2 >= 0 and i - 2 >= 0 and j + 2 <= 14:
                    ld_list = (mapRecord[i-2][j+2],mapRecord[i-1][j+1],mapRecord[i][j],mapRecord[i+1][j-1],mapRecord[i+2][j-2])
                if j + 3 <= 14 and j - 2 >= 0 :
                   right_list6 = (mapRecord[i][j-2],mapRecord[i][j-1],mapRecord[i][j],mapRecord[i][j+1],mapRecord[i][j+2],mapRecord[i][j+3])
                if i + 3 <= 14 and i - 2 >= 0:
                    down_list6 = (mapRecord[i-2][j],mapRecord[i-1][j],mapRecord[i][j],mapRecord[i+1][j],mapRecord[i+2][j],mapRecord[i+3][j])
                if i + 3 <= 14 and j + 3 <= 14 and i - 2 >= 0 and j - 2 >= 0:
                    rd_list6 = (mapRecord[i-2][j-2],mapRecord[i-1][j-1],mapRecord[i][j],mapRecord[i+1][j+1],mapRecord[i+2][j+2],mapRecord[i+3][j+3])
                if i + 3 <= 14 and j - 3 >= 0 and i - 2 >= 0 and j + 2 <= 14:
                    ld_list6 = (mapRecord[i-2][j+2],mapRecord[i-1][j+1],mapRecord[i][j],mapRecord[i+1][j-1],mapRecord[i+2][j-2],mapRecord[i+3][j-3])
                for (score, shape) in shape_score5:
                    if right_list == shape:
                        cross_list[0] += 1
                        one_score += score
                    if down_list == shape:
                        cross_list[1] += 1
                        one_score += score
                    if rd_list == shape:
                        cross_list[2] += 1
                        one_score += score
                    if ld_list == shape:
                        cross_list[3] += 1
                        one_score += score
                for (score, shape) in shape_score6:
                    if right_list6 == shape:
                        cross_list[4] += 1
                        one_score += score
                    if down_list6 == shape:
                        cross_list[5] += 1
                        one_score += score
                    if rd_list6 == shape:
                        cross_list[6] += 1
                        one_score += score
                    if ld_list6 == shape:
                        cross_list[7] += 1
                        one_score += score
                cross = 0
                for c in cross_list:
                    cross += c
                if cross:
                    total_score += one_score * cross /2           #形状乘以交叉，系数为1.5
    return total_score


#初始棋盘
def draw_map():
    global  canvas
    #画网格
    for i in range(mapsize):
        canvas.create_line(i * pixsize+pixsize/2, pixsize/2,
                      i * pixsize+pixsize/2, mapsize * pixsize-pixsize/2,
                      fill='black')
        canvas.create_line(pixsize/2, i * pixsize+pixsize/2,
                      mapsize * pixsize-pixsize/2, i * pixsize+pixsize/2,
                      fill='black')
    canvas.create_oval(34* pixsize/10,34* pixsize/10,
                       36 * pixsize/10 ,  36 * pixsize/10, fill='black')
    canvas.create_oval(34* pixsize/10+8*pixsize,34* pixsize/10,
                       36 * pixsize/10+8*pixsize ,  36 * pixsize/10, fill='black')
    canvas.create_oval(34* pixsize/10+8*pixsize,34* pixsize/10+8*pixsize,
                       36 * pixsize/10+8*pixsize,36 * pixsize/10+8*pixsize, fill='black')
    canvas.create_oval(34* pixsize/10,34* pixsize/10+8*pixsize,
                       36 * pixsize/10 ,  36 * pixsize/10+8*pixsize, fill='black')
    canvas.create_oval(34* pixsize/10+4*pixsize,34* pixsize/10+4*pixsize,
                       36 * pixsize/10+4*pixsize ,  36 * pixsize/10+4*pixsize, fill='black')


#判断是否有五子，游戏是否结束
def Is_over(mapRecord):
    global over
    for i in range(mapsize):
        for j in range(mapsize):
            if(mapRecord[i,j] != 0):
                count_right = count_down = count_right_down = count_left_down = 0
                for k in range(5):
                    if j+k <= 14:
                        count_right += mapRecord[i,j+k]
                    if i+k <= 14:
                        count_down += mapRecord[i+k,j]
                    if j+k <= 14 and i+k <= 14:
                        count_right_down += mapRecord[i+k,j+k]
                    if i+k <= 14 and j-k >= 0:
                        count_left_down += mapRecord[i+k,j-k]
                if(count_right == 5 or count_right == -5 or count_down == 5 or count_down == -5
                        or count_right_down == 5 or count_right_down == -5 or count_right_down == 5
                            or count_right_down == -5 or count_left_down == 5 or count_left_down == -5):
                    over = 1
                    return
                else:
                    over = 0
            else:
                over = 0


#定义绘制棋子的函数
def draw_chess(x,y,color):
    global B_or_W,childMap,mapRecord
    B_or_W = color
    if B_or_W == -1 :                                    #对方落白子轮到我方落黑子，但仍然需要先绘制对方的白子
        child = canvas.create_oval(x * pixsize,
                                   y * pixsize,
                                   x * pixsize + pixsize,
                                   y * pixsize + pixsize, fill='white')
        mapRecord[y, x] = 1
    elif B_or_W == 1 :
        child = canvas.create_oval(x * pixsize,
                                   y * pixsize,
                                   x * pixsize + pixsize,
                                   y * pixsize + pixsize, fill='black')
        mapRecord[y, x] = -1
    down.play()
    childMap.append(child)
    Is_over(mapRecord)
    if over == 1:
        if B_or_W == 1:
            tk.messagebox.showinfo('game over', 'black win!')
        else:
            tk.messagebox.showinfo('game over', 'white win!')
        clear()


#单机双人
def self_playChess(event):
    global  mapRecord
    global B_or_W
    global over
    x = event.x // pixsize                              # "//"表示整数除法
    y = event.y // pixsize                              # x和y获得点击的相对坐标
    if (B_or_W == 1 and mapRecord[y,x] == 0):
        child = canvas.create_oval(x * pixsize,         #画棋子
                               y * pixsize,
                               x * pixsize + pixsize,
                               y * pixsize + pixsize, fill='white')
        mapRecord[y, x] = B_or_W
        B_or_W = -1
    elif B_or_W == -1 and mapRecord[y,x] == 0:
        child = canvas.create_oval(x * pixsize,
                                   y * pixsize,
                                   x * pixsize + pixsize,
                                   y * pixsize + pixsize, fill='black')
        mapRecord[y, x] = B_or_W
        B_or_W = 1
    else:
        return                                          #如果重复点击已经落子的地方则什么都不做
    down.play()                                         #播放落子音效
    childMap.append(child)
    Is_over(mapRecord)
    if over == 1 :
        if B_or_W == 1:
            tk.messagebox.showinfo('game over','black win!')
        else:
            tk.messagebox.showinfo('game over', 'white win!')
        clear()


#需要注意 x 和 y 与 mapRecord 的 x 和 y 相反
def two_playChess(event):
    global B_or_W
    global mapRecord, childMap
    global over
    global toSend
    global myTurn
    if myTurn == True:
        x = event.x // pixsize                              #获取点击位置绘制棋子，同上
        y = event.y // pixsize
        if (B_or_W == 1 and mapRecord[y,x] == 0):
            child = canvas.create_oval(x * pixsize,
                                   y * pixsize,
                                   x * pixsize + pixsize,
                                   y * pixsize + pixsize, fill='white')
            mapRecord[y, x] = B_or_W
            B_or_W = -1
        elif B_or_W == -1 and mapRecord[y,x] == 0:
            child = canvas.create_oval(x * pixsize,
                                       y * pixsize,
                                       x * pixsize + pixsize,
                                       y * pixsize + pixsize, fill='black')
            mapRecord[y, x] = B_or_W
            B_or_W = 1
        else:
            return
        down.play()                                            #播放落子音效
        childMap.append(child)
        myTurn = False
        Is_over(mapRecord)
        if over == 1 :
            if B_or_W == 1:
                tk.messagebox.showinfo('game over','black win!')
            else:
                tk.messagebox.showinfo('game over', 'white win!')
            for child in childMap:
                canvas.delete(child)
            childMap.clear()
            mapRecord = np.zeros((15, 15))
        temp = B_or_W                                           #本地黑白翻转，传给服务器的不需要翻转
        if temp == 1:
            temp = 0
        else:
            temp =1
        toSend = [str(y),str(x),str(temp)]
        send_message()                                          #发送落子信息


#判断ai将要落子的位置是否有子相邻
def have_neighbour(mapRecord,x,y):
    if mapRecord[x+1,y] == 0 and mapRecord[x+1,y+1] == 0 and mapRecord[x,y+1] == 0 and mapRecord[x-1,y+1] == 0 and mapRecord[x-1,y] == 0 \
            and mapRecord[x-1,y-1] == 0 and mapRecord[x,y-1] == 0 and mapRecord[x+1,y-1] == 0:
        return 0
    else:
        return 1


#递归得到以落子为中心的空位列表，加快剪枝
def get_list(x,y,ai_list,round):
    if round == 0:
        return
    for i in range(max(0, x - 1), min(14, x + 2)):
        for j in range(max(0, y - 1), min(14, y + 3)):
            if mapRecord[i, j] == 0 and have_neighbour(mapRecord, i, j) and (i,j) not in ai_list:
                ai_list.append((i, j))
                get_list(i, j, ai_list, round-1)


#采用α-β剪枝的极大极小算法
def ai_search(x,y,mapRecord,alpha,beta,depth,is_ai,chess_list):
    global search_count,cut_count
    search_count += 1
    ai_list = []
    chess_list1 = chess_list[:]
    chess_list_max = chess_list[:]
    if depth == 0:
        beta = get_score(mapRecord*(-1)) - 5 * get_score(mapRecord)
        return alpha,beta,chess_list
    else:
        get_list(x,y,ai_list,10)
        if is_ai == True:
            for location in ai_list:
                # print(location,depth)                         #测试用
                mapRecord[location[0],location[1]] = -1
                chess_list = chess_list1[:]                                                 #模拟落子
                chess_list.append([location[0],location[1],-1])
                #落子后递归调用继续搜索，更新αβ值
                alpha2,beta2,chess_list2 = ai_search(location[0], location[1], mapRecord, alpha, beta, depth - 1, False,chess_list)
                # print('alpha'+str(alpha2))                    #测试用
                if alpha2 > alpha:
                    chess_list_max = chess_list2[:]
                    alpha = alpha2
                mapRecord[location[0], location[1]] = 0
                if alpha >= beta:
                    cut_count += 1
                    break
            beta = get_score(mapRecord*(-1)) - 5 * get_score(mapRecord)
            return alpha,beta,chess_list_max
        else:
            for location in ai_list:
                # print(location, depth)
                mapRecord[location[0],location[1]] = 1
                chess_list = chess_list1[:]
                chess_list.append([location[0], location[1], 1])
                # 落子后递归调用继续搜索，更新αβ值
                alpha2,beta2,chess_list2 = ai_search(location[0], location[1], mapRecord, alpha, beta, depth - 1, True,chess_list)
                # print('beta'+str(beta2)+'chess_list'+str(chess_list))         #测试用
                if beta2 < beta:
                    beta = beta2
                    chess_list_max = chess_list2[:]
                mapRecord[location[0], location[1]] = 0
                if alpha >= beta:
                    cut_count += 1
                    break
            alpha = get_score(mapRecord*-1) - 5 * get_score(mapRecord)
            return alpha,beta,chess_list_max
    return alpha, beta, chess_list_max              #返回α-β值和模拟落子的路径



#人机对战的实现函数
def ai_playChess(event):
    global mapRecord,over,depth,childMap,search_count,cut_count
    search_count = 0
    cut_count = 0
    x = event.x // pixsize
    y = event.y // pixsize
    if mapRecord[y, x] == 0:                                 #必定我方即白子先手
        child = canvas.create_oval(x * pixsize,
                                   y * pixsize,
                                   x * pixsize + pixsize,
                                   y * pixsize + pixsize, fill='white')
        mapRecord[y, x] = 1
    else:
        return
    down.play()
    childMap.append(child)
    Is_over(mapRecord)
    if over == 1 :
        tk.messagebox.showinfo('game over', 'you beat my ai!')
        clear()
        ai_play()
    else:
        alpha = -9999999999
        beta = 9999999999
        chess_list = []
        #调用α-β剪枝算法
        alpha,beta,chess_list  =ai_search(y,x,mapRecord,alpha,beta,depth,True,chess_list)
        print('search_count ='+str(search_count)+' and cut_count ='+str(cut_count))
        print(alpha,beta,chess_list)
        chess = chess_list[0]
        y = chess[0]
        x = chess[1]
        child = canvas.create_oval(x * pixsize,
                                   y * pixsize,
                                   x * pixsize + pixsize,
                                   y * pixsize + pixsize, fill='black')
        mapRecord[y, x] = -1
        down.play()
        childMap.append(child)
        Is_over(mapRecord)
        if over == 1:
            tk.messagebox.showinfo('game over', 'you lose!')
            clear()
            ai_play()


#音乐播放开关
def music_play():
    global click
    if click:
        bg_music.stop()
        click = False
        music_var.set("背景音乐: 关")
    else:
        bg_music.play(-1)
        click = True
        music_var.set("背景音乐: 开")


#搜索深度选择开关
def choose_depth():
    global d_click,depth
    if d_click:
        d_click = False
        depth = 4
        depth_var.set("ai难度：高")
    else:
        d_click = True
        depth = 2
        depth_var.set("ai难度：低")


#与服务器通信
def send_message():
    global toSend
    global dataSocket
    S = ' '.join(toSend)
    print(S)
    # 发送消息，也要编码为 bytes
    dataSocket.send(S.encode())
    return


#接受服务器消息
def msg_receive():
    global dataSocket,msg,myTurn,mapRecord
    while True:
        msg = dataSocket.recv(BUFLEN)
        if msg.decode() == '1':
            myTurn = True
            msg = '0'
        elif len(msg.decode()) > 2:
            info = msg.decode()
            mapRecord[int(info.split()[0]), int(info.split()[1])] = int(info.split()[2])
            print(int(info.split()[1]),int(info.split()[0]),int(info.split()[2]))
            draw_chess(int(info.split()[1]),int(info.split()[0]),int(info.split()[2]))
            msg = '0'


#双人对战开关
def self_play():
    clear()
    canvas.bind("<Button-1>", self_playChess)


#网络对战开关
def two_play():
    global dataSocket
    clear()
    # 实例化一个socket对象，指明协议
    dataSocket = socket(AF_INET, SOCK_STREAM)
    # 连接服务端socket
    dataSocket.connect((IP, SERVER_PORT))
    dataSocket.send('1'.encode())
    th = Thread(target=msg_receive)
    th.setDaemon(True)
    th.start()
    canvas.bind("<Button-1>", two_playChess)


#ai对战开关
def ai_play():
    clear()
    canvas.bind("<Button-1>", ai_playChess)


#清空棋盘开关
def clear():
    global childMap
    global mapRecord
    mapRecord = np.zeros((15,15))
    for child in childMap:
        canvas.delete(child)
    childMap.clear()


#控制音乐播放
music_var = tk.StringVar()
music_var.set("背景音乐: 开")
click = True
#调用pygame播放音乐
pygame.mixer.init()
bg_music = pygame.mixer.Sound("bg_music.mp3")
down = pygame.mixer.Sound("down.mp3")
bg_music.play(-1)
bg_button = tk.Button(frame_r, anchor="n", textvariable=music_var, width=10, command=music_play)
bg_button.pack()

#按钮布置
twoPlay_button = tk.Button(frame_r, command = self_play, text="双人对战", width=30, font=('Times', 20, 'bold'))
twoPlay_button.pack()
twoPlay_button = tk.Button(frame_r, command = two_play, text="网络对战", width=30, font=('Times', 20, 'bold'))
twoPlay_button.pack()
twoPlay_button = tk.Button(frame_r, command = ai_play, text="对战ai", width=30, font=('Times', 20, 'bold'))
twoPlay_button.pack()
depth_var = tk.StringVar()
depth_var.set("ai难度：低")
choose_button = tk.Button(frame_r, command = choose_depth, textvariable= depth_var, width=30, font=('Times', 20, 'bold'))
choose_button.pack()
clear_button = tk.Button(frame_r, command = clear, text="清空棋盘", width=30, font=('Times', 20, 'bold'))
clear_button.pack()
quit_button = tk.Button(frame_r, command = exit, text="安全退出", width=30, font=('Times', 20, 'bold'))
quit_button.pack()

#绘制窗口
draw_map()
top.mainloop()