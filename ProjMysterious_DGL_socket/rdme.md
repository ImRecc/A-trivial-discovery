首先这玩意以来node.js
所以需要下node.js
然后用npm (node package manager)（windows powershell不支持.ns1，而这玩意大量用到npm.ns1,所以
需要Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
管理员运行
）
然后到backend文件夹里，有个package.json,直接npm install, 下载所有依赖，然后npm start来找比如 ./src/script.js里的东西来运行
和apache服务器全家桶不同，这玩意只是一个引擎，有点极简

New-NetFirewallRule -DisplayName "DGLAB_Socket" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 9999
windows的防火墙就是这么霸道，所以需要自己打开入站防火墙规则
当然也可以手动挡去windows firewall里自己新建规则
