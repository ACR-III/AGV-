import random
from config import config
from copy import copy

class Task:
    def __init__(self):
        self.start = (-1, -1)  # 任务出发点
        self.end = (-1, -1)  # 卸货点
        self.quantity = 0  # 每个卸货点的卸货数量
        self.__cursor = 0  # 任务的游标，0表示还未开始，1表示到达装货点，2表示到达卸货点

    def setTask(self, start, end, quantity):
        self.start = start
        self.end = end
        self.quantity = quantity

    # 取下一个目的地的位置，如果返回（-1, -1），则表示任务已经完成
    def getNextDestination(self):
        if self.__cursor == 0:
            self.__cursor += 1
            return self.start
        elif self.__cursor == 1:
            self.__cursor += 1
            return self.end
        else:
            return -1, -1

def reflush():
    config.loadPs=0 #逻辑货物计算
    config.loadPM=0 #物理货物计算
    for i in range(config.check): #实时统计当前计算有多少货物(逻辑)
        config.loadPs+=config.pick[i]
        config.loadPM+=config.pick1[i]

     #使用找逻辑最繁忙算法
    max = 0
    minPos =0
    for i in range(config.check):
        if max < config.pick[i]: #找到物品最多的逻辑载货点
                minPos = i 
                max = config.pick[i]
                config.MaxPickPoint = minPos*3 #最大的载货点坐标

