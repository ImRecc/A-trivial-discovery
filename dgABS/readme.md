注意所有的ABS DG相关都暂时只是测试
需要后续补全
## 首先socket会一直保持连接，http(s)收到回复后就断链了
#### 然后python的传参和c系不同，
```
sys_ctrl = shockSystem()
#这个有点像传递了class shockSystem的地址，但python里，其实是method bound,
threading.Thread(target=self.sys_ctrl.connect, args=(self,))
#比如这里，就给了target函数代码的地址：ShockSystem.connect 的指令。
#实例的内存地址：sys_ctrl 对象的地址

threading.Thread(target=函数入口, args=(剩下的参数库,), daemon=生死同步)
target=func()，那么就是一个函数的地址，如果是类似sys_ctrl.connect,传进去的是一个结构体，包含了“函数地址”+“实例地址（sys_ctrl）”
并且如果是后者，绑定方法，那么会把实例地址sys_ctrl自动传入
然后args,类似argvs[]，传的是元组（c里的数组），所以（self,）这个代表“只有一个元素的数组”，不然不加","，就会被判定会invalid
```
