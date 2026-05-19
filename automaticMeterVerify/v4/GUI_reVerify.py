import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

# ======== 配置区 =======
UI_FILE = "water_meter.ui"
# =====================

class AuditApp(QMainWindow):
	#我记得说过了，class name(father'sName):
	#表示继承了QMainWindows
	#qt的一个主窗口类
	def __init__(self):
		super().__init__()
		#super()指向父类，这里指先运行父类的__init__()


		# 读ui
		ui_file= QFile(UI_FILE)
		# qt是C++的东西，所以不能用python原生文件对象open()，
		#QFIle只是建立链接
		if not ui_file.open(QFile.ReadOnly):
			#权限QFile.ReadOnly
			#类似open(f, 'r')
			print("找不到文件")
			sys.exit(-1)


		#self.ui = QUiLoader().load(ui_file, self)
		#不用这个，因为AuditApp这个实例继承了QMainWindow,.ui也是一个QMainWindow
		#会有灵异事件
		loader = QUiLoader() #实例化qt的加载器
		self.ui=loader.load(ui_file)
		#self.setCentralWidget(self.ui)
		ui_file.close()

		# 把ui设为主界面
		if self.ui:
			self.setCentralWidget(self.ui)
		else:
			print("ui加载失败")
			return
#706450005890178055391

		self.setWindowTitle("reVerify_G2V1")

		self.tasks=[]
		self.current_page=0
		self.mock_load_data()
		self.refresh_ui()


		#测试
		'''
		try:
			#progress标签
			self.ui.progress.setText("progress label")

			self.ui.text_0.setText("文本区")

			self.ui.img_0.setStyleSheet("background-color: #2c3e50; color: white;")
			# css支持
			self.ui.img_0.setText("图片位置")

		except AttributeError as e:
			print(f"UI绑定失败:{e}")
			'''

	def mock_load_data(self):
		for i in range(10):
			self.tasks.append({
				"target":f"期望{i}",
				"path":f"img{i}.jpg",
				"name":f"user_{i}"
			})

	def refresh_ui(self):
		start_idx = self.current_page*4

		for i in range(4):
			lbl_img = getattr(self.ui, f"img_{i}")
			lbl_text = getattr(self.ui, f"text_{i}")

			task_idx = start_idx + i

			# 只有当索引没有越界时，才去拿数据
			if task_idx < len(self.tasks):
				# 取出字典
				task = self.tasks[task_idx]

				# 2. 设置文字
				lbl_text.setText(f"{task['name']} | {task['target']}")

				# 3. 加载图片 (现在 task 是个字典了，可以用 task['path'] 了)
				pix = QPixmap(task['path'])
				#QPimax会把图片读出来化为可以贴的图
				print(task['path'])

				# 4. 把图片塞进 Label，并按 img 的大小进行缩放
				lbl_img.setPixmap(pix)

			# 绝对不要在这里再写 lbl_img.setText() 了，否则图片会被文字顶掉！

			else:
				# 如果越界了（比如最后一页只有2张图，第3、4个格子就是空的）
				lbl_text.setText("-----")
				lbl_img.clear()  # 清空之前的图片
				lbl_img.setText("noPics")

		total_pages=(len(self.tasks)+3) // 4
		#向上取整，地板除， python的5/4=1.25， 5//4=1
		self.ui.progress.setText(f"No. {self.current_page+1}/{total_pages}")

	def keyPressEvent(self, event):
		#event,运行app.exec()就会一直问
		#按下了空格 -> Windows 抓到了 -> 告诉了 Qt -> Qt 产生了一个 QKeyEvent 对象（灰字类型提示）
		# -> Qt 发现当前窗口 AuditApp -> Qt 自动调用 keyPressEvent 并把那个对象塞给 event 参数。

		if event.key() == Qt.Key_Space:
			if(self.current_page+1)*4 < len(self.tasks):
				self.current_page+=1
				self.refresh_ui()
				print("翻页成功")
			else:
				print("已经是最后一页了")

		elif event.key() == Qt.Key_Z:
			if self.current_page > 0:
				self.current_page -= 1
				self.refresh_ui()
				print("回退上一页")

if __name__ == "__main__":
	app = QApplication(sys.argv)
	#Qt跨平台的，可以比如python main.py --style=windows，来给qt塞指令
	window = AuditApp()
	window.show()
	sys.exit(app.exec())
