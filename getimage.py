#coding:utf-8
import urllib2
import os
import re
import urllib
import random
import socket  
import time
import sys
#import HTMLParser
import glob
from reportlab.pdfgen import canvas
import Image
import shutil
import thread


First_year = 2015
Last_year = 2015
socket.setdefaulttimeout(3)
CurrentPath = os.getcwd()
global DocumentPath
DocumentPath = CurrentPath + '\\temp'
SublistPath = DocumentPath +'\\List.txt'
ErrorLogPath = DocumentPath + '\\Error.txt'
Image_DocumentPath = DocumentPath +'\\image'
Pdf_DocumentPath = DocumentPath + '\\pdf'
ROOT = 'http://www.nongji360.com'


def Error_output(log):
  try:
    error_log = open(ErrorLogPath,'a')
    print >> error_log, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " " + log
    error_log.close()
  except:
    pass

def Remove_files(file_path):
  try:
    shutil.rmtree(file_path)
  except:  
    Error_output(file_path + ' deleted Error')
    pass


def Muti_try_image(url, file, volume, page, sleep_times, total_try_times):
  global try_times
  try:
    time.sleep(sleep_times)
    connection = urllib2.urlopen(url)
    file.write(connection.read())
    connection.close()
  except:
    try_times += 1
    total_try_times -= 1
    if total_try_times > 0:
      sleep_times += 1
      Muti_try_image(url, file, volume, page, sleep_times, total_try_times)
    else:
      pass


def Muti_try_year_or_vol(url, year_or_vol, sleep_times, total_try_times):
    global try_times
    try:
     time.sleep(sleep_times)
     global year_or_vol_page_read
     year_or_vol_page_req = urllib2.Request(url)
     year_or_vol_page_res = urllib2.urlopen(year_or_vol_page_req)
     year_or_vol_page_read = year_or_vol_page_res.read()
     year_or_vol_page_res.close()
    except:
     try_times += 1
     total_try_times -= 1
     if total_try_times > 0:
       sleep_times += 1
       Muti_try_year_or_vol(url, year_or_vol, sleep_times, total_try_times)
     else:
       pass
    return year_or_vol_page_read

def GetPicInfo(img_file):
    try:    
        image_file = Image.open(img_file)
        return image_file.size[0], image_file.size[1]
    except:
        pass

#def Add_acount(c):
#  global c, lock
#  lock.acquire()
#  c = c + 1
 # lock.release()
#  return c

#def Down_image(link, pathname):

    



#lock = thread.allocate_lock()

try:
  os.makedirs(DocumentPath)
  os.makedirs(Image_DocumentPath)
  os.makedirs(Pdf_DocumentPath)
except:
  pass

for year in range(First_year,Last_year + 1):
  year_page_url = 'http://www.nongji360.com/e-book/?sy=' + bytes(year)
  try_times = 0
  year_page_content = Muti_try_year_or_vol(year_page_url, year, 0, 20 )
  if try_times > 0:
     print(bytes(year) + 'year error' + bytes(try_times))
     Error_output('第' + bytes(year) +'年:下载出错' + bytes(try_times) +'次 ' + year_page_url)
  volume_list_temp = re.findall(r"ebooktime=\d*",year_page_content)
  volume_list = volume_list_temp[::2]
  volume_list.sort()
  for volume in volume_list:
     volume_name = volume.lstrip('ebooktime=')
     try_times = 0
     volume_page_content = Muti_try_year_or_vol('http://www.nongji360.com/e-book/view.asp?' + volume, volume_name, 0, 20)
     if try_times > 0:
       print(bytes(volume_name) + 'vol error' + bytes(try_times))
       Error_output('第' + bytes(volume_name) +'期:下载出错' + bytes(try_times) +'次 ' + 'http://www.nongji360.com/e-book/view.asp?' + volume)
     image_url = re.findall(r"img='/pics/ebook/magazine\d/\d*.jpg|img='/pics/ebook/magazine\d/\d*/\w*\d*.jpg",volume_page_content)
     image_title = re.findall(r"infoTitle='\S*",volume_page_content)
     s = 1
     try: 
       os.makedirs(Image_DocumentPath + '\\'+ volume_name)
     except:         
       pass
     title_file = open (SublistPath,'a')
     for title in image_title:
         title = title.strip('\'')
         print >> title_file, volume_name +' ' + bytes(s) + ' ' + title.lstrip('infoTitle=\'')
         s+=1
     title_file.close()
     s = 1
     for image in image_url:
         image = image.lstrip("img=\'")
         image_file = open(Image_DocumentPath + '\\' + volume_name +'\\' + bytes(s) + '.jpg','wb')
         try_times = 0
         Muti_try_image(ROOT + image, image_file, volume_name, s, 0, 20)
         if try_times > 0:
             print(volume_name + 'Page'+bytes(s)+'error' + bytes(try_times))
             Error_output('第' + volume_name +'期 第'+bytes(s)+'页:下载出错' + bytes(try_times) +'次 ' + ROOT + image) 
         image_file.close()
         print(volume_name+'_' + bytes(s) + '.jpg')
         s+=1
     print('Convert to pdf')
     os.chdir(Image_DocumentPath + '\\' + volume_name + '\\')
     img_list = glob.glob('*.jpg')
     img_list.sort(key=lambda x:int(x[:-4]))
     pdf_file = canvas.Canvas(Pdf_DocumentPath + '\\' + volume_name+'.pdf', pagesize = (840, 1132))
     for img_file in img_list:
       try:
     	     x,y = GetPicInfo(img_file)
     	     if int(x) * int(y) / 840 > 1132:
     	 	     pdf_file.drawImage(img_file, 0, 0, 840, 1132)
     	 	     pdf_file.showPage()
     	     else:
     	 	     pdf_file.drawImage(img_file, 0, 0, 840)
     	 	     pdf_file.showPage()
     	 	except:
     	 	  pass
     pdf_file.save()
     os.chdir(CurrentPath + '\\')
     print('Convert to pdf finished!')
     Remove_files(Image_DocumentPath + '\\'+ volume_name)
Remove_files(Image_DocumentPath)



