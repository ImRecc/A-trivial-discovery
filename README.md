#### 关于调用api
见 ./automaticMeterVerify/V4/readme.md

#### 关于port forwarding\intranet penetration
like in vps, frps.toml
bindPort=7000
./frps -c frps.toml
in local PC, frpc.toml
```
serverAddr = "x"
serverPort = 7000

# If you are using Clash TUN Global, you don't need the proxyURL line here.
# Just let Clash TUN handle the routing.

[transport]
# Tell frpc to connect to the VPS through your local Clash proxy!

proxyURL = "socks5://127.0.0.1:7890"

# Send a heartbeat every 10 seconds to keep the proxy node alive

#heartbeatInterval = 10
#heartbeatTimeout = 90

[[proxies]]
name = "normal intraNet penertration"
type = "tcp"
#for gaming, switch this to udp
localIP = "127.0.0.1"
localPort = 8000      # <--- Changed to match your Python app
remotePort = 6001     # <--- The port exposed on the VPS
# dont use 6000, it's x11(graphic app)'s, and banned for other apps

# it's gonna forwarding every traffic inbound to "vps:6001" into "localPC:8000
# don't forgot rise client on windows, frpc -c frpc.toml

### we could do `nohup ./frps -c frps.toml > frps.log 2>&1 &`
### or 
  ``` apt install screen
      screen -S my_frp    # Creates a new virtual window
      ./frps -c frps.toml # Run your program
  ```
```
and use `press Ctrl+A, then D to "detach" , screen -r my_frp to go back to that exact window`
