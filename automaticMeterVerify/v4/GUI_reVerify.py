import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import pandas as pd

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

		self.task=[]
		self.current_page=0
		self.mock_load_data()
		self.refresh_ui()


		#测试
		try:
			#progress标签
			self.ui.progress.setText("progress label")

			self.ui.text_0.setText("文本区")

			self.ui.img_0.setStyleSheet("background-color: #2c3e50; color: white;")
			# css支持
			self.ui.img_0.setText("图片位置")

		except AttributeError as e:
			print(f"UI绑定失败:{e}")

	def mock_load_data(self):
		for i in range(10):
			self.task.append({
				"target":f"期望{i}",
				"path":f"img{i}.jpg",
				"name":f"user_{i}"
			})

	def refresh_ui(self):
		start_idx = self.current_page*4

		for i in range(4):
			lbl_img=getattr(self.ui, f"img_{i}")
			lbl_text=getattr(self.ui, f"text_{i}")

			task_idx=start_idx+i

			if task_idx<len(self.task):
				task=self.task[task_idx]
				lbl_text.setText(f"{task['name']}|{task['target']}")
				lbl_img.setText(f"load pic here:{task['path']}")

			else:
				lbl_text.setText("-----")
				lbl_img.setText("noPics")

		total_pages=(len(self.task)+3) // 4
		self.ui.progress.setText(f"No. {self.current_page+1}/{total_pages}")

if __name__ == "__main__":
	app = QApplication(sys.argv)
	#Qt跨平台的，可以比如python main.py --style=windows，来给qt塞指令
	window = AuditApp()
	window.show()
	sys.exit(app.exec())
