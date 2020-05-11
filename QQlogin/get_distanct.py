
from PIL import Image
def is_pixel_equal(img1, img2, x, y):
    """
    判断两个像素是否相同
    :param image1: 图片1
    :param image2: 图片2
    :param x: 位置x
    :param y: 位置y
    :return: 像素是否相同
    """
    # 取两个图片的像素点
    pix1 = img1.load()[x, y]
    pix2 = img2.load()[x, y]
    threshold = 68
    if (abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(pix1[2] - pix2[2] < threshold )):
        return True
    else:
        return False
def get_gap(img1, img2):
    """
    获取缺口偏移量
    :param img1: 不带缺口图片
    :param img2: 带缺口图片
    :return:
    """
    left = 68
    for i in range(left, img1.size[0]):
        for j in range(img1.size[1]):
            if not is_pixel_equal(img1, img2, i, j):
                left = i
                print(i)
                return left
    return left

import cv2 as cv


def get_pos(image):
    blurred = cv.GaussianBlur(image, (5, 5), 0)
    canny = cv.Canny(blurred, 200, 400)
    contours, hierarchy = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for i, contour in enumerate(contours):
        M = cv.moments(contour)
        if M['m00'] == 0:
            cx = cy = 0
        else:
            cx, cy = M['m10'] / M['m00'], M['m01'] / M['m00']
        if 6000 < cv.contourArea(contour) < 8000 and 370 < cv.arcLength(contour, True) < 390:
            if cx < 400:
                continue
            x, y, w, h = cv.boundingRect(contour)  # 外接矩形
            cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv.imshow('image', image)
            return x
    return 0

def get_full_pic_new(bg_image):
    img1 = bg_image.convert("L")
    dir = ""
    threshold = 60
    for k in range(1,11):
        dir = "../assets/QQloginimgs/"+str(k)+".jpg"
        fullbg_image = Image.open(dir)
        img2 = fullbg_image.convert('L')
        pix11 = img1.load()[50, 50]
        pix12 = img1.load()[50, 250]
        pix13 = img1.load()[250, 50]
        pix14 = img1.load()[250, 250]

        pix21 = img2.load()[50, 50]
        pix22 = img2.load()[50, 250]
        pix23 = img2.load()[250, 50]
        pix24 = img2.load()[250, 250]
        if abs(pix11 - pix21)>threshold or abs(pix12 - pix22)>threshold or abs(pix13 - pix23)>threshold or abs(pix14 - pix24)>threshold:
            continue
        else:
            if abs(pix11 - pix21)<threshold and abs(pix12 - pix22)<threshold and abs(pix13 - pix23)<threshold and abs(pix14 - pix24)<threshold:
                print("Find the target:", dir)
                break
            else:
                print("Not found")
                dir = None
    return dir

def get_full_pic(bg_image):
    '''
    :param gap_pic: 缺口图片
    :return: (str)背景图片路径
    '''
    #转换图像到灰度
    img1 = bg_image.convert('L')
    distance = 68
    threshold = 60
    dir = ""
    for k in range(1,11):
        dir = "../assets/QQloginimgs/"+str(k)+".jpg"
        fullbg_image = Image.open(dir)
        img2 = fullbg_image.convert('L')
        diff = 0
        for i in range(distance, img1.size[0]):
            # 遍历像素点纵坐标
            for j in range(img1.size[1]):
                # 如果不是相同像素
                img1_pixe = img1.load()[i,j]
                img2_pixe = img2.load()[i,j]
                if abs(img1_pixe - img2_pixe) > threshold:
                    diff = diff + 1
            if diff > 6000:
                break
                # 不同的像素超过一定值直接认为不匹配，
                # 后期计算时可以优化一下结合图片验证码返回初始位置数据，
                # 比较图片时可以去图片部分区域数据
            elif i == img1.size[0]-1 and j == img1.size[1]-1:
                print("Find the target")
                return dir
    return dir
def get_distanct(bg_image):
    bg_img = Image.open(bg_image)
    full_dir = get_full_pic_new(bg_img)
    full_img = Image.open(full_dir)
    return get_gap(full_img, bg_img)
if __name__=="__main__":
    import time
    time_start = time.time()
    print("--"*20+"run"+"--"*20)
    dir = "../gap_pic/8.jpg"
    distanct = get_distanct(dir)
    time_end = time.time()
    print('totally cost', time_end - time_start)
    print(distanct)
