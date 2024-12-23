import socket
import threading
import sys
import libnum
import base64
import time
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton,QFileDialog,QToolButton,QMenu,QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class ServerGUI(QWidget):
    """服务器图形界面类"""

    def __init__(self):
        """初始化服务器界面及其组件"""
        super().__init__()
        self.init_jiemian()#初始化界面
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#创建服务器套接字
        self.server.bind(("0.0.0.0", 8088))#绑定服务器地址和端口
        self.server.listen(3)#设置最大连接数为3
        self.client_socket = None#客户端套接字
        threading.Thread(target=self.accept_connection, daemon=True).start()#启动接收客户端连接的线程

    def init_jiemian(self):
        """设置界面的各种组件"""
        self.setWindowTitle("服务器")#设置窗口标题
        layout = QVBoxLayout()#创建垂直布局
        self.resize(800, 600)#设置窗口大小
        self.setStyleSheet("background-color: LightBlue;")#设置背景颜色
        #设置窗口图标
        self.setWindowIcon(QIcon("./icon3.png"))


        # 创建聊天内容显示框
        self.chat_box = QTextEdit()#设置聊天内容显示框为QTextEdit
        self.chat_box.setReadOnly(True)#设置聊天内容显示框为只读
        layout.addWidget(self.chat_box)#添加聊天内容显示框到垂直布局中
        #设置聊天框的背景图片
        self.chat_box.setStyleSheet("background-image: url(./background5.jpg);")

        # 创建一个水平布局，用于容纳输入框和删除按钮、发送按钮
        h_layout = QHBoxLayout()
        #调整窗口大小
        self.resize(625, 425)

        # 创建输入消息框
        self.entry = QLineEdit()
        h_layout.addWidget(self.entry)
        # 设置输入框的背景颜色
        self.entry.setStyleSheet("background-color: white;")

         # 创建文件发送按钮
        self.file_button = QToolButton(self)#创建文件按钮
        self.file_button.setText("文件")#设置按钮文字
        self.file_button.setPopupMode(QToolButton.InstantPopup)#设置按钮弹出菜单模式
        self.file_menu = QMenu(self.file_button)#创建菜单对象
        self.file_button.setMenu(self.file_menu)#设置按钮菜单
        self.file_action = QAction("发送文件", self)#创建菜单项
        self.file_action.triggered.connect(self.send_file)#设置菜单项的触发事件
        self.file_menu.addAction(self.file_action)#添加菜单项到菜单
        h_layout.addWidget(self.file_button)#添加文件按钮到水平布局中
        # 设置文件按钮的背景颜色
        self.file_button.setStyleSheet("background-color: white;")

        # 创建删除按钮
        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self.chat_box.clear)#设置删除按钮的点击事件
        h_layout.addWidget(self.delete_button)#添加删除按钮到水平布局中
        # 设置删除按钮的背景颜色
        self.delete_button.setStyleSheet("background-color: red;")#设置删除按钮的背景颜色

        # 创建发送表情按钮
        # 表情按钮（这里用QToolButton和QMenu来实现下拉菜单）
        self.emoji_button = QToolButton(self)
        self.emoji_button.setText("😀")  # 初始显示一个表情作为按钮图标
        self.emoji_button.setPopupMode(QToolButton.InstantPopup)  # 设置为即时弹出菜单模式
        # 创建表情菜单
        self.emoji_menu = QMenu(self.emoji_button)  # 创建菜单对象
        emojis = ["😀", "😢", "😠", "😍", "😴", "🤔","🐱","🐶","😏","😪"]  # 示例表情列表
        for emoji in emojis:
            action = QAction(emoji, self)
            action.triggered.connect(lambda _, e=emoji: self.insert_emoji(e))
            self.emoji_menu.addAction(action)

        self.emoji_button.setMenu(self.emoji_menu)  # 设置菜单为表情菜单
        # 表情按钮
        h_layout.addWidget(self.emoji_button)

        # 创建发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)#设置发送按钮的点击事件
        h_layout.addWidget(self.send_button)#添加发送按钮到水平布局中
        # 设置输入框的回车键发送消息
        self.entry.returnPressed.connect(self.send_message)
        # 设置发送按钮的背景颜色
        self.send_button.setStyleSheet("background-color: green;")

        emoji = '😏'  # Emoji字符
        #在消息框中显示你好消息加个😏表情符号
        self.chat_box.append(f"<span style='color:blue'>你好，欢迎来到聊天室{emoji}</span>")
        #self.chat_box.append("<span style='color:blue'>你好，欢迎来到聊天室</span>")


        #将水平布局添加到主垂直布局中
        layout.addLayout(h_layout)
        self.setLayout(layout)


    def accept_connection(self):
        """接受客户端连接并启动接收消息的线程"""
        while True:
            client_socket, addr = self.server.accept()#等待客户端连接
            print(f"客户端 {addr} 已连接")#打印客户端连接信息
            self.client_socket = client_socket#保存客户端套接字
            threading.Thread(target=self.receive_messages, daemon=True).start()#启动接收客户端消息的线程
            break

    #删除按钮的槽函数
    def delete_message(self):
        """清除聊天记录"""
        self.chat_box.clear()


    # 文件发送按钮的槽函数
    def send_file(self):
        """发送文件到客户端"""
        file_name, _ = QFileDialog.getOpenFileName(self, "选择文件", os.getcwd(), "All Files (*)")
        if file_name:
            with open(file_name, 'rb') as f:
                file_data = f.read()#读取文件数据
            # 发送文件数据
            if self.client_socket:
                self.client_socket.sendall(file_data)
                #显示发送文件消息
                self.chat_box.append(f"<span style='color:green'>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}</span>")
                self.chat_box.append(f"<span style='color:purple'>自己: 已发送文件 {file_name}</span>")
            else:
                print("客户端未连接")
                self.chat_box.append(f"<span style='color:red'>客户端未连接</span>")




    # 可以选择哪种表情发送的槽函数
    def insert_emoji(self, emoji):
        """将选中的表情插入到消息输入框中"""
        self.entry.insert(emoji)

    def receive_messages(self):
        """接收客户端发送的消息并更新聊天框"""
        while True:
            try:
                message = (self.client_socket.recv(2048).decode('utf-8'))
                if message:
                    # AES解密消息
                    #key = '1qaz@WSXabcdefgh'  # 秘钥
                    #message = self.aes_ECB_Decrypt(message, key)
                    # RSA解密消息
                    #message = self.rsa_Decrypt(int(message))
                    #将收到的信息变成长整型
                    #c = int(message)
                    #m = pow(c, d, n)
                    #message = libnum.n2s(message).decode()
                    #显示收到消息的时间
                    self.chat_box.append(f"<span style='color:green'>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}</span>")
                    self.chat_box.append(f"<span style='color:purple'>{message}</span>")
            except ConnectionResetError:
                print("客户端断开连接")
                #在显示框中显示客户端断开连接
                self.chat_box.append(f"<span style='color:red'>客户端断开连接</span>")
                self.client_socket = None
                break

    def send_message(self):
        """发送消息到客户端并更新聊天框"""
        message = self.entry.text()
        # AES加密消息
        #key = '1qaz@WSXabcdefgh'  # 秘钥
        #message = self.aes_ECB_Encrypt(message, key)

        # RSA加密消息
        #message = self.rsa_Encrypt(message)
        #m = libnum.n2s(message)
        #c = pow(m, e, n)
        #message = str(c)
        # 发送消息
        if self.client_socket:
            #显示当前时间
            self.chat_box.append(f"<span style='color:green'>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}</span>")
            self.chat_box.append(f"<span style='color:purple'>自己: {message}</span>")
            #发送发送消息时的时间
            #self.client_socket.send(str(int(time.time())).encode('utf-8'))
            self.client_socket.send(message.encode('utf-8'))
            self.entry.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)#创建QApplication对象
    server_gui = ServerGUI()#创建服务器GUI对象
    server_gui.show()#显示服务器GUI
    sys.exit(app.exec_())#运行程序，直到退出
