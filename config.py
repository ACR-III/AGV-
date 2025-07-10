import random
import itertools
class config:
    WIDTH = 41  # 地图列数
    HEIGHT = 27  # 地图行数
    blockLength = 15  # 绘制画面时每一个节点方块的边长
    MAX_ROBOT_COUNT = 50 # 机器人数量
    ROBOT_SPEED = 2  # 机器人移动速度,单位m/s
    ROBOT_WAIT_TIME = 3  # 机器人载货、卸货的的等待时间，单位s
    ROBOT_ACCELERATION_TIME = 3  # 机器人速度从0加速到最大速度所需时间，或从最大速度减速到0所需的时间


    cargoMax=5000 #总仓库有多少货物
    
    busyColor=13 #色彩浓度的变化范围，最小0，最大250   卸货点的
    busyColorC=9 #色彩浓度的变化范围，最小0，最大250    载货点的
    
    finish ="30" #完成搬运的时间
    
    check = 0  # 取货点数量
    pick = []  # 货物堆积的情况(逻辑)
    pick1 = []  # 货物堆积的情况(物理)
    
    saftyPos =  (int)((WIDTH-1)/7) #小车不堵车的安全距离
    
    loadPs = 1 #统计出逻辑货物有多少
    loadPM = 1 #统计出物理货物有多少
    
    pickPoint=[] #设置任务分发的
    MaxPickPoint = 0 #最大的任务载货点
    startPos1 =[] #用来存开始坐标的
    endPos1 =[] #用来存结束坐标的
    
    timeDis =60 #一辆人工小车到达的时间间隔
    ArriveTime = 5 #一辆人工小车分发货物的时间间隔
    disputOn = -1 #分发的状态
    checkPos = 0 #当前检查具体到哪个up口了
    
    debug =500 #找路径的时间，如果没找着路就返回，避免死循环
    
    checkR = 0  # 卸货点数量
    checkR1 = 0  # 上/下卸货点数量
    checkR2 = 0  # 竖卸货点数量
    
    relW1 = []  # 横向的卸货点货物堆积的情况(上)
    relW2 = []  # 横向的卸货点货物堆积的情况(下)
    relH = []  # 竖向的卸货点货物堆积的情况

    start =-1 #开始结束判断
     
    MaxloadP=30 #单个载货点最大负载
    MaxloadR=20 #单个卸货点最大负载
    
    cargo=0 #总仓库剩余多少件货物
    removeGoods = 120 #把货物拿走的时间

    UpDistribute = 0 #用于统计在某一时刻,全部载货点的需求是多大
    distriCenter = 300 #单次补货
    distriCenterCurr = 0 #分发中心的当前实时的容积
    kn =1.2 #分发中心与全部载货点的容积之比
    
    orderSize = 0 #一个订单，大小是分发中心的1/5 - 1/3
    orderCollect = 0 #订单编号
    orderProcessing = 0 #记录已处理的订单
    
    plt0 = 1  # 开关窗口的
    plt1 = 1  # 开关窗口的
    
    parX=3 
    parY=1 #都是停车点的横竖坐标
    
    parX_t=5 
    parY_t=3 #临时停车坐标
    
    STOP_POINT = [] #停车点
    STOP_POINT_TEMP = [] #临时停车点
    # START_POINT = [(1, 0), (7, 0), (12, 0), (17, 0), (19, 3), (19, 8), (19, 13), (19, 19), (19, 23), (19, 28)]  # 出发点坐标
    # END_POINT = [(0, 6), (0, 12), (0, 18), (0, 23), (0, 28), (5, 29), (10, 29), (16, 29)]    # 接收点坐标
    # 65*65
    # ROOT_LOCATION = [(3,6),(6,6),(3,10),(20,4),(2,9)]
    # ROOT_LOCATION = []
    # for i in range(0,MAX_ROBOT_COUNT):
    #     ROOT_LOCATION.append(((random.randint(HEIGHT-1, WIDTH-1 )),(random.randint(HEIGHT-1,WIDTH-1))))


    # random_list = list(itertools.product(range(HEIGHT-1, WIDTH-1), range(HEIGHT-1, WIDTH-1)))
    #
    # ROOT_LOCATION = random.sample(random_list, MAX_ROBOT_COUNT)

    ROOT_LOCATION = []
    for i in range(1,MAX_ROBOT_COUNT+1):
        ROOT_LOCATION.append((random.randint(1,HEIGHT-2),random.randint(1,WIDTH-2)))

    START_POINT = []
    START_POINTcop = [] #用于判断载货点有没有被占用
    for i in range(1, HEIGHT, 3):  # 从0到宽度，步长为2
        START_POINT.append((i, 0))
        pickPoint.append((i,0))
        START_POINTcop.append((i,0,0)) #开局，没有被占用

    END_POINT = []
    
    END_POINTup = [] #上方载货点
    END_POINTdown = [] #下方载货点
    END_POINTfront = [] #竖直载货点
    
    for i in range(3, WIDTH, 3):  # 从0到宽度，步长为2
        END_POINT.append((HEIGHT - 1, i))
        END_POINTdown.append((HEIGHT - 1, i))

    for i in range(3, WIDTH,  3):  # 从0到高度，步长为2
        END_POINT.append((0, i))
        END_POINTup.append((0, i))

    for i in range(2, HEIGHT-1, 3):  # 从0到高度，步长为2
        END_POINT.append((i, WIDTH - 1))
        END_POINTfront.append((i, WIDTH - 1))

    # 原本程序
    # START_POINT = []
    # for i in range(0, WIDTH, (int)((WIDTH + HEIGHT) / MAX_ROBOT_COUNT)):  # 从0到宽度，步长为2
    #     START_POINT.append((i, 0))
    # for i in range(2, HEIGHT, (int)((WIDTH + HEIGHT) / MAX_ROBOT_COUNT)):  # 从0到高度，步长为2
    #     START_POINT.append((0, i))
    # START_POINT = [(2, 0),(4, 0),(6, 0), (8, 0),(10, 0), (12, 0), (14, 0),(16, 0),(18, 0), (20, 0),(22, 0),(24, 0), (26, 0), (28, 0), (30, 0),(32, 0), (34, 0), (36, 0), (38, 0), (40, 0), (42, 0), (44, 0), (46, 0), (48, 0), (50, 0), (52, 0), (54, 0), (56, 0),(58, 0), (60, 0),(0,2),(0,4),(0,6),(0,8),(0,10),(0,12),(0,14),(0,16),(0,18),(0,20),(0,22),(0,24),(0,26),(0,28),(0, 30), (0, 32), (0, 34), (0, 36), (0, 38), (0, 40), (0, 42), (0, 44), (0, 46), (0, 48), (0, 50), (0, 52), (0, 54), (0, 56), (0, 58), (0, 60),]
    # END_POINT = [ (2, 64), (4, 64), (6, 64), (8, 64), (10, 64), (12, 64), (14, 64), (16, 64), (18, 64), (20, 64), (22, 64), (24, 64), (26, 64), (28, 64),(30, 64), (32, 64), (34, 64), (36, 64), (38, 64), (40, 64), (42, 64), (44, 64), (46, 64), (48, 64), (50, 64), (52, 64), (54, 64), (56, 64), (58, 64), (60, 64),(64, 2), (64, 4), (64, 6), (64, 8), (64, 10), (64, 12), (64, 14), (64, 16), (64, 18), (64, 20),(64, 22), (64, 24), (64, 26), (64, 28), (64, 30), (64, 32), (64, 34), (64, 36), (64, 38), (64, 40), (64, 42), (64, 44), (64, 46), (64, 48), (64, 50), (64, 52), (64, 54), (64, 56), (64, 58), (64, 60)]  # 接收点坐标
    # END_POINT = []
    # for i in range(0, WIDTH, (int)((WIDTH + HEIGHT) / MAX_ROBOT_COUNT)):  # 从0到宽度，步长为2
    #     END_POINT.append((HEIGHT - 1, i))
    # for i in range(0, HEIGHT, (int)((WIDTH + HEIGHT) / MAX_ROBOT_COUNT)):  # 从0到高度，步长为2
    #     END_POINT.append((i, WIDTH - 1))



