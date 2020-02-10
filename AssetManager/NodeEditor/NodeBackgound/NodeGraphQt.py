from PySide2 import QtWidgets, QtCore
from NodeBackgound import NodeDialog
from NodeExample import NodeAdd, NodeNum
from PySide2 import QtGui

import json,os


# 储存连接信息
node_connect_dir = {}

#获取主文件目录
path = os.path.dirname(os.path.abspath("__file__"))

srcPath = path + r"\src"

class BackWidget(QtWidgets.QWidget):
    """背景窗口"""
    def __init__(self):
        super(BackWidget, self).__init__()
        self.resize(800,600)

        # self.setStyleSheet("background-color:rgb(63, 63, 63);color:white")
        self.setStyleSheet("color:white")


        self.window_pale = QtGui.QPalette() 
        self.window_pale.setBrush(self.backgroundRole(),QtGui.QBrush(QtGui.QPixmap(srcPath + r"\gridBackground2.jpg"))) 
        self.setPalette(self.window_pale)

        self.hasSelectFirst = False  #是否已经选择了第一个连接节点
        
        #储存节点连接数据
        self.nodeFirst = []

        self.nodeSecond = []

        self.outputRadioNum = []
        self.inputRadioNum = []
        
        #节点数目
        self.nodeCount = 0

        self.nodeData = None
       
    

    #进入选择下一个节点状态
    def selectFirst(self, node):
        if self.hasSelectFirst:  #已经选择了一个输出端,撤销原来的选择
            self.nodeFirst[self.nodeCount].setRadioFalse(self.outputRadioNum[self.nodeCount]-1)

            del self.nodeFirst[self.nodeCount]
            del self.outputRadioNum[self.nodeCount]



        self.hasSelectFirst = True

        #保存节点连接数据
        self.nodeFirst.append(node) #节点
        self.outputRadioNum.append(node.radioNum)  #节点端口号
        
        self.nodeFirst[self.nodeCount].setRadioTrue(self.outputRadioNum[self.nodeCount])


    def selectSecond(self, node):

        if self.hasSelectFirst: # 已经选择了第一个节点，如果未选则，设置为不可点击
            
            
           
            #判断节点连接类型，符合规则则设置连接,不符合，将节点按钮设置成未点击，并删除数据
            if self.nodeFirst[self.nodeCount].nodeName == "nodeNum" and node.nodeName == "nodeAdd" and node.radioNum<=1: #nodeNum - addNum 并确保add为输入端口

                self.setConnect(self.nodeFirst[self.nodeCount], node, self.outputRadioNum[self.nodeCount], node.radioNum)
                node.setInputNode(self.nodeFirst[self.nodeCount-1],node.radioNum)

            elif self.nodeFirst[self.nodeCount].nodeName == "nodeNum" and node.nodeName == "nodeOutput" : #nodeNum - nodeOutput 

                self.setConnect(self.nodeFirst[self.nodeCount],node,self.outputRadioNum[self.nodeCount],node.radioNum)
                node.setInputNode(self.nodeFirst[self.nodeCount-1])

            elif self.nodeFirst[self.nodeCount].nodeName == "nodeAdd" and node.nodeName == "nodeOutput" and self.outputRadioNum[self.nodeCount] >= 3:  #nodeNum - nodeOutput,add为输出端口

                self.setConnect(self.nodeFirst[self.nodeCount],node,self.outputRadioNum[self.nodeCount],node.radioNum)
                node.setInputNode(self.nodeFirst[self.nodeCount-1])


            elif self.nodeFirst[self.nodeCount].nodeName == node.nodeName:  ## 防止自连

                node.setRadioFalse(node.radioNum)

            else:
                
                #不符合连接规则，取消输入节点的点击
                node.setRadioFalse(node.radioNum)
            
        
        else:
            node.setRadioFalse(node.radioNum+1)
        
            
            
            
 
                


    def paintEvent(self, event):

        """绘制界面"""

        ## 遍历每一对连接的节点
        for i in range(0,self.nodeCount):
        
            self.nodeData = Pipe.connectNode(self.nodeFirst[i], self.nodeSecond[i],self.outputRadioNum[i],self.inputRadioNum[i])

            painter = QtGui.QPainter()
            pen = QtGui.QPen(QtCore.Qt.white,10,QtCore.Qt.SolidLine)

            painter.setPen(pen)
            painter.begin(self)
            # self.painter.drawLine(self.nodeData[0], self.nodeData[1],self.nodeData[2],self.nodeData[3])

            path = QtGui.QPainterPath()

            path.moveTo(self.nodeData[0], self.nodeData[1])

            #绘制控制连接线的曲率点
            x_1 = (self.nodeData[0] + self.nodeData[2]) * 149 / 300
            
            y_1 = (self.nodeData[1] + self.nodeData[3]) * 1 / 4 
            
            x_2 = (self.nodeData[0] + self.nodeData[2]) * 151 / 300
            
            y_2 = (self.nodeData[1] + self.nodeData[3]) * 3 / 4
            
            path.cubicTo(x_1, y_1, x_2, y_2, self.nodeData[2], self.nodeData[3])

            
            painter.drawPath(path)

            # #绘制箭头
            
            # #求两个节点之间的斜率,根据直线方程y = kx + b
            # x_minus = self.nodeData[0] - self.nodeData[2]
            # y_minus = self.nodeData[1] - self.nodeData[3]
            # if x_minus == 0:
            #     x_minus = 0.001
            # if y_minus == 0:
            #     y_minus = 0.001
            

            # k = (self.nodeData[3] - self.nodeData[1]) / x_minus

            # b = self.nodeData[1] - k * self.nodeData[0]

            # #连接线中心点
            # point = QtCore.QPoint((self.nodeData[0] + self.nodeData[2]) / 2, (self.nodeData[1] + self.nodeData[3]) / 2)
            
            # #三个顶点
            # point1 = point + QtCore.QPoint(10, 10*k)
            # point2 = point - QtCore.QPoint(5, self.getY(k,5,b)) + QtCore.QPoint(2,2)
            # point3 = point - QtCore.QPoint(5, self.getY(k,5,b)) - QtCore.QPoint(2,2)
            
            
            # polygon = QtGui.QPolygon()
            # polygon << point< 
            # brush = QtGui.QBrush(QtCore.Qt.white)
            # painter.setBrush(brush)
            # painter.drawConvexPolygon(polygon)
            brush = QtGui.QBrush(QtCore.Qt.white)
            painter.setBrush(brush)
            point = QtCore.QPoint((self.nodeData[0] + self.nodeData[2]) / 2, (self.nodeData[1] + self.nodeData[3]) / 2)
            painter.drawEllipse(point, 3, 3)



            painter.end()
            


        
    #按下右键，打开节点选择器
    def mousePressEvent(self,event):
    
        self.setFocus()

        if event.buttons() == QtCore.Qt.RightButton:
            
            dialogs = self.findChildren(QtWidgets.QDialog, "节点选择器")
            for dialog in dialogs:
                dialog.close()

            nodeDialog = NodeDialog.NodeDialog(event.x(),event.y())

            nodeDialog.setParent(self)

            nodeDialog.move(event.x(),event.y())

            nodeDialog.show()



    def updateWindow(self):
        """更新窗口"""
        QtWidgets.QWidget.update(self)


    def printNodeCntData(self):
        """输出节点连接数据"""
        pass


    def setConnect(self, node1, node2, node1_num, node2_num):
        """设置连接"""
        self.nodeSecond.append(node2)
        self.inputRadioNum.append(node2_num)

        #执行窗口重绘
        self.updateWindow()

        self.hasSelectFirst = False

        self.nodeFirst[self.nodeCount].setRadioReadonly(node1_num)
        self.nodeSecond[self.nodeCount].setRadioReadonly(node2_num)

        self.nodeCount += 1



    

class Pipe():
    """用于绘制两个节点之间的连线"""
    def __init__(self, input_port=None, output_port=None):
        super(Pipe, self).__init__()



    @classmethod
    def connectNode(self, node1, node2 , node1_num = 0,node2_num = 0):
        """
        作用：
            获取连接节点的位置,然后把节点设置为只读
        参数：
            node1 - 输出节点
            node2 - 输入节点
            node1_num - 输出端口号，默认第一个端口
            node2_num - 输出端口号，默认第一个端口
        返回：
            节点端口位置
        """
        


        node1_x = node1.getOutputPos(node1_num)[0]
        node1_y = node1.getOutputPos(node1_num)[1]

        node2_x = node2.getInputPos(node2_num)[0]
        node2_y = node2.getInputPos(node2_num)[1]

        return node1_x,node1_y,node2_x,node2_y
        

