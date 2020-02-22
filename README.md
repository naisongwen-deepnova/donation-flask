主要交互功能：
1. 输入捐款人信息 列出查询结果列表；
2. 输入过程中前端显示联想提示词，选择联想词后自动查询结果；
3. 从查询结果中查看证书

前端UI实现

前端展示框架，我们引用jQuery和Bootstrap，详情参见：https://getbootstrap.com/docs/4.4/getting-started/introduction/#starter-template
```
<body>
        <main>
            <section class="jumbotron text-center not-search">
                <div class="container">
                    <h1 class="jumbotron-heading">华中科技大学浙江校友会援助武汉捐款人信息查询</h1>
                    <!-- 在这里下面添加搜索框 -->
                    <div class="input-group mt-5 mb-3 position-relative">
                        <input type="text" id="keyword" class="form-control keyword-input" placeholder="捐款人姓名" autocomplete="off" aria-describedby="button-addon2" />
                        <div class="input-group-append">
                        <button id="searchDonation" class="btn btn-outline-secondary px-4" type="button">查询</button>
                    </div>
                    <!-- 这里下面放联想提示框 -->
                   <div id="suggestList" class="list-group position-absolute">
                    <!-- 每一条结果将会用jQuery插入到这里 -->
                    </div>
                </div>
            </section>
            <div id="resultSection" class="py-5 bg-light">
                <div class="container">
                    <div class="row" id="result">
                        <!-- 每一条结果将会用jQuery插入到这里 -->
                    </div>
                </div>
            </div>
       </main>
  </body>
</html>
```
在查询主页面的交互过程主要有2个：输入关键词的联想互动和查询提交和结果返回。这个通过jQuery实现，总体处理框架为：
```
$(document).ready(function() {
    // 页面刚开始隐藏搜索结果的部分
    $("#resultSection").hide();

    // id为searchDonation的按钮按下触发searchDonation()方法
    $("#searchDonation").click(function() {
        keyword = $("#keyword").val();
        searchDonation(keyword);
    });

    // id为keyword的输入框内容改变触发getSuggest()方法
    $("#keyword").on("input propertychange", function() {
        getSuggest();
    });
});

function searchDonation(key) {
    // 首先清空result中的内容以便内容填入
    $("#result").empty();
    $.getJSON({
        url: "/donation/search?key=" + key,
        success: function(result) {
        // 搜索完以后让搜索框移上去，带有动画效果
       $("section.jumbotron").animate({
             margin: "0"
       });
       // 显示搜索结果的部分
             $("#resultSection").show();
             // 清空输入联想
             $("#suggestList").empty();
}
   })
}

function getSuggest() {
    // 首先清空suggestList中原来的内容以便内容填入
    $("#suggestList").empty();
    // 向服务器请求联想词
    $.getJSON({
        url: "/donation/suggest?key=" + $("#keyword").val(),
        success: function(result) {

        }
    });
}
```
数据存储实现

所需要的信息有：捐款序号（自增ID）、捐款人姓名、捐款人金额、备注和经办人。
1. 通过sqlite3 控制台使用：

//直接输入数据库文件名，如果没有则创建。
>>sqlite3 dontion.db
//查看sqlite支持的命令
sqlite> .help
//查看当前数据库
sqlite> .databases
//查看表schema
sqlite> .schema donation_info
CREATE TABLE donation_info(id INTEGER PRIMARY KEY AUTOINCREMENT,name varchar(100) not null,amount double not null,remark varchar(200),operator varchar(20));
//导入csv格式数据，先设置csv分隔符
sqlite>.separator ","
sqlite> .import '/Users/naisongwen/武汉捐款详情.csv' donation_info
//查询表数据
sqlite> select * from donation_info limit 10;

2. 通过SQLAlchemy 使用
SQLAlchemy 的使用详情参见：https://docs.sqlalchemy.org/en/13/orm/tutorial.html#creating-a-session

#实现sqlite_helper.py
```
import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db='donation.db'

engine = create_engine('sqlite:///'+db,convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

#表存储模型设计 donor.py
from sqlite_helper import Base
from sqlalchemy import Column, String, Integer,Float

class Donor(Base):
    __tablename__ = 'donation_info'

    id = Column(Integer,autoincrement=True,primary_key=True)
    name =Column(String(80),nullable=False)
    amount =Column(Float,nullable=False)
    remark =Column(String(80),nullable=True)
    operator =Column(String(240), unique=False)

    def __init__(self, name=None, amount=None,remark=None,operator=None):
        self.name = name
        self.amount=amount
        self.remark=remark
        self.operator=operator
```
有关模型的读取参见下文服务端请求的实现部分。

