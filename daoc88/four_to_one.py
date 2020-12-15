from PIL import Image


def join(page_count):
    result = 'images/{}.gif'
    print("正在拼接碎片...")
    for i in range(1, page_count + 1):
        img1, img2, img3, img4 = Image.open("images2/{}_00.gif".format(i)), Image.open("images2/{}_01.gif".format(i)), \
                                 Image.open("images2/{}_10.gif".format(i)), Image.open("images2/{}_11.gif".format(i)),
        size1, size2, size3, size4 = img1.size, img2.size, img3.size, img4.size
        joint = Image.new('RGB', (size1[0] * 2, size1[1] * 2))
        loc1, loc2, loc3, loc4 = (0, 0), (size1[0], 0), (0, size1[1]), (size1[0], size1[1])
        joint.paste(img1, loc1)
        joint.paste(img2, loc2)
        joint.paste(img3, loc3)
        joint.paste(img4, loc4)
        joint.save(result.format(i))
    print("拼接完成！")

if __name__=="__main__":
    join(int(input("请输入页码数")))