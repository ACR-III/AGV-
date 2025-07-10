import random
import time
from config import config
from asearch import A_Search, point
import task_generator
from PyQt5.QtWidgets import QDialogButtonBox, QDialog, QMainWindow, QGridLayout, QTextEdit, QLineEdit, QWidget, \
    QMessageBox, QApplication, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, QBasicTimer
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
import json

from entity import AGV
from entity import DownPoint
from entity import UpPoint
import matplotlib.pyplot as plt

Sequence_start_point = {}  # 序列起始点
Sequence_end_point = {}  # 序列终点


class MapBoard(QMainWindow):  # 可视化类，pyqt5进行编写。
    def __init__(self):
        print('初始化地图...')
        self.Map = []
        for i in range(config.HEIGHT):
            col = []
            for j in range(config.WIDTH):
                col.append(0)
            self.Map.append(col)
        self.count = 0
        self.time_count = 0

        self.busy = 0
        #self.movement = []
        self.distancesum = 0
        self.task1 = 1
        self.average1 = 0
        self.no_hypotenuse = False
        
        for i in range(config.HEIGHT): #让我看看有多少取货点
            if i==1:
                config.check+=1
                config.pick.append(0) #逻辑  #config.MaxloadP开局送货点都是0
                config.pick1.append(0) #物理
            elif (i-1)%3==0:
                config.check+=1
                config.pick.append(0) #逻辑
                config.pick1.append(0) #物理
        
        print("载货点个数：" , config.check)
        config.cargo=config.cargoMax #实时的货物总数等于最大货物总数
        
        #config.distriCenter = (int)(config.MaxloadP * config.check*config.kn) #计算出分发中心的容积
        
        if config.distriCenterCurr == 0:
            config.distriCenterCurr = 0#config.distriCenter
            
            for i in range(len(config.START_POINT)):
                if config.cargo > config.MaxloadP:
                    config.cargo-=config.MaxloadP 
                    config.pick[i] = config.MaxloadP#填满逻辑取货点
                    config.pick1[i] = config.MaxloadP#填满物理取货点
                else:
                    config.pick[i] = config.cargo#填满逻辑取货点
                    config.pick1[i] = config.cargo#填满物理取货点
                    config.cargo=0
        
        # if config.distriCenter == config.distriCenterCurr: #如果分发中心是满的           
        #     for i in range(config.check):
        #         config.distriCenterCurr-=config.MaxloadP
        #         config.pick[i] = config.MaxloadP#填满逻辑取货点
        #         config.pick1[i] = config.MaxloadP#填满物理取货点
        # if config.distriCenterCurr < config.distriCenter: #继续取货填满分发中心
        #     cur = config.distriCenter-config.distriCenterCurr #计算出少的部分
        #     config.cargo-=cur
        #     config.distriCenterCurr+=cur #填满分发中心
        
        
        
        #config.distriCenterCurr =config.distriCenter 
        
        for i in range(config.WIDTH): #让我看看有多少横向卸货点 3,6,9,12,...,3n <=width
            if  i==0:
                continue
            
            elif i%3==0:
                config.checkR+=2
                config.relW1.append(0)
                config.relW2.append(0)
                config.checkR1+=1
        for i in range(config.HEIGHT-1): #让我看看有多少竖向的卸货点 2,2+3,2+3*2,...2+3n < Height-1
            if i==2:
                config.checkR+=1
                config.relH.append(0)
                config.checkR2+=1
            elif (i-2)%3==0:
                config.checkR+=1
                config.relH.append(0)
                config.checkR2+=1  
        print("卸货点个数：" , config.checkR)   
        
        # for i in range((int)(config.HEIGHT/3)-1): #数多少个停车点        
        #     for j in range((int)(config.WIDTH/3)-1): #设定停车场坐标
        #         config.STOP_POINT.append((config.parX,config.parY))
        #         config.parY+=3 
        #     config.parX+=3
        #     config.parY=3

        for i in range((int)(config.WIDTH/3)-1): #数多少个停车点        
            for j in range((int)(config.HEIGHT/3)): #设定停车场坐标
                config.STOP_POINT_TEMP.append((config.parY_t,config.parX_t))
                config.parY_t+=2
            config.parX_t+=2
            config.parY_t=3
        
        for i in range((int)(config.WIDTH/3)-1): #数多少个停车点        
            for j in range((int)(config.HEIGHT/3)): #设定停车场坐标
                config.STOP_POINT.append((config.parY,config.parX))
                config.parY+=3
            config.parX+=3
            config.parY=1
        #坐标都是（3，3）（3，6）.....（9，3）（9，6）
        
        # 初始化AGV列表
        self.agvList = []
        for i in range(config.MAX_ROBOT_COUNT):
            agv = AGV()
            agv.currentPos = config.STOP_POINT[i]  # 设置AGV当前位置
            if i < config.loadPM/2:
                agv.task = task_generator.generate_task()  # 设置AGV当前任务
                agv.endPos = ((config.MaxPickPoint,0)) #agv.task.getNextDestination()  # 根据设置的任务设置下一个要前往的目的地位置
                
            else:
                agv.endPos = config.STOP_POINT[i]
            self.agvList.append(agv)
            agv.stationR = config.endPos1
            agv.taskFinish = 0
            agv.fast = 1
            agv.tempPos =((-1,-1))
            agv.prevPos = config.STOP_POINT[i]
                
        
       
        
        
        # 设置AGC的颜色
        self.colorList = []
        for i in range(config.MAX_ROBOT_COUNT):
            # self.colorList.append((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            # 修改机器人的绘制颜色
            #self.movement.append(1)
            self.colorList.append((90, 193, 250))

        self.downPointList = []
        for i in range(len(config.END_POINT)):
            downPoint = DownPoint()
            downPoint.pos = config.END_POINT[i]
            self.downPointList.append(downPoint)

        self.upPointList = [] #上货点的
        for i in range(len(config.START_POINT)):
            upPoint = UpPoint()
            upPoint.pos = config.START_POINT[i]
            self.upPointList.append(upPoint)

        
        self.search = None
        self.centerTimer = None
        self.yi = None
        self.special = None
        self.ri = None
        self.rPath = []
        self.displayFlush = False

        super().__init__()
        print('初始化UI...')
        self.initUI()

    def initUI(self):
        # 开始初始化UI部分
        # 创建UI控件
        #self.label_tips_v = QLabel("平均搬运路程：", self)
        self.label_tips_v_average = QLabel("", self)
        self.label_tips_l = QLabel(
            "<p style='color:green'>使用说明：</p>单击鼠标左键选定格子为墙壁或删除墙壁。\n<p style='color:green'>颜色说明：</p>\n彩色格子代表机器人，灰色表起点，绿色代表终点，黑色代表墙壁。",
            self)
        self.label_tips = QLabel("搬运数量：" + str(self.count), self)
        self.label_tips1 = QLabel("繁忙者：" + str(self.count), self)
        self.label_tips2 = QLabel("机器人数量：" + str(config.MAX_ROBOT_COUNT), self)
        
        self.label_tipsMaxCargo = QLabel("所有货物数量：" + str(config.cargoMax), self)
        self.label_tipsCar = QLabel("路上的货物：" + str(config.MaxloadP*config.check), self)
        self.label_tipsLoad = QLabel("单次补货最大件数：" + str(config.distriCenter), self)
        self.label_tipsProcess = QLabel("补货次数：" + str(config.orderProcessing), self)
            
        
        self.label_time = QLabel("时间：", self)
        self.label_time_s = QLabel("", self)
        self.label_display = QLabel("", self)
        self.button_start = QPushButton("开始搜索（无限制）", self)
        #self.button_clearSE = QPushButton("重选起始点", self)
      #  self.button_clearWall = QPushButton("清空障碍", self)
        # self.button_statistics = QPushButton("载货点统计图", self)
        # self.button_statistics1 = QPushButton("卸货点统计图", self)
      #  self.button_search_four = QPushButton("开始搜索（禁止斜线）", self)
        # self.button_maplength = QPushButton("设置格子边长", self)
        # self.button_saveMap = QPushButton("保存地图", self)
        # self.button_loadMap = QPushButton("加载地图", self)

        # 设置控件属性
        #self.label_tips_v.setWordWrap(True)
        self.label_tips_l.setWordWrap(True)
        self.label_tips.setWordWrap(True)
        self.label_tips1.setWordWrap(True)
        self.label_tips2.setWordWrap(True)
        self.label_tipsMaxCargo.setWordWrap(True) #总剩余的货物数量
        self.label_tipsCar.setWordWrap(True) #当前没有到站的货物有多少
        self.label_tipsProcess.setWordWrap(True) #已经处理的订单数量
        self.label_tipsLoad.setWordWrap(True) #分发中心负载
        self.label_tips2.setWordWrap(True)
        #self.label_tips_v_average.setWordWrap(True)
        self.label_tips.setFont(QFont('times', 12, QFont.Black))
        self.label_tips1.setFont(QFont('times', 12, QFont.Black))
        self.label_tips2.setFont(QFont('times', 12, QFont.Black))
        
        self.label_tipsMaxCargo.setFont(QFont('times', 12, QFont.Black))
        self.label_tipsCar.setFont(QFont('times', 12, QFont.Black))
        self.label_tipsProcess.setFont(QFont('times', 12, QFont.Black))
        self.label_tipsLoad.setFont(QFont('times', 10, QFont.Black))
        
        #self.label_tips_v.setFont(QFont('times', 12, QFont.Black))
        self.label_time.setFont(QFont('times', 12, QFont.Black))
        self.label_time_s.setFont(QFont('times', 12, QFont.Black))
       #self.label_tips_v_average.setFont(QFont('times', 12, QFont.Black))
        self.label_display.setWordWrap(True)
        # 设置控件样式
        self.label_display.setStyleSheet("border:1px solid black")
        self.label_display.setAlignment(Qt.AlignLeft)
        self.label_display.setAlignment(Qt.AlignTop)
        # 设置控件的尺寸和位置
        #self.label_tips_v.resize(200, 150)
        self.label_tips_l.resize(200, 1900)
        
        self.label_tips.resize(200, 350)
        self.label_tips1.resize(200, 200)
        self.label_tips2.resize(200, 150)
        
        self.label_tipsMaxCargo.resize(200, 100)
        
        self.label_tipsCar.resize(200, 450)
        
        self.label_tipsProcess.resize(200, 550)
        self.label_tipsLoad.resize(200, 500)
        
        self.label_time_s.resize(200, 30)
        #self.label_tips_v_average.resize(200, 150)
        # self.button_saveMap.resize(80, 30)
        # self.button_loadMap.resize(80, 30)
        self.label_display.resize(200, 200)
        self.button_start.resize(200, 30)
       # self.button_clearSE.resize(200, 30)
      #  self.button_clearWall.resize(200, 30)
        # self.button_statistics.resize(200, 30)
        # self.button_statistics1.resize(200, 30)
      #  self.button_search_four.resize(200, 30)
        # self.button_maplength.resize(150, 30)

        #self.label_tips_v.move(100 + (config.WIDTH - 1) * config.blockLength, 130)
        #self.label_tips_v_average.move(270 + (config.WIDTH - 1) * config.blockLength, 130)
        self.label_tips_l.move(100 + (config.WIDTH - 1) * config.blockLength, 0)
        self.label_tips.move(100 + (config.WIDTH - 1) * config.blockLength, 0)
        self.label_tips1.move(100 + (config.WIDTH - 1) * config.blockLength, 0)
        self.label_tips2.move(100 + (config.WIDTH - 1) * config.blockLength, 0)
        
        self.label_tipsMaxCargo.move(100 + (config.WIDTH - 1) * config.blockLength, 0)
        self.label_tipsCar.move(100 + (config.WIDTH - 1) * config.blockLength, 0)
        self.label_tipsProcess.move(100 + (config.WIDTH - 1) * config.blockLength, 0)
        self.label_tipsLoad.move(100 + (config.WIDTH - 1) * config.blockLength, 0)
        
        self.label_time.move(100 + (config.WIDTH - 1) * config.blockLength, 130)
        self.label_time_s.move(170 + (config.WIDTH - 1) * config.blockLength, 130)
        self.label_display.move(100 + (config.WIDTH - 1) * config.blockLength, 600)
        self.button_start.move(100 + (config.WIDTH - 1) * config.blockLength, 300)
        #self.button_clearSE.move(100 + (config.WIDTH - 1) * config.blockLength, 400)
       # self.button_clearWall.move(100 + (config.WIDTH - 1) * config.blockLength, 450)

        # 生成统计图
        # self.button_statistics.move(100 + (config.WIDTH - 1) * config.blockLength, 500)
        # self.button_statistics1.move(100 + (config.WIDTH - 1) * config.blockLength, 550)

       # self.button_search_four.move(100 + (config.WIDTH - 1) * config.blockLength, 350)
        # 设置格子边长
        # self.button_maplength.move(100 + (config.WIDTH - 1) * config.blockLength, 500)
        # self.button_saveMap.move(100 + (config.WIDTH - 1) * config.blockLength, 450)
        # self.button_loadMap.move(200 + (config.WIDTH - 1) * config.blockLength, 450)
        # 给控件绑定事件
        self.button_start.clicked.connect(self.button_StartEvent)
      #  self.button_clearSE.clicked.connect(self.button_Clear)
      #  self.button_clearWall.clicked.connect(self.button_Clear)
        # self.button_statistics.clicked.connect(self.button_PltShow)
        # self.button_statistics1.clicked.connect(self.button_PltShow1)
        #self.button_search_four.clicked.connect(self.button_StartEvent_four)
        # self.button_saveMap.clicked.connect(self.button_SaveMap)
        # self.button_loadMap.clicked.connect(self.button_LoadMap)
        # UI初始化完成
        self.setGeometry(0, 0, 150 + (config.WIDTH * config.blockLength - config.blockLength) + 200,
                         150 + (config.HEIGHT * config.blockLength - config.blockLength))
        self.setMinimumSize(150 + (config.WIDTH * config.blockLength - config.blockLength) + 200,
                            150 + (config.HEIGHT * config.blockLength - config.blockLength))
        self.setMaximumSize(150 + (config.WIDTH * config.blockLength - config.blockLength) + 200,
                            150 + (config.HEIGHT * config.blockLength - config.blockLength))
        self.setWindowTitle('AGV仿真程序')
        self.show()

    def addDisplayText(self, text):
        if self.displayFlush:
            self.label_display.setText(text + '\n')
            self.displayFlush = False
        else:
            self.label_display.setText(self.label_display.text() + text + '\n')

    # def mousePressEvent(self, event):
    #     x, y = event.x() - 50, event.y() - 50
    #     x = x // config.blockLength
    #     y = y // config.blockLength
    #     if x >= 0 and x < config.WIDTH and y >= 0 and y < config.HEIGHT:
    #         if event.button() == Qt.LeftButton:
    #             if (x, y) != self.startPoint and (x, y) != self.endPoint:
    #                 self.Map[y][x] = (1 if self.Map[y][x] == 0 else 0)
    #         self.repaint()

    def button_StartEvent(self):
        sender = self.sender()
        print(sender)
        if len(self.agvList) != 0:
            if self.centerTimer == None:
                self.centerTimer = QBasicTimer()
            self.button_start.setEnabled(False)
           # self.button_clearSE.setEnabled(False)
          #  self.button_clearWall.setEnabled(False)
            # self.button_statistics.setEnabled(True)
           # self.button_search_four.setEnabled(False)

            self.centerTimer.start(100, self)
            self.no_hypotenuse = False
            self.ri = self.start_Search()

            self.addDisplayText('开始进行搜索')
            config.start=-config.start
    def button_StartEvent_four(self):
        sender = self.sender()
        print(sender)
        if self.startPoint != None and self.endPoint != None:
            if self.centerTimer == None:
                self.centerTimer = QBasicTimer()
            self.button_start.setEnabled(False)
           # self.button_clearSE.setEnabled(False)
           # self.button_clearWall.setEnabled(False)
            # self.button_statistics.setEnabled(True)
            #self.button_search_four.setEnabled(False)
            self.centerTimer.start(100, self)
            self.no_hypotenuse = True
            self.ri = self.start_Search()
            
            self.addDisplayText('开始进行搜索')

    def button_statistics_event(self):

        plt.rcParams['font.sans-serif'] = ['SimHei']

        plt.figure(figsize=(20, 10), dpi=100)
        # game = ['1-G1', '1-G2', '1-G3', '1-G4', '1-G5', '2-G1', '2-G2', '2-G3', '2-G4', '2-G5', '3-G1', '3-G2', '3-G3',
        #         '3-G4', '3-G5', '总决赛-G1', '总决赛-G2', '总决赛-G3', '总决赛-G4', '总决赛-G5', '总决赛-G6']
        # game = config.END_POINT
        # print(config.END_POINT)
        # lst = list(range(len(END_POINT)))
        # game = lst
        game = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
        scores = [23, 10, 38, 30, 36, 20, 28, 36, 16, 29, 15, 26, 30, 26, 38, 34, 33, 25, 28, 40, 28]
        rebounds = [17, 6, 12, 6, 10, 8, 11, 7, 15, 11, 6, 11, 10, 9, 16, 13, 9, 10, 12, 13, 14]
        assists = [16, 7, 8, 10, 10, 7, 9, 5, 9, 7, 12, 4, 11, 8, 10, 9, 9, 8, 8, 7, 10]
        plt.plot(game, scores, c='red', label="1号")
        plt.plot(game, rebounds, c='green', linestyle='--', label="2号")
        plt.plot(game, assists, c='blue', linestyle='-.', label="3号")
        plt.scatter(game, scores, c='red')
        plt.scatter(game, rebounds, c='green')
        plt.scatter(game, assists, c='blue')
        plt.legend(loc='best')
        plt.yticks(range(0, 50, 5))
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.xlabel("接收点", fontdict={'size': 16})
        plt.ylabel("数量", fontdict={'size': 16})
        plt.title("各个接受点接收数量", fontdict={'size': 20})
        plt.show()
    
    
   
    def start_Search(self):
        # 一直运行直到搬运数量达到8000件
        start_time = time.time() #计时工具
        while 1:
            # 用于记录每个机器人下一步的坐标
            nextStepList = []
                         
            # 卸货点货物堆积数量超过config.MaxloadR
            for i in range(len(self.downPointList)):
                if self.downPointList[i].goodsCount >= config.MaxloadR: 
                    self.downPointList[i].removeGoods()

            for i in range(len(self.agvList)):
                self.colorList[i] = (90, 193, 250)  # 没有啥事，就是浅蓝色！
                # print(self.agvList[i].endPos)
                if self.agvList[i].endPos in config.END_POINT:# 谁有任务，变紫色
                    self.colorList[i] = (180, 40, 210)  # 手上有任务变粉色
                    
                # 如果机器人的出发点和终点不一样，执行一次A*算法，算出下一步的坐标
                if self.agvList[i].currentPos != self.agvList[i].endPos and self.agvList[i].endPos != (-1, -1):
                    
                    
                    # 判断AGV的终点是否已经被其它AGV给占据
                    destinationOccupied = False
                    for k in range(len(self.agvList)):
                        if self.agvList[i].endPos == self.agvList[k].currentPos:
                            destinationOccupied = True
                            break

                    downPointClosed = False  # 判断卸货点是否被关闭
                    downPointNumber = -1  # 卸货点的编号
                    # 查询目的地是否为卸货点
                    for k in range(len(self.downPointList)):
                        if self.agvList[i].endPos == self.downPointList[k].pos:
                            downPointNumber = k
                            break
                        
                    # 如果目的地是一个卸货点，且卸货点已经被关闭，则将标志为设为true
                    if downPointNumber != -1 and downPointNumber < len(self.downPointList):
                        if self.downPointList[downPointNumber].status == 1:
                            downPointClosed = True
                            
                    #upPointZero = False
                    # 如果AGV的终点已经被占据，减速靠近
                    if destinationOccupied or downPointClosed :#or upPointZero:
                        
                        if destinationOccupied ==True:
                            for k in range(len(self.agvList)):
                                
                                if self.agvList[i].endPos == self.agvList[k].currentPos: #被占了终点
                                    
                                    if self.agvList[i].fast==1: 
                                        self.agvList[i].fast=0
                                        
                                    if self.agvList[i].endPos[1]==0 and ((self.agvList[i].endPos[0]-1)%3==0 or self.agvList[i].endPos[0] == 0): #有人占了载货点
                                    #直接让它对齐载货点!
                                            if self.agvList[i].currentPos[0]!=self.agvList[i].endPos[0] :#and self.agvList[i].endPos != (0,0) and self.agvList[i].endPos != (config.HEIGHT-1,0):
                                                if self.agvList[i].endPos[0] > self.agvList[i].currentPos[0]:
                                                    nextStep = (self.agvList[i].currentPos[0]+1,self.agvList[i].currentPos[1])
                                                elif self.agvList[i].endPos[0] < self.agvList[i].currentPos[0]:
                                                    nextStep = (self.agvList[i].currentPos[0]-1,self.agvList[i].currentPos[1]) #让她上下移动就行了
                                            elif (int)(self.agvList[i].currentPos[1]) >= config.saftyPos: #目标距离大于安全距离的时候，让他可以靠近
                                                nextStep = (self.agvList[i].currentPos[0],self.agvList[i].currentPos[1]-1)
                                            
                                           # print("正在靠近")
                                                #靠近
                                        # elif self.agvList[i].endPos == (0,0): #讨论在边边角角的两种情况         
                                        #     if self.agvList[i].endPos[0]+1 < self.agvList[i].currentPos[0]:
                                        #         nextStep = (self.agvList[i].currentPos[0]-1,self.agvList[i].currentPos[1]) #让她上移,直到(1,x),与上面始终距离一个单位
                                        #     elif self.agvList[i].currentPos[1] >= config.saftyPos: #目标距离大于安全距离的时候，让他可以靠近
                                        #         nextStep = (self.agvList[i].currentPos[0],self.agvList[i].currentPos[1]-1)
                                        
                                        # elif self.agvList[i].endPos == (config.HEIGHT-1,0):  #讨论在边边角角的两种情况
                                        #     if self.agvList[i].endPos[0]-1 < self.agvList[i].currentPos[0]:
                                        #         nextStep = (self.agvList[i].currentPos[0]-1,self.agvList[i].currentPos[1]) #让她下移,直到(H-2,x),与下面始终距离一个单位
                                        #     elif self.agvList[i].currentPos[1] >= config.saftyPos: #目标距离大于安全距离的时候，让他可以靠近
                                        #         nextStep = (self.agvList[i].currentPos[0],self.agvList[i].currentPos[1]-1)
                                                
                                    else : #有人占了卸货点  #(self.agvList[i].endPos[1]%3 == 0 and (self.agvList[i].endPos[0] == config.HEIGHT or self.agvList[i].endPos[0] == 0)) 
                                        
                                        #计算机器与卸货点的物理距离
                                        A1=(self.agvList[i].currentPos[0])
                                        A2=(self.agvList[i].currentPos[1])
                                        
                                        B1=(self.agvList[i].endPos[0])
                                        B2=(self.agvList[i].endPos[1])
                                        #高中数学公式：：：：
                                        
                                        L1=(int)(pow((pow((A1-B1),2) + pow((A2-B2),2)),0.5)) #求距离公式
                                        
                                        if L1 >= config.saftyPos : #如果大于安全距离，就可以靠近
                                            search = A_Search(point(self.agvList[i].currentPos[0], self.agvList[i].currentPos[1]),
                                            point(self.agvList[i].endPos[0], self.agvList[i].endPos[1]),
                                            self.Map,
                                            self.no_hypotenuse)  # no_hypotenuse为禁止走斜边的标志，设置为True将禁止走斜边
                                            nextStep = search.process()
                                            if nextStep == None:
                                                    print(str(i) + "号小车" + "触发空坐标保护" + str(self.agvList[i].currentPos))
                                                    nextStep = self.agvList[i].currentPos
                                                    #nextStepList.append(self.agvList[i].currentPos)  
                                        elif L1 <= config.saftyPos :#and self.agvList[i].currentPos[1]!=0 and (self.agvList[i].endPos[0]-1)%3!=0: #如果小于安全距离，并且堵路了别动
                                            #if (self.agvList[i].endPos[0] == config.HEIGHT-1 and self.agvList[i].endPos[1] < config.WIDTH/4) or (self.agvList[i].endPos[0] == 0 and self.agvList[i].endPos[1] < config.WIDTH/4):
                                            if (self.agvList[i].currentPos[1] == 0 and self.agvList[i].endPos[1] < config.WIDTH/4):
                                                search = A_Search(point(self.agvList[i].currentPos[0], self.agvList[i].currentPos[1]),
                                                point(self.agvList[i].endPos[0], self.agvList[i].endPos[1]),
                                                self.Map,
                                                self.no_hypotenuse)  # no_hypotenuse为禁止走斜边的标志，设置为True将禁止走斜边
                                                nextStep = search.process()
                                                if nextStep == None:
                                                    print(str(i) + "号小车" + "触发空坐标保护" + str(self.agvList[i].currentPos))
                                                    nextStep = self.agvList[i].currentPos
                                                    #nextStepList.append(self.agvList[i].currentPos)  
                                                
                                            else:
                                                nextStep = self.agvList[i].currentPos
                                                                                                   
                        #if downPointClosed ==True:
                        if downPointNumber != -1 and downPointNumber < len(self.downPointList):
                                
                                if self.downPointList[downPointNumber].status != 1: #down点没有被占                       
                            #上下卸货点压着了
                                    if ((self.agvList[i].currentPos[1]%3 == 0) and (self.agvList[i].currentPos[0] == 0 or self.agvList[i].currentPos[1]==config.HEIGHT-1)) :
                                #赶紧走
                                        search = A_Search(point(self.agvList[i].currentPos[0], self.agvList[i].currentPos[1]),
                                            point(self.agvList[i].endPos[0], self.agvList[i].endPos[1]),
                                            self.Map,
                                            self.no_hypotenuse)  # no_hypotenuse为禁止走斜边的标志，设置为True将禁止走斜边
                                        nextStep = search.process()
                                        if nextStep == None:
                                                    print(str(i) + "号小车" + "触发空坐标保护" + str(self.agvList[i].currentPos))
                                                    nextStep = self.agvList[i].currentPos
                                                    #nextStepList.append(self.agvList[i].currentPos)  
                                        
                                        downPointClosed = True
                             #竖直卸货点压着了   
                                    elif ((self.agvList[i].currentPos[1]%3 == 0) and ((self.agvList[i].currentPos[0]+1)%3 == 0)) :
                                #赶紧走
                                        search = A_Search(point(self.agvList[i].currentPos[0], self.agvList[i].currentPos[1]),
                                            point(self.agvList[i].endPos[0], self.agvList[i].endPos[1]),
                                            self.Map,
                                            self.no_hypotenuse)  # no_hypotenuse为禁止走斜边的标志，设置为True将禁止走斜边
                                        nextStep = search.process()
                                        if nextStep == None:
                                                    print(str(i) + "号小车" + "触发空坐标保护" + str(self.agvList[i].currentPos))
                                                    nextStep = self.agvList[i].currentPos
                                                    #nextStepList.append(self.agvList[i].currentPos)  
                                        downPointClosed = True
                                    # for k in range(len(self.agvList)): #down点被人用了
                                    #     if self.agvList[i].endPos == self.agvList[k].currentPos:
                                            
                        #if upPointZero ==True:
                            
                                elif self.downPointList[downPointNumber].status == 1: #down点被占
                                    
                                    search = A_Search(point(self.agvList[i].currentPos[0], self.agvList[i].currentPos[1]),
                                          point(self.agvList[i].endPos[0], self.agvList[i].endPos[1]),
                                          self.Map,
                                          self.no_hypotenuse)  # no_hypotenuse为禁止走斜边的标志，设置为True将禁止走斜边    
                                    nextStep = search.process()
                                    if nextStep == None:
                                                    print(str(i) + "号小车" + "触发空坐标保护" + str(self.agvList[i].currentPos))
                                                    nextStep = self.agvList[i].currentPos
                                                    #nextStepList.append(self.agvList[i].currentPos)  
                                      
                                    if nextStep == self.agvList[i].endPos:
                                        nextStep = self.agvList[i].currentPos  # 下一步是卸货点，就保持不动
                                        #self.agvList[i].noMoveCount += 1  # 记录下保持不动的次数
                                        downPointClosed == True

                                    # nextStep = self.agvList[i].currentPos  # 下一步和当前位置一样，即保持不动
                                    # self.agvList[i].noMoveCount += 1  # 记录下保持不动的次数
                    # 若终点没有被占据，则用A*算法计算下一步的位置
                    else:
                      
                        if 1:
                            search = A_Search(point(self.agvList[i].currentPos[0], self.agvList[i].currentPos[1]),
                                          point(self.agvList[i].endPos[0], self.agvList[i].endPos[1]),
                                          self.Map,
                                          self.no_hypotenuse)  # no_hypotenuse为禁止走斜边的标志，设置为True将禁止走斜边
                        else:    
                            search = A_Search(point(self.agvList[i].currentPos[0], self.agvList[i].currentPos[1]),
                                          point(self.agvList[i].endPos[0], self.agvList[i].endPos[1]),
                                          self.Map,
                                          True)  # no_hypotenuse为禁止走斜边的标志，设置为True将禁止走斜边
                        nextStep = search.process()
                        if nextStep == None:
                                print(str(i) + "号小车" + "触发空坐标保护" + str(self.agvList[i].currentPos))
                                nextStep = self.agvList[i].currentPos
                                #nextStepList.append(self.agvList[i].currentPos)  


                        # 如果因为不可达而没有返回下一步的路径，则保持不动
                        if not nextStep:
                            nextStep = self.agvList[i].currentPos
                        
                        self.agvList[i].noMoveCount = 0  # 因为本次移动了，所以将保持不动的次数清零

                    if nextStep == self.agvList[i].endPos:  # 如果下一步将到达终点，则开始减速
                        
                        self.colorList[i] = (122, 156, 184)  # 换浅蓝色，要到站了！
                        self.agvList[i].lowSpeedFlags = True
                        

                    t = nextStep[0] - self.agvList[i].currentPos[0]
                    k = nextStep[1] - self.agvList[i].currentPos[1]
                    
                    if (t, k) != self.agvList[i].direction:  # 计算方向向量，如果判断出和上一步的方向不同，则开始减速
                        if self.agvList[i].direction != (0, 0):
                            self.agvList[i].lowSpeedFlags = True
                        self.agvList[i].direction = (t, k)

                    if self.agvList[i].lowSpeedFlags:  # 若需要加速或减速，则保持当前位置不动直到加速或减速完毕
                        if self.agvList[i].lowSpeedWait == 0:
                            self.agvList[i].lowSpeedWait = config.ROBOT_ACCELERATION_TIME
                            nextStep = self.agvList[i].currentPos
                        elif self.agvList[i].lowSpeedWait > 1:
                            nextStep = self.agvList[i].currentPos
                            self.agvList[i].lowSpeedWait -= 1
                        elif self.agvList[i].lowSpeedWait == 1:
                            self.agvList[i].lowSpeedWait = 0
                            self.agvList[i].lowSpeedFlags = False

                    if self.agvList[i].currentPos == self.agvList[i].previousStart:  # 如果上一步是出发点，则开始加速
                        self.agvList[i].lowSpeedFlags = True

                    #如果机器不动，应该首先判断是不是占了别人的取货点，是不是来取货的
                    
                    for j in range(len(nextStepList)): 
                        
                        if (nextStep == self.agvList[j].prevPos and self.agvList[j].lowSpeedFlags == True): #碰到减速进站的，要让行
                            nextStep = self.agvList[i].currentPos
                    
                    if self.agvList[i].noMoveCount > 25:
                        
                        #if self.agvList[i].endPos[0]/3 == 0 and self.agvList[i].endPos[1] == 0:# 小车是来取货的
                        #    config.pick[(int)(self.agvList[i].endPos[0]/3)] += 1 #恢复原来的逻辑坐标的货物
                        #
                        # 用回光返照算法
                        self.agvList[i].noMoveCount = 0                     
                        #self.agvList[i].endPos = config.START_POINT[random.randint(0, len(config.START_POINT) - 1)]
                        pos1 = self.agvList[i].currentPos
                        print(str(i)+"号小车堵车，坐标"+"->"+str(pos1))
                        
                    point.clear()

                    # 冲突处理，如果检查到下一步两个机器人的坐标相同，让一个机器人本次不动，保持在出发点位置
                    for j in range(len(nextStepList)):
                        
                        # if (nextStep == self.agvList[j].prevPos and self.agvList[j].lowSpeedFlags == True): #碰到减速进站的，要让行
                        #     nextStep = self.agvList[i].currentPos
                            
                        if nextStep != nextStepList[j]:

                            continue
                        else:
                            nextStep = self.agvList[i].currentPos
                            
                            if destinationOccupied == False:
                                self.colorList[j] = (210, 40, 40)  # 你变红
                                self.colorList[i] = (210, 40, 40)  # 我变红
                                
                            self.agvList[i].noMoveCount += 1  # 记录下保持不动的次数
                            self.agvList[j].noMoveCount += 1  # 记录下保持不动的次数
                            break
                    
                    self.agvList[i].prevPos = self.agvList[i].currentPos #要到下一步坐标了
                    nextStepList.append(nextStep)
                else:
                    nextStepList.append(self.agvList[i].currentPos)

            for i in range(len(self.agvList)):
                for j in range(len(self.agvList)):
                    # 冲突处理，如果下一步坐标已经被另一个机器人占据，则保持不动
                    if i != j and nextStepList[i] == nextStepList[j]:
                        nextStepList[i] = self.agvList[i].currentPos
                        break
            
            if nextStep == self.agvList[i].currentPos:
                self.agvList[i].noMoveCount+=1
            

            
            for i in range(len(self.agvList)):
                if self.agvList[i].currentPos != self.agvList[i].endPos and self.agvList[i].endPos != (-1, -1) and self.agvList[i].lowSpeedFlags != True:
                    # 更新地图，将上一步坐标的障碍标记清除，因为现在机器人将会离开这个坐标
                    self.Map[self.agvList[i].currentPos[0]][self.agvList[i].currentPos[1]] = 0
                    # 将机器人的新的出发点设为下一步的坐标
                    self.agvList[i].currentPos = nextStepList[i]
                else: #减速的机器人默认他占领两个坐标
                    self.Map[self.agvList[i].currentPos[0]][self.agvList[i].currentPos[1]] = 1
                    self.agvList[i].currentPos = nextStepList[i]
            for i in range(len(self.agvList)):
                # 因为机器人已经移动到了下一步的坐标，所以将该处坐标的障碍标记置1
                self.Map[self.agvList[i].currentPos[0]][self.agvList[i].currentPos[1]] = 1

           #min = int(self.time_count / 60)
           
            sec = self.time_count

            if (sec % config.timeDis == 0 and sec > 0): # and config.distriCenterCurr>0: #直接从分发中心补满载货点货物
                
                task_generator.reflush()
                if config.cargo >= config.distriCenter:
                    print("正在补满载货点货物")
                    config.orderProcessing+=1
                    config.distriCenterCurr = config.distriCenter#30件货
                    #config.cargo-=config.distriCenter
                #row = 0 #统计循环次数，防止死锁
                elif config.cargo>0 and config.distriCenter > config.cargo:
                    print("已经全部补满载货点货物")
                    config.orderProcessing+=1
                    config.distriCenterCurr = config.cargo#30件货
                    config.cargo==0
                    
                if config.cargo >=0 and config.distriCenterCurr>0:
                    cur = config.distriCenterCurr #一开始有多少货物
                    config.checkPos = (int)(config.check/3) #从中间开始补货
                    while 1:               
                        if (config.pick1[config.checkPos] < config.MaxloadP) and config.distriCenterCurr > 0: #直接补满
                            
                            if config.distriCenterCurr > (config.MaxloadP - config.pick1[config.checkPos]):    
                                temp = config.MaxloadP - config.pick1[config.checkPos] #补满一次物理载货点
                                config.distriCenterCurr -=temp
                                config.pick1[config.checkPos] +=temp                     
                                config.pick[config.checkPos]+=temp #补满逻辑载货点
                                #print("已经补满"+str(config.checkPos)+"号载货点"+"剩余："+str(config.distriCenterCurr))
                                config.cargo -= temp
                                if config.checkPos+1 < config.check:
                                    config.checkPos+=1 #下次访问下一位
                                else:
                                    config.checkPos=0 #回到开头
                                    
                            elif (config.distriCenterCurr <= (config.MaxloadP - config.pick1[config.checkPos])):
                                temp = config.distriCenterCurr
                                config.distriCenterCurr =0
                                config.pick1[config.checkPos] +=temp                     
                                config.pick[config.checkPos]+=temp #补满逻辑载货点
                                #print("已经补"+str(config.checkPos)+"号载货点")
                                config.cargo -= temp
                                if config.checkPos+1 < config.check:
                                    config.checkPos+=1 #下次访问下一位
                                else:
                                    config.checkPos=0 #回到开头 
                                break
                        else: #补满了还有多的，就打道回府送回仓库
                            if config.distriCenterCurr==0 and config.cargo==0:
                                print("已经补满全部货物")
                            else:    
                                print("已经补满"+str(cur - config.distriCenterCurr))
                                config.distriCenterCurr=0
                                break
                        
                        
                        
                config.loadPs=1
                config.loadPM=1
                #print("正在补满载货点货物")
                task_generator.reflush()
                if config.loadPM > 0:
                    for i in range(config.MAX_ROBOT_COUNT):
                        if i+1 > config.loadPs: #防止有多的小车被唤醒
                            break
                        if (self.agvList[i].endPos == config.STOP_POINT[i] or self.agvList[i].endPos == config.STOP_POINT_TEMP[i]) and config.loadPs>0: #把停车的叫醒
                            self.agvList[i].task = task_generator.generate_task()
                            self.agvList[i].stationR = config.endPos1
                            self.agvList[i].endPos = config.startPos1
                            task_generator.reflush()
            
            # 程序执行到此处会暂停，直到页面刷新函数调用“next”
            yield nextStepList

    def button_SaveMap(self):
        with open('map.txt', 'w') as f:
            f.write(json.dumps(self.Map))
            self.addDisplayText('地图保存成功-->map.txt')

    # else:
    # self.addDisplayText('地图保存失败')
    def button_LoadMap(self):
        try:
            with open('map.txt', 'r') as f:
                self.Map = json.loads(f.read())
                config.HEIGHT = len(self.Map)
                config.WIDTH = len(self.Map[0])
                self.addDisplayText('地图加载成功')
                self.repaint()
        except Exception as e:
            print('失败', e, type(e))
            if type(e) == FileNotFoundError:
                self.addDisplayText('地图加载失败:地图文件不存在')
            elif type(e) == json.decoder.JSONDecodeError:
                self.addDisplayText('地图加载失败:错误的地图文件')

    def button_Clear(self):
        sender = self.sender()
     #   print(self.button_clearSE, type(self.button_clearSE))
      #  if sender == self.button_clearSE:
      #      self.repaint()
      #      self.addDisplayText('清空起始点')
