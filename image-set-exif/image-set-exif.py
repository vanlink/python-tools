import os
import piexif
from datetime import datetime
from PIL import Image

ROOT = "E:\\incoming\\done1\\"

def get_photo_taken_time(file_path):
    try:
        # 读取EXIF数据
        exif_dict = piexif.load(file_path)
        
        # 检查是否存在EXIF信息
        if not exif_dict or 'Exif' not in exif_dict:
            # print("照片中未找到EXIF信息")
            return None
        
        # 检查DateTimeOriginal标签是否存在
        if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
            date_bytes = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
            date_str = date_bytes.decode('utf-8')
            
            # 将字符串转换为datetime对象
            try:
                taken_time = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                return taken_time
            except ValueError:
                print(f"无法解析日期格式: {date_str}")
                return None
        else:
            # print("照片中未找到拍摄时间信息")
            return None
            
    except Exception as e:
        print(f"读取EXIF信息时出错: {e}")
        return None

def convert_to_timestamp(time_str):
    # 定义时间格式
    format_str = "%Y-%m-%d %H:%M:%S"
    # 将字符串转换为datetime对象
    dt_obj = datetime.strptime(time_str, format_str)
    # 将datetime对象转换为时间戳（秒）
    timestamp = dt_obj.timestamp()
    return timestamp

def update_exif_datetime(path, new_dt_str):
    """
    更新 JPEG 图片的 DateTimeOriginal 和 DateTimeDigitized 字段，
    其他 EXIF 信息保持不变。

    :param path: 图片文件路径（JPEG）
    :param new_dt_str: 日期时间字符串，格式 YYYY:MM:DD HH:MM:SS
    """
    # 打开图片并读取现有 EXIF
    img = Image.open(path)
    
    exif_bytes = img.info.get("exif")
    if exif_bytes:
        exif_dict = piexif.load(exif_bytes)
    else:
        exif_dict = {"0th":{}, "Exif":{}, "GPS":{}, "Interop":{}, "1st":{}, "thumbnail":None}

    # 写入新的时间戳（需要 bytes 编码）
    dt_bytes = new_dt_str.encode('utf-8')
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = dt_bytes
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = dt_bytes
    exif_dict['0th'][piexif.ImageIFD.DateTime] = dt_bytes

    # 生成新的 EXIF 二进制数据
    exif_bytes = piexif.dump(exif_dict)

    # 插入 EXIF 而不重新压缩图像
    piexif.insert(exif_bytes, path)

for item in os.scandir(ROOT):
    if item.is_dir():
        dirname = item.name
        dirtime = dirname[0:10]
        dirtime += " 12:00:00"
        dirtime2 = dirtime.replace("-", ":")
        dirts = convert_to_timestamp(dirtime)
        # print("doing ... {} {} {}".format(dirname, dirtime, dirts))
        for root, dirname, files in os.walk(os.path.join(ROOT, item.name)):
            for f in files:
                pathall = os.path.join(root, f)
                if pathall.lower().endswith("jpg"):
                    tt = get_photo_taken_time(pathall)
                    if tt:
                        filets = convert_to_timestamp(str(tt))
                        diff = abs(int(filets) - int(dirts))
                        if diff > 24 * 3600 * 64:
                            print("{} TIME {} DIR {} DIFF {} days".format(pathall, tt, dirtime2, int(diff / 3600 / 24)))
                            # update_exif_datetime(pathall, dirtime2)
                    else:
                        print("{} TIME NOT FOUND".format(pathall))
                        # update_exif_datetime(pathall, dirtime2)
                else:
                    pass
                    # print("NOT picture {}".format(pathall))

print("--- done ---")