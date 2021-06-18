## WFQ

### 使用方式[Linux]
- 本机网卡新增配置6个IP地址，分别是 172.16.1.1 172.16.1.2 172.16.1.3 172.16.1.254 172.16.2.1 172.16.2.2
- python3 ControlPlane.py
- 网页打开 127.0.0.1 依次点击网页按钮启动Router/Receiver/Sender

### 使用方式[Windows]
- 本机网卡新增配置6个IP地址，分别是 172.16.1.1 172.16.1.2 172.16.1.3 172.16.1.254 172.16.2.1 172.1
6.2.2
- python3 ControlPlane.py
- 网页打开 127.0.0.1
- python3 Router.py
- python3 Receiver.py
- python3 Sender.py
- python3 Sender.py
- python3 Sender.py
> Sender启动三次，每次启动都会从控制器获取不同的配置文件，虽然代码一样。

### 已解决
- [x] 算法RN(if) = FN
- [x] Sender 启动多个数据错误
- [x] 图片实时数据需要处理
- [x] 动态修改table单元格边框
- [x] Sender 不会读取配置文件
- [x] 网页默认值问题
- [x] 点击启动按钮，使用子进程解决（确保Linux能使用）
