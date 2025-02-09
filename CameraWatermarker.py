import exifread
from PIL import Image,ImageDraw, ImageFont


def get_image_meta_info(img_file,str_map={}):

    meta_dic={}

    with open(img_file, 'rb') as img_file:

        tags = exifread.process_file(img_file)
        
        # 快门
        if 'EXIF ExposureTime' in tags:
            meta_dic['exposure_time'] = str(tags['EXIF ExposureTime'])+'S'
        else:
            meta_dic['exposure_time'] = ''
        
        # 光圈
        if 'EXIF FNumber' in tags:
            meta_dic['f_number'] = 'F'+str(tags['EXIF FNumber'])
        else:
            meta_dic['f_number'] = ''

        # ISO
        if 'EXIF ISOSpeedRatings' in tags:
            meta_dic['iso'] = 'ISO'+str(tags['EXIF ISOSpeedRatings'])
        else:
            meta_dic['iso'] = ''

        # 焦距
        if 'EXIF FocalLength' in tags:
            meta_dic['focal_length'] = str(tags['EXIF FocalLength'])+'MM'
        else:
            meta_dic['focal_length'] = ''

        # 品牌
        if 'Image Make' in tags:
            meta_dic['device_brand'] = str(tags['Image Make'])
        else:
            meta_dic['device_brand'] = ''

        # 相机型号
        if 'Image Model' in tags:
            meta_dic['device_model'] = str(tags['Image Model'])
            if meta_dic['device_model'] in str_map :
                meta_dic['device_model'] = str_map[meta_dic['device_model']]
        else:
            meta_dic['device_model'] = ''

        # 镜头型号
        if 'EXIF LensModel' in tags:
            meta_dic['lens_model'] = str(tags['EXIF LensModel'])
        else:
            meta_dic['lens_model'] = ''

        # 拍摄时间
        if 'EXIF DateTimeDigitized' in tags:
            meta_dic['date_time'] = str(tags['EXIF DateTimeDigitized'])
            meta_dic['date_time'] = meta_dic['date_time'][0:4]+ '-'+meta_dic['date_time'][5:7]+ '-'+meta_dic['date_time'][8:]
        else:
            meta_dic['date_time'] = ''
        
    return meta_dic

