#### 首先是个冷知识：大伙都干了，都偷了奥特曼的api那一套
```
curl -X 'POST' \
'http://0.0.0.0:8000/v1/chat/completions' \
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
    }'
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
    ```
    英伟达还贴心的组织了如何用base64编码图片：
    ```
    def encode_media_base64(media_file):
    with open(media_file, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
        #找英伟达偷的
    ```
    
