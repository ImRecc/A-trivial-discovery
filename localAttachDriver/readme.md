flask是一个python用的后端，拿了把url请求映射到python\
对比 C 语言：在 C 里，如果你要写一个 Web 服务器，你得处理原始的 Socket、解析 HTTP 报文头、处理各种字符串拼接。\

Flask 的作用：它把这些脏活累活全包了。“如果有人访问 /upload 这个地址，就去运行 upload_file() 这个函数”。\
```
<li> 以内的内容会变成一行新的东西，列表一样 ，配合for循环来列文件列表这些</li>
```
<li>比如</li>

比如有个class Mint:
此时，在某处调用plant = Mint(paraA) \
Python 在内存里 malloc 了一块空间，用来存放这个新对象。\
Python 自动调用 MiniNasGui.__init__(这块内存的地址, root)。\
初始化完成后，把这块内存的地址赋给变量 app \

Python 强迫把这个“当前实例的内存地址”写在第一个参数上， \
让人时刻清楚：self.ip_label 是绑定在这个特定内存块上的数据，而不是全局变量 \

这东西可以改名：
```
class MiniNasGui:
    def __init__(this_instance, root):
        this_instance.ip_label = "xxx"
```