def camera_watermarker(img_file,output_dir='./',output_suffix='',str_map={},border=0.03):
    
    try:
        org_img=Image.open(img_file)
    except Exception as e:
        print(e)
        return
    finally:
        pass

    meta_dic=get_image_meta_info(img_file,str_map)
    print(meta_dic)
    # meta_dic['f_number']='F11'
    # meta_dic['iso'] = 'ISO12800'
    # meta_dic['focal_length']='200MM'
    # meta_dic['exposure_time']='1/4000S'

    org_img_w = org_img.size[0]
    org_img_h = org_img.size[1]
    border_w = int(org_img_w * border)
    wm_width = org_img_w # 原始宽度
    wm_heigh = int(org_img_h*0.06) # 原始照片高度的百分比
    res_img_w = wm_width + border_w*2
    res_img_h = org_img_h+wm_heigh+border_w*2 # 原始高度+水印信息高度+1倍边框高度

    # print(img.format,img.size,img.mode)

    # 水印信息绘制
    # 字体参数配置
    font_size_1 = 120
    font_size_2 = 80
    font1 = ImageFont.truetype("./src/方正黑体_GBK.TTF", font_size_1)
    font2 = ImageFont.truetype("./src/方正黑体_GBK.TTF", font_size_2)
    color1=(0,0,0)
    color2=(150,150,150)
    color3=(200,200,200)

    # 左侧水印信息绘制
    left_wm_img_w = 800
    left_wm_img_h = 250
    left_wm_img=Image.new(org_img.mode,(left_wm_img_w,left_wm_img_h),'white')
    left_wm_img_draw = ImageDraw.Draw(left_wm_img)

     # 设备型号
    device_model_x = 20
    device_model_y = 20
    device_model_w,device_model_h = left_wm_img_draw.textsize(meta_dic['device_model'],font1) 

    # 镜头型号
    lens_model_x = device_model_x
    lens_model_y = device_model_y+130
    lens_model_w,lens_model_h = left_wm_img_draw.textsize(meta_dic['lens_model'],font2) 

    left_wm_img_w = 40 + (device_model_w if device_model_w>lens_model_w else lens_model_w)
    left_wm_img=left_wm_img.resize((left_wm_img_w,left_wm_img_h))
    left_wm_img_draw = ImageDraw.Draw(left_wm_img)

    left_wm_img_draw.text((device_model_x, device_model_y), meta_dic['device_model'], font=font1,stroke_width=1, fill=color1)
    left_wm_img_draw.text((lens_model_x, lens_model_y), meta_dic['lens_model'], font=font2,stroke_width=1, fill=color2)

    # left_wm_img.show()

    # 右侧水印信息绘制
    right_wm_img_w = 2600
    right_wm_img_h = 250
    right_wm_img=Image.new(org_img.mode,(right_wm_img_w,right_wm_img_h),'white')
    right_wm_img_draw = ImageDraw.Draw(right_wm_img)

    # 绘制水印 logo
    img_sony_logo = Image.open('./src/sony_logo.jpg')
    img_sony_logo_h = right_wm_img_h - 40
    img_sony_logo_w = int(img_sony_logo.size[0] * img_sony_logo_h / img_sony_logo.size[1])
    img_sony_logo_x = 20
    img_sony_logo_y = 20
    img_sony_logo = img_sony_logo.resize((img_sony_logo_w,img_sony_logo_h))

    # 绘制分割线
    split_line_x= img_sony_logo_w+int(left_wm_img_h*0.2)
    split_line_y= 20
    split_line_w= int(right_wm_img_h*0.02)
    split_line_h= int(right_wm_img_h*0.8)

    # 拍摄参数
    img_exposure_value_text = meta_dic['focal_length']+' '+meta_dic['f_number']+' '+meta_dic['exposure_time']+' '+meta_dic['iso']
    img_exposure_value_x = split_line_x + int(left_wm_img_h*0.2)
    img_exposure_value_y = device_model_y
    img_exposure_value_w , img_exposure_value_h = right_wm_img_draw.textsize(img_exposure_value_text,font1)

    # 拍摄日期
    date_time_x = img_exposure_value_x
    date_time_y = lens_model_y
    date_time_w , date_time_h = right_wm_img_draw.textsize(meta_dic['date_time'],font2)

    right_wm_img_w = 40 + img_sony_logo_w + split_line_w + int(left_wm_img_h*0.4) + (img_exposure_value_w if img_exposure_value_w>date_time_w else date_time_w)
    right_wm_img=right_wm_img.resize((right_wm_img_w,right_wm_img_h))
    right_wm_img_draw = ImageDraw.Draw(right_wm_img)
    
    right_wm_img.paste(img_sony_logo,(img_sony_logo_x,img_sony_logo_y))   
    right_wm_img_draw.rectangle((split_line_x,split_line_y,split_line_x+split_line_w,split_line_y+split_line_h),fill=color3)
    right_wm_img_draw.text((img_exposure_value_x, img_exposure_value_y), img_exposure_value_text, font=font1,stroke_width=1, fill=color1)
    right_wm_img_draw.text((date_time_x, date_time_y), meta_dic['date_time'], font=font2,stroke_width=1, fill=color2)

    # right_wm_img.show()

    # 合并左右水印
    left_wm_img_w = int(left_wm_img_w*wm_heigh/left_wm_img_h)
    left_wm_img_h = wm_heigh
    left_wm_img=left_wm_img.resize((left_wm_img_w,left_wm_img_h))
    right_wm_img_w = int(right_wm_img_w*wm_heigh/right_wm_img_h)
    right_wm_img_h = wm_heigh
    right_wm_img=right_wm_img.resize((right_wm_img_w,right_wm_img_h))

    mrg_wm_img_w = int((left_wm_img.size[0] + right_wm_img.size[0]) * 1.2)
    mrg_wm_img = None
    if mrg_wm_img_w > wm_width :
        mrg_wm_img = Image.new(org_img.mode,(mrg_wm_img_w,wm_heigh),'white')
        mrg_wm_img.paste(left_wm_img,(0,0))
        mrg_wm_img.paste(right_wm_img,(mrg_wm_img_w - right_wm_img_w,0))
        mrg_wm_img=mrg_wm_img.resize((wm_width,int(mrg_wm_img.size[1] * wm_width/mrg_wm_img.size[0])))
    else :
        mrg_wm_img = Image.new(org_img.mode,(wm_width,wm_heigh),'white')
        mrg_wm_img.paste(left_wm_img,(0,0))
        mrg_wm_img.paste(right_wm_img,(wm_width-right_wm_img_w,0))

    # mrg_wm_img.show()

    # 绘制输出图片
    res_img_h = border_w * 2 + org_img_h + mrg_wm_img.size[1]
    res_img=Image.new(org_img.mode,(res_img_w,res_img_h),'white')
    res_img.paste(org_img,(border_w,border_w))
    res_img.paste(mrg_wm_img,(border_w, int(border_w * 1.5 + org_img_h)))
    res_img.show()

    # 处理输出图片文件名和路径
    input_file_name = '.'.join(img_file.split('/')[-1].split('.')[0:-1])
    input_file_type = img_file.split('/')[-1].split('.')[-1]
    output_file_name = input_file_name+output_suffix+'.'+input_file_type
    output_file_path = output_dir+output_file_name
    # print(output_file_path)

    # 保存图片
    res_img.save(output_file_path)

if __name__ == '__main__':  

    img_file='./img/demo.jpg' # 原始图片

    # 字符串映射
    str_map = {'ILCE-7CM2':'A7C2'} # 将扩展信息中解析出的原始文本映射成你想要的数值

    camera_watermarker(img_file,
                       output_dir='./img/', # 输出文件夹
                       output_suffix='_wm', # 输出文件名后缀 demo.jpg -> demo_wm.jpg
                       str_map=str_map,
                       border=0.03 # 边框宽度比率
                       )