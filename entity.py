from config import config


class AGV:
    def __init__(self):
        self.task = None

        self.currentPos = (-1, -1)  # AGV当前的位置
        self.endPos = (-1, -1)  # AGV终点的位置

        self.previousStart = (-1, -1)  # 机器人上一个载货点或卸货点的位置，用于判断当前机器人是不是刚刚离开需要加速

        self.lowSpeedFlags = False  # 记录机器人是否正在低速行使（加速中或减速中）的标志
        self.lowSpeedWait = 0  # 记录机器人加速或减速的剩余等待时间
        self.direction = (0, 0)  # 机器人当前移动的方向

        self.noMoveCount = 0  # 记录机器人没有移动的次数

        self.load_or_unload_wait_countdown = config.ROBOT_WAIT_TIME  # 记录机器人载货或卸货的等待时间


class DownPoint:
    def __init__(self):
        self.pos = (-1, -1)  # 下货点的位置
        self.goodsCount = 0  # 下货点的货物堆放数量
        self.status = 0  # 下货点的状态，0表示打开，1表示关闭

        self.__removeGoodsCountDown = config.removeGoods  # 将卸货点的货物移上车的时间，这里设置为30s

    def removeGoods(self):
        self.__removeGoodsCountDown -= (1.0 / config.ROBOT_SPEED)  # 货物还没搬晚，倒计时减去(1 / config.ROBOT_SPEED)，即每走一步的用时
        if self.__removeGoodsCountDown > 0:
            self.status = 1  # 卸货点状态关闭
            return False  # False表示每搬运完
        else:
            self.status = 0  # 卸货点状态打开
            self.goodsCount = 0  # 货物清空
            self.__removeGoodsCountDown = 5.0  # 已经搬运完毕，重置倒计时便于下一次使用
            return True  # True表示搬运完毕
        
    
class UpPoint:
    def __init__(self):
        self.pos = (-1, -1)
        self.goodsCount = config.MaxloadP #货物直接上满
        