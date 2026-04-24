### 一点 request.get()的小知识：

def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": BAIDU_API_KEY, "client_secret": BAIDU_SECRET_KEY}
    #baidu api要求把目的、id、密钥在网址后传递过去
    try:
        response = requests.get(url, params=params, verify=False, timeout=10)
        return response.json().get("access_token")
        # get(地址、参数、python无需验证、10秒超时)
        # response.json().get("access_token")
        # requests包的内置方法json()，能直接把返回的json给dump成字典
    #所以无需 tempDic=json.load(response),直接dictionary.get(key)就行
    #理论上读文档得了，
    '''大概长这样：
    {
  "refresh_token": "25.3f9f...xxx",
  "expires_in": 2592000,
  "session_key": "9mzd...xxx",
  "access_token": "24.3f9f...xxx",
  "scope": "brain_all_scope"
}
'''
    except: return None
    

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(img_url, headers=headers, timeout=15)

这个get干的事情是直接有完整的路径，所以只需要再搞个headers做伪装就结束了
