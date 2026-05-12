#### 首先是个冷知识：大伙都干了，都偷了奥特曼的api那一套
```
curl -X 'POST' \
http://0.0.0.0:8000/v1/chat/completions' \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
        "model": "nvidia/nemotron-nano-12b-v2-vl",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url":
                            {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                            }
                    }
                ]
            }
        ],
        "max_tokens": 1024
    }
```

这个是nvidia的，\
curl是linux的玩意，这里用了python的request.post替换 \
```
    X POST：代表你要寄一个包裹（而不是像 GET 那样去拿包裹）。对应 requests.post()。
    -H (Header, 请求头)：这是包裹外面的快递单
    -H 'Content-Type: application/json' 意思是快递单上写明：“里面装的是 JSON 格式的东西”。
    -d (Data, 数据/请求体)：这是包裹里面装的真正物品。

    也就可以写成：
    requests.post(INVOKE_URL, headers=headers, json=payload, timeout=30)

    英伟达还贴心的组织了如何用base64编码图片：

    def encode_media_base64(media_file):
    with open(media_file, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
        #找英伟达偷的
```

##### 然后返回值：
```
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "nvidia/nemotron-nano-12b-v2-vl",
  "choices":[
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "555.0\n"  <--- 我们要的数据在这里！！！
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 9,
    "completion_tokens": 12,
    "total_tokens": 21
  }
}
```
这个样子\

#### 关于多线程：
首先是基本的 ` import threading 里的threading.Thread(funcAddress, daemon=).start()` 
需要大量手搓管理线程 \
常用的是 ` from concurrent.futures import ThreadPoolExecutor, as_completed `
```
def single_tast(val):
with ThreadPoolExecutor(max_workers = MAX_WORKERS) as executor:
    for i in range(10):
        executor.submit(single_tast, i)
#或者
todo=[]
with ThreadPoolExecutor(max_workers=3) as executor:
    # 方式 A：直接传一个列表 (todo 就是一个列表)
    executor.map(single_task, todo) 
    
    # 方式 B：传一个 range 序列
    executor.map(single_task, range(10))
#或者用字典展开式
with ThreadPoolExecutor(max_workers=3) as executor:
    # 完美利用字典推导式的特性，一边拉起循环，一边提交任务，一边生成字典，python是屁股先看
    ticket_map = {executor.submit(single_task, i): i for i in range(10)}
    
    # 配合 as_completed 监听
    for ticket in as_completed(ticket_map):
        # 任务完成了
        # 去字典里查一下就知道谁完成
        original_i = ticket_map[ticket] 
        print(f"参数为 {original_i} 的任务刚刚完成")
