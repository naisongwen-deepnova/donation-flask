# -*- coding:utf-8 -*-
 
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
        # 图片名称
        img = './certificate_template.jpeg' # 图片模板
        new_img = self.no+'.png' # 生成的图片
        compress_img = 'compress.png' # 压缩后的图片
         
        # 设置字体样式 https://vimsky.com/zh-tw/examples/detail/python-method-ImageFont.truetype.html
        font_medium_type = '/System/Library/Fonts/STHeiti Medium.ttc'
        #ubuntu sudo apt-get install  ttf-wqy-zenhei ttf-wqy-microhei fonts-arphic-ukai fonts-arphic-uming  https://gist.github.com/allex/11203573
        font_medium_type='/usr/share/fonts/truetype/arphic/ukai.ttc'
        #font_type = '/System/Library/Fonts/STHeiti Light.ttc'
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
        draw.text((680,620), u'%s' % year, color,date_font)
        # 月
        month=datetime.datetime.now().strftime('%m')
        draw.text((782,620), u'%s' % month, color,date_font) 
        # 日
        day=datetime.datetime.now().strftime('%d')
        draw.text((853,620), u'%s' % day, color, date_font) 

        # 生成图片
        image.save('certificates/'+new_img, 'png')

        ''' 
        # 压缩图片
        sImg = Image.open(new_img)
        w, h = sImg.size
        width = int(w / 2)
        height = int(h / 2)
        dImg = sImg.resize((width, height), Image.ANTIALIAS)
        dImg.save(compress_img)
        '''
        return new_img

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
