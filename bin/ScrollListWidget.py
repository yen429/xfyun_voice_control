from PyQt5 import QtCore, QtGui, QtWidgets

class ScrollListWidget(QtWidgets.QListWidget):
    cur_position = 0

    def __init__(self, parent=None):
        super(ScrollListWidget, self).__init__(parent)
        #设置垂直滚动条按像素滚动，如果使用ScrollPerItem按项滚动会感觉到卡顿
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

    def mouseMoveEvent(self, event):
        global cur_position
        #只有当鼠标左键按下时才触发
        if (event.buttons() == QtCore.Qt.LeftButton):
            #根据实际需要的效果设置qt4Delta
            delta = (event.y() - cur_position) * 1
            e = QtGui.QWheelEvent(event.pos(), event.globalPos(), QtCore.QPoint(0, 0), QtCore.QPoint(0, 0),delta, QtCore.Qt.Vertical, QtCore.Qt.NoButton, QtCore.Qt.NoModifier)
            #self.verticalScrollBar().wheelEvent(e)
            self.wheelEvent(e)
            cur_position = event.y()

    def mousePressEvent(self, event):
        global cur_position
        cur_position = event.y()
