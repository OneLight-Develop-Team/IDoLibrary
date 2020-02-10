from NodeBackgound import NodeGraphQt
from PySide2 import QtWidgets
import sys



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = NodeGraphQt.BackWidget()
    win.show()

    app.exec_()