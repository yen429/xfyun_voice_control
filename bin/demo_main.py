# -*- coding: utf-8 -*-

# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from get_data import getDialogState, getCardData
from clock import getTime
from ScrollListWidget import ScrollListWidget
from watchdog.observers import Observer
from watchdog.events import *
import json
import urllib.request
import threading
import os
import math

class Ui_MainWindow(QtCore.QObject):
    refreshSignal = QtCore.pyqtSignal(str)
    switchSignal = QtCore.pyqtSignal(str)

    listwidget_background_style = '''
            QWidget{
                background-color: #E0E0E0;
            }
                
        '''
        
    label_robot_style = '''
            QLabel{
                border-radius: 6px;
                padding: 10px;
                font-size: 12pt;
                background-color: #ffffff;
                }
        '''
        
    label_user_style = '''
            QLabel{
                border-radius: 6px;
                padding: 10px;
                font-size: 12pt;
                background-color: #00ff66;
                }
        '''

	#窗口尺寸
    contentWidth = 480
    contentHeight = 800

    #字体
    globalTextFont = QtGui.QFont()
    globalTextFont.setFamily("Bookman Old Style")
    globalTextFont.setPointSize(12)

    body_template1 = 'BodyTemplate1'
    body_template2 = 'BodyTemplate2'
    list_template1 = 'ListTemplate1'
    weather_template = 'WeatherTemplate'
    
    #label的宽度
    label_max_width = 450
    #label的单行高度
    label_single_height = 70
    
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        
        #设置主窗口宽和高
        #MainWindow.resize(self.contentWidth, self.contentHeight)
		#全屏显示时设置高度，用于List Widget居中
        desktop = QtWidgets.QApplication.desktop()
        MainWindow.resize(desktop.width(), desktop.height())

        #设置主窗口背景色
        MainWindow.setAutoFillBackground(True)
        palette = QtGui.QPalette()
        palette.setColor(MainWindow.backgroundRole(), QtGui.QColor(000,000,000))
        MainWindow.setPalette(palette)

        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")

        #初始化状态
        self.oldState = "none"
        self.firstRun = True
        self.answerItem_total_height = 0
        self.respond_animation = QtGui.QMovie("./res/respond.gif")

        #设置List Widget
        self.listWidget = ScrollListWidget(self.centralWidget)
        #设置List Widget尺寸(x起点，y起点，x宽度，y高度)
        self.listWidget.setGeometry(QtCore.QRect((MainWindow.width() - self.contentWidth)/2, (MainWindow.height() - self.contentHeight)/2, self.contentWidth, self.contentHeight*9/10))
        #去掉List Widget边框
        self.listWidget.setFrameShape(QtWidgets.QListWidget.NoFrame)
        self.listWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.listWidget.setDefaultDropAction(QtCore.Qt.MoveAction)
        #避免选中，去掉选中的背景高亮效果
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.listWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.listWidget.setFocusPolicy(QtCore.Qt.NoFocus);
        self.listWidget.setObjectName("listWidget")
        #self.listWidget.setStyleSheet("background-color:HoneyDew;");
        self.listWidget.setStyleSheet(self.listwidget_background_style)

        #首次打开添加一个item到List Widget
        idleWidget = QtWidgets.QWidget(MainWindow)
        idleLayout = QtWidgets.QHBoxLayout(idleWidget)
        idleLayout.setAlignment(QtCore.Qt.AlignLeft)
        idleLab1 = QtWidgets.QLabel(MainWindow)
        idleLab2 = QtWidgets.QLabel(MainWindow)
        idleLab1.setAlignment(QtCore.Qt.AlignLeft)
        idleLab2.setAlignment(QtCore.Qt.AlignLeft)
        idleLayout.addWidget(idleLab1)
        idleLayout.addWidget(idleLab2)
        #设置居中、边框及背景色
        idleLab2.setAlignment(QtCore.Qt.AlignVCenter)
        idleLab2.setStyleSheet(self.label_robot_style)
        #设置头像尺寸(x起点，y起点，x宽度，y高度)
        pixMap = QtGui.QPixmap("./res/robot_avatar.png").scaled(40,40)  
        idleLab1.setPixmap(pixMap)
        idleLab2.setFont(self.globalTextFont)
        idleLab2.setText("What can I service for you?")
        idleWidget.setLayout(idleLayout)
        idleItem = QtWidgets.QListWidgetItem(self.listWidget)
        self.listWidget.addItem(idleItem)
        self.listWidget.setItemWidget(idleItem,idleWidget)
        #设置item的宽度和高度
        idleItem.setSizeHint(QtCore.QSize(0,self.label_single_height))
        idleWidget.show()

        #设置底部状态显示区
        self.footerLabel = QtWidgets.QLabel(MainWindow)
        #设置底部状态显示区尺寸(x起点，y起点，x宽度，y高度)
        self.footerLabel.setGeometry(QtCore.QRect((MainWindow.width() - self.contentWidth)/2, (MainWindow.height() - self.contentHeight)/2 + self.listWidget.height(), self.contentWidth, self.contentHeight/10))
        self.footerLabel.setStyleSheet("background-color:AliceBlue;")
        #Bottom居中
        self.footerLabel.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.footerLabel.setFont(self.globalTextFont)

		 #设置首次页面
        self.standbyWidget = QtWidgets.QWidget(self.centralWidget)
        self.standbyWidget.setGeometry(QtCore.QRect((MainWindow.width() - self.contentWidth)/2, (MainWindow.height() - self.contentHeight)/2, self.contentWidth, self.contentHeight*9/10))
        self.standbyWidget.setObjectName("standbyWidget")

        self.standbyLabel = QtWidgets.QLabel(self.standbyWidget)
        #设置底部状态显示区尺寸(x起点，y起点，x宽度，y高度)
        self.standbyLabel.setGeometry(QtCore.QRect(0, 0, self.contentWidth, self.contentHeight*9/10))
        self.standbyLabel.setStyleSheet("background-color:AliceBlue;")
        #竖向居中
        self.standbyLabel.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignHCenter)
        pixMap = QtGui.QPixmap("./res/background.jpg")
        self.standbyLabel.setPixmap(pixMap)

        #standby时钟
        self.hourAndMin = QtWidgets.QLabel(self.standbyWidget)
        self.hourAndMin.setGeometry(QtCore.QRect(self.contentWidth/6, self.contentHeight/5, 300, 100))
        font = QtGui.QFont()
        font.setPointSize(60)
        self.hourAndMin.setFont(font)
        self.hourAndMin.setStyleSheet("color: rgb(255, 255, 255);")
        self.hourAndMin.setObjectName("hourAndMin")
        self.second = QtWidgets.QLabel(self.standbyWidget)
		#尺寸适用于树莓派3
        self.second.setGeometry(QtCore.QRect(self.contentWidth/6+230, self.contentHeight/5+15, 100, 100))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.second.setFont(font)
        self.second.setStyleSheet("color: rgb(255, 255, 255);")
        self.second.setObjectName("second")

        MainWindow.setCentralWidget(self.centralWidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        #绑定信号和槽函数
        self.refreshSignal.connect(self.update_card_data)
        self.switchSignal.connect(self.switchState)
		#初始化状态
        #no need for xunfei self.update_state()
        self.update_clock()
        #全屏显示,必须放在所有组件画完以后执行
        MainWindow.showFullScreen()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.hourAndMin.setText(_translate("MainWindow", "00:00"))
        self.second.setText(_translate("MainWindow", "00"))

    def update_clock(self):
        _translate = QtCore.QCoreApplication.translate
        hour_time, min_time, sec_time = getTime()
        ahead_time = hour_time + ':' + min_time
        self.second.setText(_translate("MainWindow",sec_time))
        self.hourAndMin.setText(_translate("MainWindow",ahead_time))
        if self.firstRun == True:
            clockTimer = threading.Timer(1, self.update_clock)
            clockTimer.start()
    
    #for xunfei
    def pre_process_data(self,data):
        if "ANS:" in data:
            self.add_answer_item(data[4:])
        elif "ASK:" in data:
            self.add_ask_item(data[4:])
        else:
            if "IDLE_STATE" in data:
                state = "Online"
            elif "LISTEN_STATE" in data:
                state = "Listening"
            elif "THINK_STATE" in data:
                state = "Thinking"
            elif "SPEAK_STATE" in data:
                state = "Speaking"

            print("state: %s"%(state))

            if self.firstRun == False:
                self.standbyWidget.hide()

            #若状态未改变，则不需要发出state更改信号
            if state == self.oldState:
                return
            else:
                self.oldState = state

            if "Close" in state:
                #关闭窗口
                MainWindow.close()
            else:
                #切换状态，发射信号(子线程触发主线程函数)
                self.switchSignal.emit(state)

    def switchState(self,state):
        if "Online" in state and not "Thinking" in self.oldState:
            #pixMap = QtGui.QPixmap("./res/idle.png").scaled(self.footerLabel.width(),self.footerLabel.height())
            #self.footerLabel.setPixmap(pixMap)
            self.footerLabel.setStyleSheet("color:#408CBE;background-image:url(./res/idle.png);background-color:AliceBlue;")

            #For Google assistant library:
            #self.footerLabel.setText("Speak 'OK,Google' To Start")

            #For Google assistant service:
            #self.footerLabel.setText("Speak 'Jarvis' To Start")

            #For xunfei:
            self.footerLabel.setText("Speak '哈囉你好' To Start")

            self.respond_animation.stop()
        elif "Listening" in state:
            if self.firstRun == True:
                self.standbyWidget.hide()
                self.firstRun = False
            animation = QtGui.QMovie("./res/listening.gif")
            self.footerLabel.setStyleSheet("background-color:AliceBlue;")
            self.footerLabel.setMovie(animation)
            animation.start()
        elif "Thinking" in state:
            #For Google assistant library
            #self.refreshSignal.emit("Ask")

            animation = QtGui.QMovie("./res/thinking.gif")
            self.footerLabel.setStyleSheet("background-color:AliceBlue;")
            self.footerLabel.setMovie(animation)
            animation.start()
        elif "Speaking" in state:
            #For Alexa:
            #self.refreshSignal.emit("Alexa_Data") #更新数据

            #For Google assistant library:
            #self.add_answer_item_for_google_assistant_library() # add answer item

            #For Google assistant service:
            self.refreshSignal.emit("Service_Data")

            animation = QtGui.QMovie("./res/speaking.gif")
            self.footerLabel.setStyleSheet("background-color:AliceBlue;")
            self.footerLabel.setMovie(animation)
            animation.start()
        elif "Connecting" in state:
            self.refreshSignal.emit() #更新数据
            animation = QtGui.QMovie("./res/connecting.gif")
            self.footerLabel.setStyleSheet("background-color:AliceBlue;")
            self.footerLabel.setMovie(animation)
            animation.start()
        elif "Disconnected" in state:
            pixMap = QtGui.QPixmap("./res/offline.png").scaled(self.footerLabel.width(),self.footerLabel.height())
            self.footerLabel.setStyleSheet("background-color:AliceBlue;")
            self.footerLabel.setPixmap(pixMap)

    def update_state(self):
        state = getDialogState()
        print("state: %s"%(state))

        if self.firstRun == False:
            self.standbyWidget.hide()

        #若状态未改变，则不需要发出state更改信号
        if state == self.oldState:
            return
        else:
            self.oldState = state

        if "Close" in state:
            #关闭窗口
            MainWindow.close()
        else:
            #切换状态，发射信号(子线程触发主线程函数)
            self.switchSignal.emit(state)

    def update_card_data(self,state):
        data = getCardData()
        if "Ask" in state:
            #Google assistant library only
            self.add_ask_item(data)
        elif "Service_Data" in state:
            #Google assistant service only
            try:
                result = json.loads(data)
            except json.JSONDecodeError:
                return
            self.add_ask_item(result['ask'])
            self.add_answer_item(result['answer'])
        elif "Alexa_Data" in state:
            #Alexa Only
            try:
                result = json.loads(data)
            except json.JSONDecodeError:
                return
            self.add_ask_item(result['title']['mainTitle'])
            self.add_answer_item_for_alexa(self,result)

    def add_ask_item(self,text):
        #添加用户语句到List Widget
        askWidget = QtWidgets.QWidget(MainWindow)
        askLayout = QtWidgets.QHBoxLayout(askWidget)
        askLayout.setAlignment(QtCore.Qt.AlignRight)
        askLab1 = QtWidgets.QLabel(MainWindow)
        askLab2 = QtWidgets.QLabel(MainWindow)
        askLab1.setAlignment(QtCore.Qt.AlignRight)
        askLab2.setAlignment(QtCore.Qt.AlignRight)
        askLayout.addWidget(askLab1)
        askLayout.addWidget(askLab2)
        #设置居中、边框和背景色
        askLab1.setAlignment(QtCore.Qt.AlignVCenter)
        #askLab1.setStyleSheet("background-color:LightSkyBlue;border:0.5px solid;border-color:LightSkyBlue;border-radius:5px;");
        askLab1.setStyleSheet(self.label_user_style)
        #自动换行
        #askLab1.setWordWrap(True)
        askLab1.setFont(self.globalTextFont)
        #自适应获取当前text对应的label高度
        ask_label_total_height = self.label_height_by_text(askLab1, text)
        askLab1.setGeometry(0, 0, self.label_max_width, ask_label_total_height)
        askLab1.setText(text)

        #设置头像尺寸(x起点，y起点，x宽度，y高度)
        pixMap = QtGui.QPixmap("./res/user_avatar.png").scaled(40, 40)  
        askLab2.setPixmap(pixMap)

        askWidget.setLayout(askLayout)
        askItem = QtWidgets.QListWidgetItem(self.listWidget)
        self.listWidget.addItem(askItem)
        self.listWidget.setItemWidget(askItem,askWidget)
        #设置item的宽度和高度
        askItem.setSizeHint(QtCore.QSize(0,ask_label_total_height))
        askWidget.show()
        #添加新内容后，列表滚动到底部
        self.listWidget.scrollToBottom()

    def add_answer_item_for_google_assistant(self):
        #添加到List Widget
        answerWidget = QtWidgets.QWidget(MainWindow)
        answerLayout = QtWidgets.QHBoxLayout(answerWidget)
        answerLayout.setAlignment(QtCore.Qt.AlignLeft)
        answerLab1 = QtWidgets.QLabel(MainWindow)
        answerLab1.setAlignment(QtCore.Qt.AlignLeft)
        answerLayout.addWidget(answerLab1)
        answerLayout.addWidget(self.set_response_anim_widget())

        #设置头像尺寸(宽度，高度)
        pixMap = QtGui.QPixmap("./res/robot_avatar.png").scaled(40,40)  
        answerLab1.setPixmap(pixMap)

        answerWidget.setLayout(answerLayout)
        answerItem = QtWidgets.QListWidgetItem(self.listWidget)
        self.listWidget.addItem(answerItem)
        self.listWidget.setItemWidget(answerItem,answerWidget)
        #设置item的宽度和高度
        answerItem.setSizeHint(QtCore.QSize(0, self.answerItem_total_height))
        answerWidget.show()

        #添加新内容后，列表滚动到底部
        self.listWidget.scrollToBottom()

    def add_answer_item(self,text):
        #添加到List Widget
        answerWidget = QtWidgets.QWidget(MainWindow)
        answerLayout = QtWidgets.QHBoxLayout(answerWidget)
        answerLayout.setAlignment(QtCore.Qt.AlignLeft)
        answerLab1 = QtWidgets.QLabel(MainWindow)
        answerLab1.setAlignment(QtCore.Qt.AlignLeft)
        answerLayout.addWidget(answerLab1)
        answerLayout.addWidget(self.set_response_text_widget(text))

        #设置头像尺寸(宽度，高度)
        pixMap = QtGui.QPixmap("./res/robot_avatar.png").scaled(40,40)  
        answerLab1.setPixmap(pixMap)

        answerWidget.setLayout(answerLayout)
        answerItem = QtWidgets.QListWidgetItem(self.listWidget)
        self.listWidget.addItem(answerItem)
        self.listWidget.setItemWidget(answerItem,answerWidget)
        #设置item的宽度和高度
        answerItem.setSizeHint(QtCore.QSize(0, self.answerItem_total_height))
        answerWidget.show()

        #添加新内容后，列表滚动到底部
        self.listWidget.scrollToBottom()

    def add_answer_item_for_alexa(self,result):
        #添加Alexa应答语句到List Widget
        answerWidget = QtWidgets.QWidget(MainWindow)
        answerLayout = QtWidgets.QHBoxLayout(answerWidget)
        answerLayout.setAlignment(QtCore.Qt.AlignLeft)
        answerLab1 = QtWidgets.QLabel(MainWindow)
        answerLab1.setAlignment(QtCore.Qt.AlignLeft)
        answerLayout.addWidget(answerLab1)
        answerLayout.addWidget(self.set_data_to_item_layout(result))

        #设置头像尺寸(宽度，高度)
        pixMap = QtGui.QPixmap("./res/robot_avatar.png").scaled(40,40)  
        answerLab1.setPixmap(pixMap)

        answerWidget.setLayout(answerLayout)
        answerItem = QtWidgets.QListWidgetItem(self.listWidget)
        self.listWidget.addItem(answerItem)
        self.listWidget.setItemWidget(answerItem,answerWidget)
        #设置item的宽度和高度
        answerItem.setSizeHint(QtCore.QSize(0, self.answerItem_total_height))
        answerWidget.show()

        #添加新内容后，列表滚动到底部
        self.listWidget.scrollToBottom()

    #根据文字高度自适应获得Label高度
    def label_height_by_text(self, label, label_text):
        answer_metrics = QFontMetrics(label.font())
        #获取text在当前label font的宽度
        text_width = answer_metrics.width(label_text)
        #带小数的行数
        label_rows = text_width / self.label_max_width
        #实际label行数,向上取整
        real_label_rows = math.ceil(label_rows)
        return real_label_rows * self.label_single_height
        
    def set_data_to_item_layout(self, json_data):
        item_widget = QtWidgets.QWidget(MainWindow)
        if json_data:
            type = json_data.get('type',  'NA')
            if self.body_template1 in type:
                item_widget = self.set_body_template1_widget(json_data)
            elif self.body_template2 in type:
                item_widget = self.set_body_template2_widget(json_data)
            elif self.weather_template in type:
                item_widget = self.set_weather_template_widget(json_data)
            elif self.list_template1 in type:
                item_widget = self.set_list_template1_widget(json_data)
        return item_widget

    def set_response_text_widget(self, text):
        item_widget = QtWidgets.QWidget(MainWindow)
        item_widget.setContentsMargins(0, 0, 0, 0)
        item_layout = QtWidgets.QHBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(0)
        item_layout.setAlignment(QtCore.Qt.AlignLeft)
        item_label = QtWidgets.QLabel(MainWindow)
        #设置居中、边框和背景色
        item_label.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        item_label.setStyleSheet(self.label_robot_style)
        #自动换行
        item_label.setWordWrap(True)
        
        answer_text = text
        item_label.setFont(self.globalTextFont)
        #自适应获取当前text对应的label高度
        answer_label_total_height = self.label_height_by_text(item_label, answer_text)
        print("answer_label_total_height: %s"%(answer_label_total_height))
        item_label.setGeometry(0, 0, self.label_max_width, answer_label_total_height)
        
        item_label.setText(answer_text)
        item_layout.addWidget(item_label)
        item_widget.setLayout(item_layout)
        self.answerItem_total_height = answer_label_total_height
        return item_widget

    def set_response_anim_widget(self):
        item_widget = QtWidgets.QWidget(MainWindow)
        item_widget.setContentsMargins(0, 0, 0, 0)
        item_layout = QtWidgets.QHBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(0)
        item_layout.setAlignment(QtCore.Qt.AlignLeft)
        item_label = QtWidgets.QLabel(MainWindow)
        #设置居中、边框和背景色
        item_label.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        item_label.setStyleSheet(self.label_robot_style)
        self.respond_animation = QtGui.QMovie("./res/respond.gif")
        item_label.setMovie(self.respond_animation)
        self.respond_animation.start()

        item_layout.addWidget(item_label)
        item_widget.setLayout(item_layout)
        self.answerItem_total_height = self.label_single_height
        return item_widget
                
    def set_body_template1_widget(self, json_data):
        item_widget = QtWidgets.QWidget(MainWindow)
        item_widget.setContentsMargins(0, 0, 0, 0)
        item_layout = QtWidgets.QHBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(0)
        item_layout.setAlignment(QtCore.Qt.AlignLeft)
        item_label = QtWidgets.QLabel(MainWindow)
        #设置居中、边框和背景色
        item_label.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        item_label.setStyleSheet(self.label_robot_style)
        #自动换行
        item_label.setWordWrap(True)
        
        answer_text = json_data.get('textField',  'NA')
        item_label.setFont(self.globalTextFont)
        #自适应获取当前text对应的label高度
        answer_label_total_height = self.label_height_by_text(item_label, answer_text)
        print("answer_label_total_height: %s"%(answer_label_total_height))
        item_label.setGeometry(0, 0, self.label_max_width, answer_label_total_height)
        
        item_label.setText(answer_text)
        item_layout.addWidget(item_label)
        item_widget.setLayout(item_layout)
        self.answerItem_total_height = answer_label_total_height
        return item_widget
    
    def set_body_template2_widget(self, json_data):
        item_widget = QtWidgets.QWidget(MainWindow)
        item_widget.setContentsMargins(0, 0, 0, 0)
        item_layout = QtWidgets.QVBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(0)
        item_layout.setAlignment(QtCore.Qt.AlignLeft)
        #设置文字label
        item_label = QtWidgets.QLabel(MainWindow)
        #设置居中、边框和背景色
        item_label.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        item_label.setStyleSheet(self.label_robot_style)
        #自动换行
        item_label.setWordWrap(True)
    
        answer_text = json_data.get('textField',  'NA')
        item_label.setFont(self.globalTextFont)
        #自适应获取当前text对应的label高度
        answer_label_total_height = self.label_height_by_text(item_label, answer_text)
        item_label.setGeometry(0, 0, self.label_max_width, answer_label_total_height)
        item_label.setText(answer_text)
        
        #设置图片
        item_image_label = QtWidgets.QLabel(MainWindow)
        item_image_label.setAlignment(QtCore.Qt.AlignLeft)
        item_image_label.setScaledContents(True)
        
		#解析json获取url
        image_urls = [(source .get('size', 'NA'), source .get('url', 'NA')) for source in json_data.get('image',  'NA').get('sources',  'NA')]
        url = image_urls[0][1]
        file_name = os.path.basename(url)
        file_path = "%s/%s"%(os.getcwd(), file_name)
		
		#启动线程下载图片
        download_images_thread = Ui_MainWindow.DownloadImageThread(url, file_path, item_image_label, self.label_max_width, self.label_max_width/ 2)
        download_images_thread.start()
        print("image url: %s"%(url))
        pixmap = QPixmap("./res/loading.png").scaled(self.label_max_width, self.label_max_width/ 2)  
        item_image_label.setPixmap(pixmap)
        item_image_label.setGeometry(0, 0, self.label_max_width, self.label_max_width / 2)
        #添加label到widget
        item_layout.addWidget(item_label)
        item_layout.addWidget(item_image_label)
        self.answerItem_total_height = answer_label_total_height + self.label_max_width/ 2
        return item_widget
        
    def set_weather_template_widget(self, json_data):
        item_widget = QtWidgets.QWidget(MainWindow)
        item_widget.setContentsMargins(0, 0, 0, 0)
        item_layout = QtWidgets.QVBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(0)

        #当前温度的widget
        current_weather_widget = QtWidgets.QWidget(MainWindow)
        current_weather_layout = QtWidgets.QHBoxLayout(current_weather_widget)
        
        #设置main title label
        main_title_label = QtWidgets.QLabel(MainWindow)
        
        #设置居中、边框和背景色
        main_title_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        #自动换行
        main_title_label.setScaledContents(True)
        main_title_label.adjustSize()
        main_title_label.setWordWrap(True)
        main_title_label.setFont(self.globalTextFont)
    
        mian_title_text = json_data.get('title',  'NA').get('mainTitle', 'NA')
        #自适应获取当前text对应的label高度
        main_title_label_total_height = self.label_height_by_text(main_title_label, mian_title_text)
        main_title_label.setGeometry(0, 0, self.label_max_width, main_title_label_total_height)
        main_title_label.setText(mian_title_text)
        
        #设置描述label
        description_label = QtWidgets.QLabel(MainWindow)
        
        #设置居中、边框和背景色
        description_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        #自动换行
        description_label.setScaledContents(True)
        description_label.adjustSize()
        description_label.setWordWrap(True)
        description_label.setFont(self.globalTextFont)
    
        description_text = json_data.get('description', 'NA')
        #自适应获取当前text对应的label高度
        description_label_total_height = self.label_height_by_text(description_label, description_text)
        description_label.setGeometry(0, 0, self.label_max_width, description_label_total_height)
        description_label.setText(description_text)
        
        #设置日期label
        date_item_label = QtWidgets.QLabel(MainWindow)
        
        #设置居中、边框和背景色
        date_item_label.setAlignment(QtCore.Qt.AlignCenter)
        #自动换行
        date_item_label.setScaledContents(True)
        date_item_label.adjustSize()
        date_item_label.setWordWrap(True)
        date_item_label.setFont(self.globalTextFont)
    
        date_text = json_data.get('title',  'NA').get('subTitle', 'NA')
        #自适应获取当前text对应的label高度
        date_item_label.setGeometry(0, 0, self.label_max_width / 3, 2 * self.label_single_height)
        date_item_label.setText(date_text)
        
        #设置图片
        item_image_label = QtWidgets.QLabel(MainWindow)
        item_image_label.setAlignment(QtCore.Qt.AlignCenter)
        item_image_label.setScaledContents(True)
        
        image_urls = [(source.get('url', 'NA')) for source in json_data.get('currentWeatherIcon',  'NA').get('sources',  'NA')]
        url = image_urls[0]
        file_name = os.path.basename(url)
        file_path = "%s/%s"%(os.getcwd(), file_name)
        #启动线程下载图片
        download_images_thread = Ui_MainWindow.DownloadImageThread(url, file_path, item_image_label, self.label_max_width / 6, 2 * self.label_single_height)
        download_images_thread.start()
        pixmap = QPixmap("./res/loading.png").scaled(self.label_max_width / 6, 2 * self.label_single_height)  
        item_image_label.setPixmap(pixmap)
        item_image_label.setGeometry(0, 0, self.label_max_width / 6, 2 * self.label_single_height)
        
        #温度label
        temperature_item_label = QtWidgets.QLabel(MainWindow)
        #设置居中、边框和背景色
        temperature_item_label.setAlignment(QtCore.Qt.AlignCenter)
        #自动换行
        temperature_item_label.setScaledContents(True)
        temperature_item_label.adjustSize()
        temperature_item_label.setWordWrap(True)
        temperature_item_label.setFont(self.globalTextFont)
        current_temp = str(json_data.get('currentWeather',  'NA'))
        low_temp = str(json_data.get('lowTemperature', 'NA').get('value', 'NA'))
        high_temp = str(json_data.get('highTemperature', 'NA').get('value', 'NA'))
        temperature_text = "%s\n%s/%s"%(current_temp, low_temp, high_temp)
        temperature_item_label.setGeometry(0, 0, self.label_max_width / 3, 2 * self.label_single_height)
        temperature_item_label.setText(temperature_text)
        #将三个label加入current_weather_layout
        current_weather_layout.addWidget(date_item_label)
        current_weather_layout.addWidget(item_image_label)
        current_weather_layout.addWidget(temperature_item_label)
        
        #将current_weather_widget加入tem_layout中
        item_layout.addWidget(main_title_label)
        item_layout.addWidget(description_label)
        item_layout.addWidget(current_weather_widget)
        count = 0
        for forcast in json_data.get('weatherForecast', 'NA'):
            #天气预报部分
            forcast_item_weather_widget = QtWidgets.QWidget(MainWindow)
            forcast_item_weather_layout = QtWidgets.QHBoxLayout(forcast_item_weather_widget)
            #设置日期label
            forcast_date_item_label = QtWidgets.QLabel(MainWindow)
        
            #设置居中、边框和背景色
            forcast_date_item_label.setAlignment(QtCore.Qt.AlignCenter)
            #自动换行
            forcast_date_item_label.setScaledContents(True)
            forcast_date_item_label.adjustSize()
            forcast_date_item_label.setWordWrap(True)
            forcast_date_item_label.setFont(self.globalTextFont)
            forcast_day_text = str(forcast.get('day',  'NA'))
            forcast_date_text = str(forcast.get('date',  'NA'))
            forcast_date = "%s\n%s"%(forcast_day_text, forcast_date_text)
            #自适应获取当前text对应的label高度
            forcast_date_item_label.setGeometry(0, 0, self.label_max_width / 3, 2 * self.label_single_height)
            forcast_date_item_label.setText(forcast_date)
        
            #设置图片
            forcast_item_image_label = QtWidgets.QLabel(MainWindow)
            forcast_item_image_label.setAlignment(QtCore.Qt.AlignCenter)
            forcast_item_image_label.setScaledContents(True)
        
            forcast_image_urls = [(forcast_source.get('url', 'NA')) for forcast_source in forcast.get('image',  'NA').get('sources',  'NA')]
            forcast_url = forcast_image_urls[0]
            forcast_file_name = os.path.basename(forcast_url)
            forcast_file_path = "%s/%s"%(os.getcwd(), forcast_file_name)
            #启动线程下载图片
            forcast_download_images_thread = Ui_MainWindow.DownloadImageThread(forcast_url, forcast_file_path, forcast_item_image_label, self.label_max_width / 6, 2 * self.label_single_height)
            forcast_download_images_thread.start()
            forcast_pixmap = QPixmap("./res/loading.png").scaled(self.label_max_width / 6, 2 * self.label_single_height)  
            forcast_item_image_label.setPixmap(forcast_pixmap)
            forcast_item_image_label.setGeometry(0, 0, self.label_max_width / 6, 2 * self.label_single_height)
        
            #温度label
            forcast_temperature_item_label = QtWidgets.QLabel(MainWindow)
            #设置居中、边框和背景色
            forcast_temperature_item_label.setAlignment(QtCore.Qt.AlignCenter)
            #自动换行
            forcast_temperature_item_label.setScaledContents(True)
            forcast_temperature_item_label.adjustSize()
            forcast_temperature_item_label.setWordWrap(True)
            forcast_temperature_item_label.setFont(self.globalTextFont)
            forcast_low_temp = str(forcast.get('lowTemperature', 'NA'))
            forcast_high_temp = str(forcast.get('highTemperature', 'NA'))
            forcast_temperature_text = "%s/%s"%(forcast_low_temp, forcast_high_temp)
            forcast_temperature_item_label.setGeometry(0, 0, self.label_max_width / 3, 2 * self.label_single_height)
            forcast_temperature_item_label.setText(forcast_temperature_text)
            #将三个label加入current_weather_layout
            forcast_item_weather_layout.addWidget(forcast_date_item_label)
            forcast_item_weather_layout.addWidget(forcast_item_image_label)
            forcast_item_weather_layout.addWidget(forcast_temperature_item_label)
            #将forcast_weather_widget加入tem_layout中
            item_layout.addWidget(forcast_item_weather_widget)
            count = count + 1
            if count == 2:
                break
            
        self.answerItem_total_height = (1 + count) * 2 * self.label_single_height + main_title_label_total_height + description_label_total_height
        item_widget.setStyleSheet("background-color:00ff66;border:0.5px solid;border-color:Gainsboro;border-radius:5px;");
        return item_widget

    def set_list_template1_widget(self, json_data):
        item_widget = QtWidgets.QWidget(MainWindow)
        item_widget.setContentsMargins(0, 0, 0, 0)
        item_layout = QtWidgets.QVBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(0)
        
        #设置main title label
        main_title_label = QtWidgets.QLabel(MainWindow)
        
        #设置居中、边框和背景色
        main_title_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        #自动换行
        main_title_label.setScaledContents(True)
        main_title_label.adjustSize()
        main_title_label.setWordWrap(True)
        main_title_label.setFont(self.globalTextFont)
    
        mian_title_text = json_data.get('title',  'NA').get('mainTitle', 'NA')
        #自适应获取当前text对应的label高度
        main_title_label_total_height = self.label_height_by_text(main_title_label, mian_title_text)
        main_title_label.setGeometry(0, 0, self.label_max_width, main_title_label_total_height)
        main_title_label.setText(mian_title_text)
        
        #设置描述label
        subtitle_label = QtWidgets.QLabel(MainWindow)
        
        #设置居中、边框和背景色
        subtitle_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        #自动换行
        subtitle_label.setScaledContents(True)
        subtitle_label.adjustSize()
        subtitle_label.setWordWrap(True)
        subtitle_label.setFont(self.globalTextFont)
    
        subtitle_text = json_data.get('title',  'NA').get('subTitle', 'NA')
        #自适应获取当前text对应的label高度
        subtitle_label_total_height = self.label_height_by_text(subtitle_label, subtitle_text)
        subtitle_label.setGeometry(0, 0, self.label_max_width, subtitle_label_total_height)
        subtitle_label.setText(subtitle_text)
        
        #将titel label加入tem_layout中
        item_layout.addWidget(main_title_label)
        item_layout.addWidget(subtitle_label)
        count = 0
        for list_items in json_data.get('listItems', 'NA'):
            count = count + 1
            #天气预报部分
            list_item__widget = QtWidgets.QWidget(MainWindow)
            list_item_layout = QtWidgets.QHBoxLayout(list_item__widget)
            #计数label
            number_label = QtWidgets.QLabel(MainWindow)
        
            #设置居中、边框和背景色
            number_label.setAlignment(QtCore.Qt.AlignCenter)
            #自动换行
            number_label.setScaledContents(True)
            number_label.adjustSize()
            number_label.setWordWrap(True)
            number_label.setFont(self.globalTextFont)
            count_text = "%s\t"%(count)
            #自适应获取当前text对应的label高度
            number_label.setGeometry(0, 0, self.label_single_height / 2, 2* self.label_single_height)
            number_label.setText(count_text)
        
            #left text label
            left_text_label = QtWidgets.QLabel(MainWindow)
            #设置居中、边框和背景色
            left_text_label.setAlignment(QtCore.Qt.AlignCenter)
            #自动换行
            left_text_label.setScaledContents(True)
            left_text_label.adjustSize()
            left_text_label.setWordWrap(True)
            left_text_label.setFont(self.globalTextFont)
            left_text = list_items.get('leftTextField', 'NA')
            #自适应获取当前text对应的label高度
            left_text_label.setGeometry(self.label_single_height, 0, self.label_single_height, 2 * self.label_single_height)
            left_text_label.setText(left_text)
        
            #left text label
            right_text_label = QtWidgets.QLabel(MainWindow)
            #设置居中、边框和背景色
            right_text_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter)
            #自动换行
            right_text_label.setScaledContents(True)
            right_text_label.adjustSize()
            right_text_label.setWordWrap(True)
            right_text_label.setFont(self.globalTextFont)
            right_text = list_items.get('rightTextField', 'NA')
            #自适应获取当前text对应的label高度
            right_text_label.setGeometry(self.label_single_height, 0, self.label_single_height, 2 * self.label_single_height)
            right_text_label.setText(right_text)
            #将三个label加入current_weather_layout
            list_item_layout.addWidget(number_label)
            list_item_layout.addWidget(left_text_label)
            list_item_layout.addWidget(right_text_label)
            #将forcast_weather_widget加入tem_layout中
            item_layout.addWidget(list_item__widget)
            if count == 2:
                break
            
        self.answerItem_total_height = count * 2 * self.label_single_height + main_title_label_total_height + subtitle_label_total_height
        item_widget.setStyleSheet("background-color:00ff66;border:0.5px solid;border-color:Gainsboro;border-radius:5px;");
        return item_widget
    
    class DownloadImageThread(threading.Thread):
        #代理地址和端口号
        proxy_addr = "172.20.30.1:3128"
        def __init__(self, url, file_path, item_image_label, width, height):
            threading.Thread.__init__(self)
            self.url = url
            self.file_path = file_path
            self.item_image_label = item_image_label
            self.width = width
            self.height = height
        
        def run(self):
            if os.path.exists(self.file_path):
                print("image exist")
                self.image_download_success()
                return
              
            #设置网络下载代理
            #proxy = urllib.request.ProxyHandler({'https': self.proxy_addr})
            #opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
            #urllib.request.install_opener(opener)
            f = open(self.file_path,'wb') #注意第二个参数要写成wb，写成w会报错  
            req = urllib.request.urlopen(self.url)  
            buf = req.read()
            f.write(buf)
            self.image_download_success()
        
        #下载图片后更新image_label
        def image_download_success(self):
            pixmap = QPixmap(self.file_path).scaled(self.width, self.height)  
            self.item_image_label.setPixmap(pixmap)
            self.item_image_label.setGeometry(0, 0, self.width, self.height)
    
    class FileEventHandler(FileSystemEventHandler):
        def __init__(self, f):
            FileSystemEventHandler.__init__(self)
            self.func = f

        #文件移动动作
        def on_moved(self, event):
            if event.is_directory:
                print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
            else:
                print("file moved from {0} to {1}".format(event.src_path,event.dest_path))

        #文件创建动作
        def on_created(self, event):
            if event.is_directory:
                print("directory created:{0}".format(event.src_path))
            else:
                print("file created:{0}".format(event.src_path))
                self.func()
                
        #文件删除动作
        def on_deleted(self, event):
            if event.is_directory:
                print("directory deleted:{0}".format(event.src_path))
            else:
                print("file deleted:{0}".format(event.src_path))

        #文件修改动作
        def on_modified(self, event):
            if event.is_directory:
                print("directory modified:{0}".format(event.src_path))
            else:
                self.func()
  
    

    class StateObserverThread(QThread):
        # 定义信号,定义参数为str类型
        _state_signal = pyqtSignal()
        def __init__(self, parent=None):
            super().__init__(parent)
            self.old_state = getDialogState()            
        
        def notify(self):
            self._state_signal.emit()
        
        def initFileObserver(self):
            #file observer
            observer = Observer()
            path = os.getcwd()
            event_handler = Ui_MainWindow.FileEventHandler(self.notify)
            observer.schedule(event_handler, path, True)
            observer.start()

        def run(self):
            self.initFileObserver()

    #For xunfei
    class FifoObserverThread(QThread):
        data_signal = pyqtSignal(str)
        def __init__(self, parent=None):
            super().__init__(parent)

        def run(self):
            fifo="voice_control_fifo"
            fd=open(fifo,"r")
            while True:
                line = fd.readline()
                if line !="":
                    self.data_signal.emit(line)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    # 创建线程
    #thread = Ui_MainWindow.StateObserverThread()
    # 注册信号处理函数
    #thread._state_signal.connect(ui.update_state)
    #thread.start()

    # for xunfei 创建线程
    thread = Ui_MainWindow.FifoObserverThread()
    # 注册信号处理函数
    thread.data_signal.connect(ui.pre_process_data)
    thread.start()

    sys.exit(app.exec_())
