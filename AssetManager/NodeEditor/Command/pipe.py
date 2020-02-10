from NodeExample.node import BaseNode


class Pipe():
    """用于绘制两个节点之间的连线"""
    def __init__(self, input_port=None, output_port=None):
        super(Pipe, self).__init__()

    # def paint(self):
    #     """
    #     绘制两个节点之间的连线        
    #     """
    #     painter = QtGui.QPainter()
    #     pen = QtGui.QPen()
    #     painter.setPen(pen)
    #     path = QtGui.QPainterPath()
    #     painter.drawPath(path)

    @classmethod
    def connectNode(self, node1, node2):
        """连接节点"""
        
        node1_x = node1.getOutputPos()[0]
        node1_y = node1.getOutputPos()[1]

        node2_x = node2.getPos()[0]
        node2_y = node2.getPos()[1]

        print(node1_x)
        print(node1_y)
        print(node2_x)
        print(node2_y)
        

