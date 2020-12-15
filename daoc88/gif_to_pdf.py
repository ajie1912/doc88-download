from PIL import Image
import os
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def rea(pdf_name):
    file_list = os.listdir('images/')
    pic_name = []
    im_list = []
    for x in file_list:
        if "gif" in x:
            pic_name.append("images/" + x)
    pic_name.sort()
    im1 = Image.open(pic_name[0])
    pic_name.pop(0)
    for i in pic_name:
        img = Image.open(i)
        if img.mode == "RGBA":
            img = img.convert('RGB')
            im_list.append(img)
        else:
            im_list.append(img)
    if not os.path.exists('pdf/'):
        os.mkdir("pdf/")
    else:
        if os.path.exists("pdf/" + pdf_name):
            os.remove("pdf/" + pdf_name)
    im1.save("pdf/" + pdf_name, "PDF", resolution=100.0, save_all=True, append_images=im_list)
    print("输出文件名称：", pdf_name)


def save_to_pdf(pdf_name):
    if ".pdf" in pdf_name:
        rea(pdf_name=pdf_name)
    else:
        rea(pdf_name="{}.pdf".format(pdf_name))
    print("转化pdf已完成！")


if __name__=="__main__":
    save_to_pdf(input("输入pdf名："))