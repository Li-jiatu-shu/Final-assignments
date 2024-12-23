import socket
import threading
import sys
import libnum
import base64
import time
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QToolButton, QMenu, QAction, QListWidget, QMessageBox, QScrollArea, QGridLayout
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat, QPalette, QBrush, QLinearGradient
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon



class LoginWindow(QWidget):
    """ 登录窗口类，用于处理用户登录界面及逻辑 """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """ 初始化登录窗口的用户界面 """
        self.setWindowTitle("登录窗口")
        self.setGeometry(600, 500, 300, 400)
        # 创建渐变色
        gradient = QLinearGradient(0, 0, 0, 400)  # 垂直渐变
        # 使用QColor定义颜色
        gradient.setColorAt(0, QColor("SkyBlue"))  # 起始颜色
        gradient.setColorAt(0.5, QColor("LightCyan"))  # 中间颜色
        gradient.setColorAt(1, QColor("LightPink"))  # 结束颜色

        # 设置窗口背景为渐变色
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        #设置窗口图标
        self.setWindowIcon(QIcon("icon2.png"))

        layout = QGridLayout()  # 创建布局
        # 用户名、IP地址、端口号输入框
        self.username_edit = self.create_input("请输入用户名", 0, 2, layout)  # 设置为中间列
        self.username_edit.setFixedWidth(300)
        self.username_edit.setFixedHeight(40)

        self.ip_edit = self.create_input("请输入IP地址", 1, 2, layout)  # 设置为中间列
        self.ip_edit.setFixedWidth(300)
        self.ip_edit.setFixedHeight(40)

        self.port_edit = self.create_input("请输入端口号", 2, 2, layout)  # 设置为中间列
        self.port_edit.setFixedWidth(300)
        self.port_edit.setFixedHeight(40)

        # 登录按钮
        self.button_login = QPushButton("登录")

        self.button_login.setStyleSheet("background-color: green; color: white;")
        self.button_login.setFixedHeight(50)
        self.button_login.clicked.connect(self.login)
        layout.addWidget(self.button_login, 3, 1, 1, 3)  # 登录按钮保持在中间列
        #将登录按键绑定回车键
        self.button_login.setShortcut(Qt.Key_Return)
        self.setLayout(layout)

    # 创建输入框
    def create_input(self, placeholder, row, col, layout):
        input_edit = QLineEdit()
        input_edit.setPlaceholderText(placeholder)
        layout.addWidget(input_edit, row, col)
        return input_edit
    #登录按钮的槽函数
    def login(self):
        username = self.username_edit.text().strip()#用户名
        ip = self.ip_edit.text().strip()#IP地址
        port = self.port_edit.text().strip()#端口号

        if not username or not ip or not port:
            QMessageBox.warning(self, "错误", "用户名、IP地址和端口号不能为空")
            return

        try:
            port_number = int(port)
            if not (1 <= port_number <= 65535):
                raise ValueError("端口号必须在1到65535之间")
        except ValueError as e:
            QMessageBox.warning(self, "错误", str(e))
            return
        #传递用户名、IP地址、端口号到主窗口

        self.main_window = ClientGUI(username, ip, port_number)#创建主窗口
        self.main_window.show()#显示主窗口
        self.close()