def generate_task():
  
    task = Task()
    startPos = config.START_POINT[random.randint(0, len(config.START_POINT) - 1)]
    endPos = [] # config.END_POINT[random.randint(0, len(config.END_POINT) - 1)]
    quantity = 1#random.randint(1, 3)
    task.setTask(startPos, endPos, quantity)
    endPosCount = 1
    # if config.start > 0: #仿真1开始，下面的才会做判断
    
    
    config.loadPs=0 #逻辑货物计算
    config.loadPM=0 #物理货物计算
    for i in range(config.check): #实时统计当前计算有多少货物(逻辑)
        config.loadPs+=config.pick[i]
        config.loadPM+=config.pick1[i]

     #使用找逻辑最繁忙算法
    max = 0
    maxPos =0
    for i in range(config.check):
        if max < config.pick[i]: #找到物品最多的逻辑载货点
                maxPos = i
                max = config.pick[i]
                config.MaxPickPoint = maxPos*3+1 #最大的载货点坐标         
    if max!=0: #还有货物
        startPos = (config.MaxPickPoint,0)  #往物品最多载货点进发
    else:
            #task =((-1,-1),(-1,-1),-1) #赋值
        print("货物发放完毕，小车将回到起始点")
            #config.pick[(int)(startPos[0]/3)] -= 1 #逻辑货物减一
        return task
    
    # if config.pick[maxPos]>=2: #看看载货点还有多少货物
    #     endPosCount = 2
    # elif config.pick[maxPos]==1:
    #     endPosCount = 1
    tig = random.randint(1,10) #十分之一的几率送1个货物
    if tig ==1 :#and (startPos[0] >= ((config.HEIGHT)/4)) and (startPos[0] <= (((config.HEIGHT)/4)*3)):
        endPosCount = 1
    else:
        endPosCount = 2        
    if config.pick[maxPos]<2: #看看载货点还有多少货物
        endPosCount = 1
    #endPosCount = 2
    if endPosCount == 2 :
        if startPos[0] < ((config.HEIGHT)/4): #前四分之一的载货点，负责送上方的卸货点
            
            e1 = config.END_POINTup[random.randint(0, (int)(((len(config.END_POINTup) - 1)/3)-1))]
            e2 = config.END_POINTdown[random.randint((int)(((len(config.END_POINTdown) - 1)/3)), (int)(((len(config.END_POINTdown) - 1)/3)*2)-1)]           
            endPos.append(e1)
            endPos.append(e2)
            
        #中间四分之一的载货点
        elif (startPos[0] >= ((config.HEIGHT)/4)) and (startPos[0] <= (((config.HEIGHT)/4)*2)):     
            e1 = config.END_POINTfront[random.randint(0, (int)((len(config.END_POINTfront) - 1)/2)-1)] 
            e2 = config.END_POINTup[random.randint((int)(((len(config.END_POINTup) - 1)/3)*2), ((len(config.END_POINTup) - 1)))]
            endPos.append(e1)
            endPos.append(e2)
        #中间四分之一的载货点
        elif (startPos[0] >= ((config.HEIGHT)/2)) and (startPos[0] <= (((config.HEIGHT)/4)*3)):     
            e1 = config.END_POINTfront[random.randint((int)((len(config.END_POINTfront) - 1)/2), (int)((len(config.END_POINTfront) - 1)))] 
            e2 = config.END_POINTdown[random.randint((int)(((len(config.END_POINTdown) - 1)/3)*2), ((len(config.END_POINTdown) - 1)))]
            endPos.append(e1)
            endPos.append(e2)
        #下面四分之一的载货点，负责送上方的卸货点
        elif startPos[0] > (((config.HEIGHT)/4)*3):
            e1 = config.END_POINTdown[random.randint(0, (int)(((len(config.END_POINTup) - 1)/3)-1))]
            e2 = config.END_POINTup[random.randint((int)(((len(config.END_POINTdown) - 1)/3)), (int)(((len(config.END_POINTdown) - 1)/3)*2)-1)]           
            endPos.append(e1)
            endPos.append(e2)
            
            #endPos = config.END_POINTdown[random.randint(0, (int)((len(config.END_POINTdown) - 1)))]

    if endPosCount == 1 :
        tig = random.randint(1,2)
        if startPos[0] < ((config.HEIGHT)/4): #前四分之一的载货点，负责送上方的卸货点  
            if tig ==1:    
                e1 = config.END_POINTup[random.randint(0, (int)(((len(config.END_POINTup) - 1)/3)))]
            elif tig ==2:    
                e1 = config.END_POINTdown[random.randint((int)(((len(config.END_POINTdown) - 1)/3-1)), (int)(((len(config.END_POINTdown) - 1)/3)*2)-1)]           
            endPos.append(e1)
            endPos.append((-1,-1))
            
        #中间四分之一的载货点
        elif (startPos[0] >= ((config.HEIGHT)/4)) and (startPos[0] <= (((config.HEIGHT)/4)*2)):    
            if tig ==1: 
                e1 = config.END_POINTfront[random.randint(0, (int)((len(config.END_POINTfront) - 1)/2)-1)]
            elif tig ==2:  
                e1 = config.END_POINTup[random.randint((int)(((len(config.END_POINTup) - 1)/3)*2), ((len(config.END_POINTup) - 1)))]
            endPos.append(e1)
            endPos.append((-1,-1))
        #中间四分之一的载货点
        elif (startPos[0] >= ((config.HEIGHT)/2)) and (startPos[0] <= (((config.HEIGHT)/4)*3)): 
            if tig ==1:     
                e1 = config.END_POINTfront[random.randint((int)((len(config.END_POINTfront) - 1)/2), (int)((len(config.END_POINTfront) - 1)))]
            elif tig ==2:  
                e1 = config.END_POINTdown[random.randint((int)(((len(config.END_POINTdown) - 1)/3)*2), ((len(config.END_POINTdown) - 1)))]
            endPos.append(e1)
            endPos.append((-1,-1))
        #下面四分之一的载货点，负责送上方的卸货点
        elif startPos[0] > (((config.HEIGHT)/4)*3):
            if tig ==1: 
                e1 = config.END_POINTdown[random.randint(0, (int)(((len(config.END_POINTup) - 1)/3)))]
            elif tig ==2: 
                e1 = config.END_POINTup[random.randint((int)(((len(config.END_POINTdown) - 1)/3)-1), (int)(((len(config.END_POINTdown) - 1)/3)*2)-1)]           
            endPos.append(e1)
            endPos.append((-1,-1))
    

    
    config.endPos1 = endPos #调用一次，生成一个
    config.startPos1 = startPos
    print("产生了一个起始于" + str(startPos) + "的任务。载货量:" + str(quantity) + " 卸货点：" + str(endPos))
    
    #config.distriCenterCurr-=1   #分发中心和总库代码 (伪)
    

        
    #end_time = time.time()
    
    #elapsed_time = end_time - start_time

    #print("程序运行时间：", elapsed_time, "秒")
    
    # if config.distriCenterCurr < config.distriCenter - (int)(config.distriCenter/4): #当分发中心容量小于四分之一
    #     carCurr = random.randint(0,(int)(config.distriCenter/5))
    #     if config.cargo > carCurr:
    #         config.cargo -=carCurr #总量减少
    #         config.distriCenterCurr+=carCurr #分发中心负载增加
    #         config.orderCollect+=1
    #         config.orderProcessing+=1
            
    #     if config.cargo==0:
    #         config.cargo=0
    #         #print("总仓库已经发放完成货物")
                
    #     elif config.cargo < carCurr:
    #         config.cargo=0
    #         carCurr = config.cargo #总量减少
    #         config.distriCenterCurr+=carCurr #分发中心负载增加
    #         config.orderCollect+=1
    #         config.orderProcessing+=1
    if endPosCount == 1:                
        config.pick[(int)(startPos[0]/3)] -= 1 #逻辑货物减一
    elif endPosCount == 2:
        config.pick[(int)(startPos[0]/3)] -= 2 #逻辑货物减二
    return task




# # 返回一个随机的出发点的坐标
# def gen_start_position(arg_map):
#     pos = config.START_POINT[random.randint(0, len(config.START_POINT) - 1)]
#     #while arg_map[pos[0]][pos[1]] == 1:
#     #    pos = config.START_POINT[random.randint(0, len(config.START_POINT) - 1)]
#     return pos

# # 返回一个随机的接收点坐标
# def gen_end_position(arg_map):
#     pos = config.END_POINT[random.randint(0, len(config.END_POINT) - 1)]
#     #while arg_map[pos[0]][pos[1]] == 1:
#     #    pos = config.END_POINT[random.randint(0, len(config.START_POINT) - 1)]
#     return pos
