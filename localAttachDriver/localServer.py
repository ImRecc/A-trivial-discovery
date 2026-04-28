from flask import Flask, render_template_string, request, send_from_directory
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
os.makedirs('shared', exist_ok=True) # 自动创建共享文件夹
shared_data = {"text": "在这里打字，所有设备实时同步。"}

# 极简前端网页
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body style="font-family: sans-serif; padding: 20px; max-width: 600px; margin: auto;">
    <h3>局域网中转站</h3>
    
    <textarea id="log" rows="6" style="width: 100%; margin-bottom: 10px;" oninput="sendText()">{{ text }}</textarea>
    
    <hr>
    <form action="/upload" method="POST" enctype="multipart/form-data">
        <input type="file" name="file" style="margin-bottom: 10px;"><br>
        <input type="submit" value="上传文件到共享文件夹" style="padding: 10px; background: #2196F3; color: white; border: none;">
    </form>
    
    <hr>
    <h4>点击下载文件:</h4>
    {% for f in files %}
        <li><a href="/shared/{{ f }}" target="_blank">{{ f }}</a></li>
    {% endfor %}

    <script>
        var socket = io();
        // 接收到别人打字，立刻更新到自己的输入框
        socket.on('update_text', function(msg) {
            document.getElementById('log').value = msg.text;
        });
        // 自己打字时，立刻发送给服务器
        function sendText() {
            var msg = document.getElementById('log').value;
            socket.emit('client_send', {text: msg});
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    files = os.listdir('shared')
    return render_template_string(HTML, text=shared_data["text"], webFiles=files)

@socketio.on('client_send')
def handle_message(data):
    shared_data["text"] = data['text']
    # 广播给除发送者以外的所有设备
    emit('update_text', data, broadcast=True, include_self=False)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' in request.files:
        f = request.files['file']
        if f.filename:
            f.save(os.path.join('shared', f.filename))
    return "<script>alert('上传成功！'); window.location.href='/';</script>"

@app.route('/shared/<path:filename>')
def download(filename):
    return send_from_directory('shared', filename)

if __name__ == '__main__':
    print("中转站启动！手机浏览器访问: http://局域网IP:5000")
    socketio.run(app, host='0.0.0.0', port=5000)