#        elif sender == self.button_clearWall:
     #       for i in range(len(self.Map)):
      #          for j in range(len(self.Map[i])):
      #              self.Map[i][j] = 0
     #      self.repaint()
     #       self.addDisplayText('清空所有墙壁')

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawBoard(event, qp)
        qp.end()

    def drawBoard(self, event, qp):
        self.drawMap(qp)

    def drawMap(self, qp):  # 画面绘制方法，每次地图有所改动都将重绘
        time1 = time.time()
        for i in range(len(self.Map)):
            for j in range(len(self.Map[i])):

                i_j_is_agv = False
                i_j_is_endPoint = False

                if self.Map[i][j] == 0:
                    qp.setBrush(QColor(230, 230, 230))
                elif self.Map[i][j] == 1:
                    qp.setBrush(QColor(0, 0, 0))
                
                
                for s in range(len(config.START_POINT)):
                    if (i, j) == config.START_POINT[s]:
                        if ((int)(config.pick[(int)(i/3)]))*config.busyColorC > 250:
                            qp.setBrush(QColor(255, 75, 90)) #取货点
                        else:
                            #qp.setBrush(QColor((config.busyColorC)*(self.upPointList[(int)(i/3)].goodsCount), 75, 90)) #取货点
                            qp.setBrush(QColor((config.busyColorC)*((int)(config.pick[(int)(i/3)])), 75, 90)) #取货点
                        L=(config.blockLength+100)*0.56 #y轴移动距离
                        W=(config.blockLength+100)*0.02 #x轴移动距离
                        
                        #st1=str(self.upPointList[s].goodsCount) #斜线左边是货物逻辑上被小车领走的部分，右边是物理上还存在多少货物
                        st1=str(config.pick1[(int)(i/3)]) #斜线左边是货物逻辑上被小车领走的部分，右边是物理上还存在多少货物
                        st2=str(config.pick[(int)(i/3)])
                        str3= st2 + "|" + st1 #str(config.MaxloadP)
                        qp.drawText((int)(W) + j * config.blockLength, (int)(L) + i * config.blockLength, str(str3)) #画取货点编号
                        break
                   
              
                    
                    
                for t in range(len(config.END_POINT)):
                    if (i, j) == config.END_POINT[t]:
                        i_j_is_endPoint = True
                        qp.setBrush(QColor(100, 200, 50))
                        break
             
                for k in range(len(self.agvList)):
                    if (i, j) == self.agvList[k].currentPos:  ## (i,j)有机器人
                        i_j_is_agv = True
                        # qp.setBrush(QColor(255, 255, 0))
                        qp.setBrush(QColor(self.colorList[k][0], self.colorList[k][1], self.colorList[k][2]))
                        break

                # ======= 开始绘制(i,j)格子 ======
                # 画矩形，参数：x,y,w,h
                if i_j_is_agv:
                    qp.drawEllipse(50 + j * config.blockLength, 50 + i * config.blockLength, config.blockLength,
                                   config.blockLength)
                    L = (config.blockLength + 100) * 0.56  # y轴移动距离
                    W = (config.blockLength + 100) * 0.44  # x轴移动距离
                    qp.drawText((int)(W) + j * config.blockLength, (int)(L) + i * config.blockLength, str(k))  # 画机器人编号
                    # qp.drawText(50 + j * config.blockLength, 50 + i * config.blockLength, str(k))
                    continue
                if i_j_is_endPoint:
                    # 首先计算出该卸货点对应的编号downPointNumber
                    downPointNumber = 0
                    for downPointNumber in range(len(self.downPointList)):
                        if (i, j) == self.downPointList[downPointNumber].pos:
                            break
                    # 如果卸货点处于关闭状态，则用红色画出
                    if self.downPointList[downPointNumber].status == 1:
                        qp.setBrush(QColor(255, 0, 0))
                        qp.setPen(QColor(255, 0, 0))
                    # 如果处于开放状态，则用绿色画出
                    else:
                        qp.setPen(QColor(0, 0, 0))
                        # qp.setPen(QColor(100, 200, 50))  # 用绿色写出卸货点堆积的货物数量
                        qp.setBrush(QColor(100, 200, 50))
                    # L = (config.blockLength + 100) * 0.56  # y轴移动距离
                    # W = (config.blockLength + 100) * 0.44  # x轴移动距离
                    # qp.drawText((int)(W) + j * config.blockLength, (int)(L) + i * config.blockLength,str(self.downPointList[downPointNumber].goodsCount))

                    if i == 0:
                        L = (config.blockLength + 100) * 0.36  # y轴移动距离
                        W = (config.blockLength + 100) * 0.44  # x轴移动距离
                        qp.drawText((int)(W) + j * config.blockLength, (int)(L) + i * config.blockLength,
                                    str(self.downPointList[downPointNumber].goodsCount))
                    elif i == config.HEIGHT-1:
                        L = (config.blockLength + 100) * 0.76  # y轴移动距离
                        W = (config.blockLength + 100) * 0.44  # x轴移动距离
                        qp.drawText((int)(W) + j * config.blockLength, (int)(L) + i * config.blockLength,
                                    str(self.downPointList[downPointNumber].goodsCount))
                    elif j==config.WIDTH-1: #竖卸货点
                        L = (config.blockLength + 100) * 0.56  # y轴移动距离
                        W = (config.blockLength + 100) * 0.64  # x轴移动距离
                        qp.drawText((int)(W) + j * config.blockLength, (int)(L) + i * config.blockLength,
                                    str(self.downPointList[downPointNumber].goodsCount))
                        
                    if (self.downPointList[downPointNumber].goodsCount)*config.busyColor >= 250:
                        qp.setBrush(QColor(255, 200, 40)) #送货点
                    else:
                        qp.setBrush(QColor((config.busyColor)*(self.downPointList[downPointNumber].goodsCount), 200, 40)) #送货点
                        
                    qp.setPen(QColor(0, 0, 0))  # 将画笔的颜色重新设置为黑色的
                    qp.drawRect(50 + j * config.blockLength, 50 + i * config.blockLength, config.blockLength,
                                config.blockLength)
                else:
                    qp.drawRect(50 + j * config.blockLength, 50 + i * config.blockLength, config.blockLength,
                                config.blockLength)
                # ======= 开始绘制(i,j)格子 ======

    # time.sleep(20)
    # print('绘制时间：',time2-time1)
    def timerEvent(self, e):
        try:
            data = next(self.ri)
        except Exception as e:
            self.addDisplayText('搜索结束:')
            print('搜索结束！')
            self.centerTimer.stop()
            self.search = None
            self.yi = None
            self.special = None
            self.rPath.clear()
            self.ri = None
            point.clear()
            self.button_start.setEnabled(True)
        #    self.button_clearSE.setEnabled(True)
        #    self.button_clearWall.setEnabled(True)
            self.displayFlush = True
            print(e)
        else:
            # self.repaint()
            for i in range(len(self.agvList)):
                if self.agvList[i].currentPos == self.agvList[i].endPos or self.agvList[i].endPos == (-1, -1):
                    # Sequence_start_point[self.agvList[i].currentPos] = Sequence_start_point.get(self.agvList[i].currentPos, 0) + 1
                    # Sequence_start_point[Sequence_record_count] = self.startPs[i]
                    # 对每一个机器人的当前位置进行遍历，若机器人在出发点，则等待载货，然后分配一个前往接收点的任务
                    for j in range(len(config.START_POINT)):

                        if self.agvList[i].currentPos == config.START_POINT[j]: #载货点发现机器人
                            config.START_POINTcop[j]=(config.START_POINTcop[j][0],config.START_POINTcop[j][1],1) #设置为有机器人的状态
                            self.agvList[i].previousStart = config.START_POINT[j]
                            
                            if self.agvList[i].load_or_unload_wait_countdown == 0: #时间到，马上搬运货物马上走
                                self.agvList[i].endPos = self.agvList[i].stationR[0]
                                self.agvList[i].taskFinish=0
                                
                                if self.agvList[i].stationR[1] != (-1,-1):
                                    config.pick1[(int)(self.agvList[i].currentPos[0]/3)]-=2 #有机器搬运了，就物理货物-2
                                else:
                                    config.pick1[(int)(self.agvList[i].currentPos[0]/3)]-=1 #有机器搬运了，就物理货物-1
                                    
                            if self.agvList[i].load_or_unload_wait_countdown >= 0:
                                # 等待载货倒计时
                                self.colorList[i] = (180, 40, 210)  # 变紫色
                                self.agvList[i].load_or_unload_wait_countdown -= (1 / config.ROBOT_SPEED)
                            else:
                                nextDestination = self.agvList[i].task.getNextDestination()
                                self.agvList[i].endPos = self.agvList[i].stationR[0]
                                    
                                if nextDestination == (-1, -1):
                                    task_generator.reflush()                               
                                    if config.loadPs !=0: #还有货物
                                        #self.agvList[i].task = task_generator.generate_task()
                                        nextDestination = self.agvList[i].stationR[0] #(-1, -1) # self.agvList[i].task.getNextDestination()
                                    elif config.loadPs ==0:
                                        if self.busy !=0:
                                            nextDestination = config.STOP_POINT_TEMP[i] #先去临时停车点，防止堵路
                                        else: #送完了再去停车点
                                            nextDestination = config.STOP_POINT[i]
                                # 终点设为一个接收点
                                elif nextDestination != (-1, -1):
                                    if self.agvList[i].stationR[1] != (-1,-1):                                  
                                        config.pick1[(int)(self.agvList[i].currentPos[0]/3)]-=2 #有机器搬运了，就物理货物-2
                                    elif self.agvList[i].stationR[1] == (-1,-1):
                                        config.pick1[(int)(self.agvList[i].currentPos[0]/3)]-=1 #有机器搬运了，就物理货物-1
                                        
                                self.agvList[i].endPos = self.agvList[i].stationR[0]
                                # Sequence_end_point[self.agvList[i].endPos] = Sequence_end_point.get(self.agvList[i].endPos, 0) + 1  # 终点序列
                                self.agvList[i].taskFinish=0
                                # 倒计时恢复，以便下一次调用
                                self.agvList[i].load_or_unload_wait_countdown = config.ROBOT_WAIT_TIME
                            break
                        else:
                            config.START_POINTcop[j]=(config.START_POINTcop[j][0],config.START_POINTcop[j][1],0) #这地方没有机器
                            
                    self.busy=0
                    for j in range(config.MAX_ROBOT_COUNT): #让我看看谁最忙
                        if self.agvList[j].endPos[1]!=0 and self.agvList[j].endPos[0]!=-1 and (self.agvList[j].endPos != config.STOP_POINT[j] and self.agvList[j].endPos != config.STOP_POINT_TEMP[j]):#谁有任务，busy+1
                            self.busy+=1
                    
                    for j in range(len(self.downPointList)): #移动货物
                        if self.downPointList[j].goodsCount >= config.MaxloadR: 
                            self.downPointList[j].removeGoods()
                    
                    # 对每一个机器人的当前位置进行遍历，若机器人在接收点，则等待卸货，然后分配一个前往出发点的任务
                    for j in range(len(config.END_POINT)):
                        if self.agvList[i].currentPos == config.END_POINT[j]:
                            
                            self.agvList[i].previousStart = config.END_POINT[j]
                            tig = 0 #分配任务的小指示器
                            
                            if self.agvList[i].load_or_unload_wait_countdown == 0: 
                                self.agvList[i].fast =1#恢复快速模式
                                task_generator.reflush() #刷新一遍货物 
                                self.agvList[i].taskFinish+=1
                                self.count += 1
                                if self.agvList[i].stationR[1]==(-1,-1): #送一次的                        
                                    if config.loadPs !=0:
                                       # self.count += 1#self.agvList[i].task.quantity
                                        self.agvList[i].task = task_generator.generate_task()
                                    if config.loadPs !=0:
                                        #task_generator.reflush() #刷新一遍货物
                                        nextDestination = self.agvList[i].task.getNextDestination()
                                        self.agvList[i].endPos = ((config.MaxPickPoint,0))
                                        self.agvList[i].stationR = config.endPos1
                                        
                                    elif config.loadPs ==0: #停车
                                        if self.busy != 0:
                                            nextDestination = config.STOP_POINT_TEMP[i] #先去临时停车点防止堵路
                                        else:
                                            nextDestination = config.STOP_POINT[i]
                                        self.agvList[i].endPos = nextDestination
                                    self.downPointList[j].goodsCount += self.agvList[i].task.quantity
                                    tig = 1 #指示器
                                
                                elif self.agvList[i].taskFinish==2: #送两次的送完了       
                                    if config.loadPs !=0:
                                        # if self.busy!=0:
                                        #     self.count += 1#self.agvList[i].task.quantity
                                        self.agvList[i].task = task_generator.generate_task()
                                    if config.loadPs !=0:
                                        #task_generator.reflush() #刷新一遍货物
                                        nextDestination = self.agvList[i].task.getNextDestination()
                                        self.agvList[i].endPos = ((config.MaxPickPoint,0))
                                        self.agvList[i].stationR = config.endPos1
                                        
                                    elif config.loadPs ==0: #停车
                                        if self.busy !=0:
                                            nextDestination = config.STOP_POINT_TEMP[i]
                                        else:
                                            nextDestination = config.STOP_POINT[i]
                                        self.agvList[i].endPos = nextDestination
                                    self.downPointList[j].goodsCount += self.agvList[i].task.quantity
                                    tig = 1 #指示器  
                                else : #送两次没送完的 
                                    #self.count += 1
                                    self.agvList[i].load_or_unload_wait_countdown = config.ROBOT_WAIT_TIME  # 倒计时恢复，以便下一次调用
                                    nextDestination = self.agvList[i].task.getNextDestination()
                                    self.agvList[i].endPos = self.agvList[i].stationR[1]  #前往下一个坐标
                                    self.downPointList[j].goodsCount += self.agvList[i].task.quantity
                                    tig = 1
                                    #self.agvList[i].stationR = config.endPos1
                                    
                            if self.agvList[i].load_or_unload_wait_countdown >= 0:
                                # 等待卸货倒计时
                                self.colorList[i] = (210, 140, 40)  # 变橙
                                self.agvList[i].load_or_unload_wait_countdown -= (1 / config.ROBOT_SPEED)
                            else:
                                
                                #if tig ==0 and self.busy!=0:
                                #    self.count += 1
                                
                                if tig ==0:
                                    self.downPointList[j].goodsCount += self.agvList[i].task.quantity
                                    #self.count += 1#self.agvList[i].task.quantity

                                nextDestination = self.agvList[i].task.getNextDestination()
                                
                                if nextDestination == (-1, -1) and tig == 0:
                                                               
                                    if config.loadPs !=0:
                                        self.agvList[i].task = task_generator.generate_task()
                                    if config.loadPs !=0:
                                        nextDestination = self.agvList[i].task.getNextDestination()
                                        self.agvList[i].endPos = ((config.MaxPickPoint,0))
                                        self.agvList[i].stationR = config.endPos1
                                    elif config.loadPs ==0: #停车
                                        if self.busy !=0:
                                            nextDestination = config.STOP_POINT_TEMP[i]
                                        else:
                                            nextDestination = config.STOP_POINT[i]
                                        self.agvList[i].endPos = nextDestination
                                        
                                '''
                                # 终点设为一个随机的出发点
                                self.endPs[i] = task_generator.gen_start_position(self.Map)
                                '''

                                # 倒计时恢复，以便下一次调用
                                self.agvList[i].load_or_unload_wait_countdown = config.ROBOT_WAIT_TIME
                                self.task1 += 1

                            break
            #num = round(((config.distriCenterCurr/config.distriCenter)*100),2)
            # 更新搬运数量
            self.label_tips.setText("搬运数量：" + str(self.count))
            self.label_tips1.setText("繁忙者：" + str(self.busy))
            self.label_tips2.setText("机器人数量:" + str(config.MAX_ROBOT_COUNT))
            
            self.label_tipsMaxCargo.setText("卡车货物:" + str(config.cargo) +"/"+ str(config.cargoMax))
            self.label_tipsLoad.setText("单次最大补货件数:" + str(config.distriCenter))
            
            task_generator.reflush()
            self.label_tipsCar.setText("路上的货物:" + str(config.cargoMax - config.cargo - self.count))
            self.label_tipsProcess.setText("当前补货的次数:" + str(config.orderProcessing))
            
            # self.label_tips_v_average.setText(str(self.distancesum/self.task1))
            # 更新总时长
            
            
            if config.cargo == 0 and self.busy == 0 :
                for i in range(config.MAX_ROBOT_COUNT):
                    self.agvList[i].endPos = config.STOP_POINT[i]
                self.time_count# = 1 / config.ROBOT_SPEED +
                minute = int(self.time_count / 60)
                second = int(self.time_count % 60)
                config.finish = "完成用时" + str(minute) + "分" + str(second) + "秒"
                self.label_time_s.setText(config.finish)
            else:
                self.time_count += 1 / config.ROBOT_SPEED
                minute = int(self.time_count / 60)
                second = int(self.time_count % 60)
                self.label_time_s.setText(str(minute) + "分" + str(second) + "秒")

            self.repaint()

    def Sequence_histogram_startP(self):
        plt.figure()
        countdata = self.process(Sequence_start_point, config.START_POINT)
        # print(f"Sequence_start_point的长度：{len(Sequence_start_point)}")
        # print(f"Sequence_start_point的数据：{Sequence_start_point}")
        # 绘制图
        plt.bar(range(len(countdata)),
                countdata,
                tick_label=range(1, len(countdata) + 1))

        # 添加标题和标签
        plt.title('Sequence_start_point')
        plt.xlabel('start_point')
        plt.ylabel('number')



    def Sequence_histogram_endP(self):
        plt.figure()
        countdata = self.process(Sequence_end_point, config.END_POINT)
        # print(f"Sequence_end_point：{len(Sequence_end_point)}")
        # print(f"Sequence_end_point数据：{Sequence_end_point}")
        plt.bar(range(len(countdata)),
                countdata,
                tick_label=range(1, len(countdata) + 1))

        # 添加标题和标签
        plt.title('Sequence_end_point')
        plt.xlabel('end_point')
        plt.ylabel('number')

        # 显示图表
        # plt.show()

    def button_PltShow(self):
        """
        按下button_pltShow按键后进行plt画图
        :return: None
        """
        plt.close()
        config.plt0 = -config.plt0
        config.plt1 = -config.plt1
        if config.plt0 > 0:
            plt.close()
            return 0

        self.Sequence_histogram_startP()
        # self.Sequence_histogram_endP()
        plt.ion()  # 打开交互模式
        while True:
            # 更新数据(表一)
            if config.plt0 > 0:
                plt.close()
                break
            countdata1 = self.process(Sequence_start_point, config.START_POINT)
            # 清空坐标轴
            plt.clf()
            # 绘制新的柱状图
            plt.bar(range(len(countdata1)), countdata1, tick_label=range(1, len(countdata1) + 1))
            # 设置标题和标签
            plt.title('Pickup-Times')
            plt.xlabel('Pickup point')
            plt.ylabel('Times')
            # 绘制图表并暂停一段时间
            plt.draw()
            plt.pause(1)

    def button_PltShow1(self):
        """
        按下button_pltShow1按键后进行plt画图
        :return: None
        """
        plt.close()
        config.plt1 = -config.plt1
        config.plt0 = -config.plt0
        if config.plt1 > 0:
            plt.close()
            return 0
        self.Sequence_histogram_endP()
        plt.ion()  # 打开交互模式
        while True:
            # 更新数据(表二)
            if config.plt1 > 0:
                plt.close()
                break
            countdata2 = self.process(Sequence_end_point, config.END_POINT)
            # 清空坐标轴
            plt.clf()
            # 绘制新的柱状图
            plt.bar(range(len(countdata2)), countdata2, tick_label=range(1, len(countdata2) + 1))

            # 设置标题和标签
            plt.title('Release-Times')
            plt.xlabel('Release point')
            plt.ylabel('Times')
            # 绘制图表并暂停一段时间
            plt.draw()
            plt.pause(1)

    def process(self, data, keyOrderList):
        """
        data:生成数据字典
        :keyOrderList:配置文件中的config.START_POINT 或者 config.END_POINT
        :return: 经过处理后的按照config文件配置的列表数据
        """
        res = []
        for key in keyOrderList:
            res.append(int(data.get(key, 0)))
        return res