class ClientGUI(QWidget):#客户端GUI类
    """客户端图形用户界面类"""
    def __init__(self, username, ip, port_number):
        """初始化客户端GUI，包括窗口设置和socket连接"""
        super().__init__()
        self.init_jiemian()#初始化界面
        self.username = username#用户名
        print(f"用户名：{self.username}")#打印用户名
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#创建socket对象
        self.client.connect((ip, port_number))#连接服务器
        threading.Thread(target=self.receive_messages, daemon=True).start()#启动接收消息线程

    def init_jiemian(self):
        """初始化用户界面，包括聊天框、输入框和按钮等组件的设置"""
        self.setWindowTitle("客户端")#设置窗口标题
        layout = QVBoxLayout()#创建垂直布局
        self.resize(800, 600)  # 设置窗口大小
        # 设置窗口图标
        self.setWindowIcon(QIcon("./icon4.png"))#设置窗口图标

        # 创建聊天内容显示框
        self.chat_box = QTextEdit()#创建聊天框
        self.chat_box.setReadOnly(True)#设置聊天框为只读
        layout.addWidget(self.chat_box)#添加聊天框到布局中
        self.chat_box.setStyleSheet("background-image: url(./backgroun12.jpg);")#设置聊天框背景图片



        # 创建一个水平布局，用于容纳输入框和删除按钮、发送按钮
        h_layout = QHBoxLayout()
        # 调整窗口大小
        self.resize(625, 425)
        # 创建输入消息框
        self.entry = QLineEdit()
        h_layout.addWidget(self.entry)#添加输入框到水平布局

        # 创建删除按钮
        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self.chat_box.clear)
        h_layout.addWidget(self.delete_button)
        #设置删除按钮的背景颜色
        self.delete_button.setStyleSheet("background-color: red; color: white;")
        # 设置删除按钮的大小

        # 创建发送表情按钮
        # 表情按钮（这里用QToolButton和QMenu来实现下拉菜单）
        self.emoji_button = QToolButton(self)
        self.emoji_button.setText("😍")  # 初始显示一个表情作为按钮图标
        self.emoji_button.setPopupMode(QToolButton.InstantPopup)  # 设置为即时弹出菜单模式
        # 创建表情菜单
        self.emoji_menu = QMenu(self.emoji_button)  # 创建菜单对象
        emojis = ["😄", "😢", "😠", "😍", "😴", "🤔", "🐱", "🐶", "😏", "😪"]  # 示例表情列表
        for emoji in emojis:#遍历表情列表
            action = QAction(emoji, self)
            action.triggered.connect(lambda _, e=emoji: self.insert_emoji(e))#绑定表情菜单的槽函数
            self.emoji_menu.addAction(action)

        self.emoji_button.setMenu(self.emoji_menu)  # 设置菜单为表情菜单
        # 表情按钮
        h_layout.addWidget(self.emoji_button)

        # 创建发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)#绑定发送按钮的槽函数
        h_layout.addWidget(self.send_button)#添加发送按钮到水平布局
        # 设置输入框的回车键发送消息
        self.entry.returnPressed.connect(self.send_message)
        # 设置发送按钮的背景颜色
        self.send_button.setStyleSheet("background-color: green; color: white;")

        emoji = '😀'  # Emoji字符
        # 在消息框中显示欢迎用户信息，并加个😀表情符号
        self.chat_box.append(f"<span style='color:blue'>你好，欢迎来到聊天室{emoji}</span>")
        # self.chat_box.append("<span style='color:blue'>你好，欢迎来到聊天室</span>")

        # 将水平布局添加到主垂直布局中
        layout.addLayout(h_layout)
        self.setLayout(layout)

    def receive_messages(self):
        """接收服务器发送的消息并显示在聊天框中"""
        while True:
            try:
                message = self.client.recv(2048).decode('utf-8')
                #判断收到消息是否为空
                if message:
                    # 解密消息
                    #key = '1qaz@WSXabcdefgh'  # 秘钥
                    #message = self.aes_ECB_Decrypt(message, key)
                    # RSA解密消息
                    #message = self.rsa_Decrypt(message)
                    #c = int(message)
                    #m = pow(c, d, n)
                    #message = libnum.n2s(message).decode()
                    self.chat_box.append(f"<span style='color:green'>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}</span>")
                    self.chat_box.append(f"服务器: {message}")
            except ConnectionResetError:
                #在显示框中显示服务器断开连接信息
                self.chat_box.append(f"<span style='color:red'>服务器断开连接</span>")
                print("服务器断开连接")
                break

    # 删除按钮的槽函数
    def delete_message(self):
        """清空聊天框中的所有消息"""
        self.chat_box.clear()

    # 可以选择哪种表情发送的槽函数
    def insert_emoji(self, emoji):
        """将选中的表情插入到消息输入框中"""
        self.entry.insert(emoji)

    def send_message(self):
        """发送用户输入的消息并显示在聊天框中"""
        message = self.entry.text()
        # 显示发送的消息
        #self.chat_box.append(f"<span style='color:green'>你: {message}</span>")
        # RSA加密消息
        #message = self.rsa_Encrypt(message)
        #key = '1qaz@WSXabcdefgh'  # 秘钥
        #message = self.aes_ECB_Encrypt(message, key)
        #RSA加密消息
        #message = self.rsa_Encrypt(message)
        #m = libnum.n2s(message)
        #c = pow(m, e, n)
        #message = str(c)
        # 发送消息
        self.chat_box.append(f"<span style='color:green'>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}</span>")
        # 显示发送的消息
        #self.chat_box.append(f"<span style='color:orange'>自己: {message}</span>")
        self.chat_box.append(f"<span style='color:orange'>{self.username}: {message}</span>")
        message = f"{self.username}:{message}"
        # 发送用户名和消息到服务器
        self.client.send(message.encode('utf-8'))
        #self.chat_box.append(f"<span style='color:green'>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}</span>")
        self.entry.clear()



if __name__ == "__main__":
    """程序入口点，启动客户端GUI并运行事件循环"""
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
