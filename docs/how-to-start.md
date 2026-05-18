## 第一步：启动后端
在项目根目录打开终端：
```
pip install -r requirements.txt
python main.py
```
确认后端跑起来，看到 127.0.0.1:8000 的日志。
 
## 第二步：启动前端
再开一个新终端，进入前端目录：
```
cd frontend
npm install
npm run dev
```
然后浏览器打开：
```
http://localhost:5173
```