后端服务请求实现
```
app = Flask(__name__,template_folder='templates',static_folder='static',static_url_path='')
app.config.from_object(Config)

@app.route('/donation/index')
def index():
    return render_template('search.html')

@app.route('/donation/search',methods=['GET','POST'])
def search():
    key = request.args.get('key')
    donors=Donor.query.filter(Donor.name.like("%" + key + "%") if key is not None else "").all()
    dcs=[donor2dict(donor) for donor in donors]
    return make_response({'items':dcs})


@app.route('/donation/suggest',methods=['GET','POST'])
def suggest():
    key = request.args.get('key')
    donors=Donor.query.filter(Donor.name.like("%" + key + "%") if key is not None else "").all()
    names=[donor.name for donor in donors]
    return make_response({'suggestions':names})
```
证书颁发

证书模板上面需要填充的内容有：捐款人姓名、捐款金额、证书编号和颁发年月日信息，这里使用Pillow库进行图片文字的绘制，具体实现参考如下代码：
```
from PIL import Image, ImageDraw, ImageFont
import time
import sys
import datetime

class Certificate:

    def __init__(self,name,amount,no):
        self.name=name
        self.amount=amount
        self.no=no

    def grant(self):
        # 安装库：pip install Pillow
        img = './certificate_template.jpeg' # 图片模板
        new_img = self.no+'.png' # 生成的图片

        # 设置字体样式 https://vimsky.com/zh-tw/examples/detail/python-method-ImageFont.truetype.html
        font_medium_type = '/System/Library/Fonts/STHeiti Medium.ttc' # for mac os
        #ubuntu sudo apt-get install  ttf-wqy-zenhei ttf-wqy-microhei fonts-arphic-ukai fonts-arphic-uming  https://gist.github.com/allex/11203573
        font_medium_type='/usr/share/fonts/truetype/arphic/ukai.ttc' #for ubuntu os
        font_type = font_medium_type
        name_font = ImageFont.truetype(font_medium_type,30,encoding="unic")
        color = "#000000"

        # 打开图片
        image = Image.open(img)
        draw = ImageDraw.Draw(image)
        width, height = image.size

        # name姓名
        name_x = 603
        name_y = 240
        print(self.name)
        draw.text((name_x,name_y),u'%s' %self.name, color,name_font)

        # no.编号
        no_x = 243
        no_y = 600
        no_font = ImageFont.truetype(font_medium_type,25)
        draw.text((no_x,no_y), u'%s' % self.no, color, no_font)

        # 金额
        amount_font = ImageFont.truetype(font_medium_type,25)
        draw.text((792,385), u'%s' %self.amount, color,amount_font)

        date_font = ImageFont.truetype(font_type,25)
        # 年
        year=datetime.datetime.now().strftime('%Y')
        draw.text((647,585), u'%s' % year, color,date_font)
        # 月
        month=datetime.datetime.now().strftime('%m')
        draw.text((752,585), u'%s' % month, color,date_font)
        # 日
         day=datetime.datetime.now().strftime('%d')
        draw.text((823,585), u'%s' % day, color, date_font)

        # 生成图片
        image.save('certificates/'+new_img, 'png')

if __name__ == '__main__':
    if len(sys.argv) <2:
        print('illegal params')
        exit(0)
    #捐款人姓名
    name=sys.argv[1]
    #捐款金额
    amount=sys.argv[2]
    #证书编号
    no='20200128000838'
    #no=sys.argv[3]

    cert=Certificate(name,amount,no)
    cert.grant()
```
系统部署
部署通过nginx反向代理到本机 8080端口，本机应用启动命令：
gunicorn -b 0.0.0.0:8080 donation:app

niginx反向代理配置为：
#/etc/nginx/sites-enabled/proxy.conf
```
upstream local {
        server 172.31.8.106:8080 weight=2 max_fails=2 fail_timeout=2;
}

server {
        listen 80;
        listen 443 ;
        server_name localhost;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        set_real_ip_from 172.16.0.0/12;
        real_ip_header    X-Forwarded-For;
        real_ip_recursive on;

        location / {
                autoindex on;
#                auth_basic "Input your username and password !!";
#                auth_basic_user_file /etc/nginx/.htpasswd;
                proxy_pass http://local;
         }
```
