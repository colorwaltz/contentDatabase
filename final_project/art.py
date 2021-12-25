import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import firestore


import PySimpleGUI as psg
import io
import os
from PIL import Image
import requests
import time 


psg.theme('DarkPurple1')



cred = credentials.Certificate('./colorwaltzdb.json')
firebase_admin.initialize_app(cred,{'storageBucket':'colorwaltzdb.appspot.com','projectId':'colorwaltzdb',})

db = firestore.client()

#image file
file_types = [("JPEG(*.jpg)","*.jpg"),("PNG(*.png)","*.png"),("All files(*.*)","*,*")]


#pysimple
data = []
index = ['작가명','<작품명>','제작연도']
myselect = ['전체','작가명','작품명','제작연도']

mylayout = [[psg.Text("미술 작품 데이터 베이스", expand_x = True, font='any 20 bold', justification="center", pad=((0,0),(50,50)))], 
[psg.Button("시작하기",key = "start",expand_x=True,pad=((100,100),(0,0)) )]]

start_win = psg.Window("시작 페이지", mylayout, size =(600,200))


# 작품 추가창 구현 
def add_win():
     left_layout = [[psg.Image(key="IMAGE",size = (150,150), background_color="grey")],
     [psg.FileBrowse(button_text="Open", file_types=file_types),
     psg.Button("Load Image",expand_x=True)]]

     right_layout = [[psg.Text("작가명    "),psg.In(key ="name_input", expand_x = True)],
     [psg.Text("<작품명>"),psg.In(key ="title_input", expand_x = True)],
     [psg.Text("제작연도 "),psg.In(key ="year_input", expand_x = True)],
     [psg.Text("재료       "),psg.In(key ="material_input", expand_x = True)],
     [psg.Text("크기       "),psg.In(key ="size_input", expand_x = True)]]

     add_layout = [[psg.Column(left_layout),psg.Column(right_layout)],
     [psg.Multiline('작품 설명란',key = "description_input",expand_x = True, expand_y=True)],
     [psg.Button("추가하기",key = "add_ok",expand_x=True)]]

     add_w = psg.Window("미술 작품 추가", add_layout, size = (500,400))
     
     while True:
          e,v = add_w.read()
          if e == psg.WIN_CLOSED:
               break
               
          elif e == "Load Image":
               filename = v["Open"]
               if os.path.exists(filename):
                    image = Image.open(filename)
                    image.thumbnail((150,150))
                    bio = io.BytesIO()
                    image.save(bio, format = "PNG")
                    add_w["IMAGE"].update(data = bio.getvalue())
          elif e == "add_ok":
               bucket = storage.bucket()
               filetype = os.path.splitext(v['Open'])
               now = time.localtime()
               filename = str(now.tm_year)+"_"+str(now.tm_mon)+"_"+str(now.tm_mday)+"_"+str(now.tm_hour)+"_"+str(now.tm_min)+"_"+str(now.tm_sec)+filetype[1]

               blob = bucket.blob(filename)
               blob.upload_from_filename(v['Open'])
               blob.make_public()

               db.collection('artdb').add({
                    'name': v["name_input"],
                    'title': v["title_input"],
                    'year': v["year_input"],
                    'material': v["material_input"],
                    'size': v["size_input"],
                    'description' : v["description_input"],
                    'thumb' : blob.public_url
               })
               break
     add_w.close()





# 작품 선택하고 클릭하면 뜨는 옵션 선택창 // 정보 확인과 정보 삭제 가능 
def Option(name,title):
     option_layout = [[psg.Button("작품 정보 확인", key = "info", expand_x=True, expand_y= True, button_color= '#ff66ff')],
                    [psg.Button("작품 정보 수정", key = "modi", expand_x=True, expand_y= True, button_color= '#ff33ff')],
                    [psg.Button("작품 정보 삭제", key = "del", expand_x=True, expand_y= True, button_color= '#cc00cc')],
                    [psg.Button("창 닫기", key = "close_option", expand_x=True, expand_y= True, button_color= '#990099')]]

     option_w = psg.Window("옵션선택", option_layout, size = (400,150))

     while True:
          e,v = option_w.read()
          if e == psg.WIN_CLOSED:
               break
          elif e == "info":
               Viewer_info(name,title) #break 까먹은거 아님! 의도적으로 안걸어둔거임
          elif e == 'del':
               search = db.collection('artdb').where('name', '==', name).where('title', '==', title).get()
               for i in search:
                    db.collection('artdb').document(i.id).delete()
               break
          elif e == 'modi':
               Viewer_modi(name,title)  #break 까먹은거 아님! 의도적으로 안걸어둔거임
          elif e == 'close_option':
               break
     option_w.close()




# 작품선택창 -> 작품 정보 보는 창 구현 
def Viewer_info(name,title):
     search = db.collection('artdb').where('name', '==', name).where('title', '==', title).get()
     for i in search:
          imageurl = i.to_dict()['thumb']
          year = i.to_dict()['year']
          material = i.to_dict()['material']
          size = i.to_dict()['size']
          description = i.to_dict()['description']
          
     res = requests.get(imageurl)
     request_get_img = Image.open(io.BytesIO(res.content))
     bio = io.BytesIO()
     request_get_img.save(bio, format="PNG")
     

     left_layout = [[psg.Image(key="IMAGE",size = (150,180), background_color="grey", data = bio.getvalue())]]

     right_layout = [[psg.Text("작가명    "),psg.Text(name, expand_x = True)],
     [psg.Text("<작품명>"),psg.Text(title, expand_x = True)],
     [psg.Text("제작연도 "),psg.Text(year, expand_x = True)],
     [psg.Text("재료       "),psg.Text(material, expand_x = True)],
     [psg.Text("크기       "),psg.Text(size, expand_x = True)]]

     view_layout = [[psg.Column(left_layout),psg.Column(right_layout)],
     [psg.Multiline(description, key = "description_input",expand_x = True, expand_y=True, disabled=True)],
     [psg.Button("닫기",key = "close_btn",expand_x=True)]]

     view_w = psg.Window("작품 정보 확인", view_layout, size = (500,400))

     while True:
          e,v = view_w.read()
          if e == psg.WIN_CLOSED:
               break
          elif e == 'close_btn':
               break
     view_w.close()


# 작품선택창 -> 작품 정보 수정하는 창 구현 
def Viewer_modi(name,title):
     search = db.collection('artdb').where('name', '==', name).where('title', '==', title).get()
     for i in search:
          imageurl = i.to_dict()['thumb']
          year = i.to_dict()['year']
          material = i.to_dict()['material']
          size = i.to_dict()['size']
          description = i.to_dict()['description']

     change_image = False
          
     res = requests.get(imageurl)
     request_get_img = Image.open(io.BytesIO(res.content))
     bio = io.BytesIO()
     request_get_img.save(bio, format="PNG")

     left_layout = [[psg.Image(key="IMAGE",size = (150,150), background_color="grey", data = bio.getvalue())],
     [psg.FileBrowse(button_text="Open", file_types=file_types),
     psg.Button("Load Image",expand_x=True)]]

     right_layout = [[psg.Text("작가명    "),psg.In(name, key ="name_input", expand_x = True)],
     [psg.Text("<작품명>"),psg.In(title, key ="title_input", expand_x = True)],
     [psg.Text("제작연도 "),psg.In(year, key ="year_input", expand_x = True)],
     [psg.Text("재료       "),psg.In(material, key ="material_input", expand_x = True)],
     [psg.Text("크기       "),psg.In(size, key ="size_input", expand_x = True)]]

     modi_layout = [[psg.Column(left_layout),psg.Column(right_layout)],
     [psg.Multiline(description,key = "description_input",expand_x = True, expand_y=True)],
     [psg.Button("수정 완료",key = "modi_ok",expand_x=True)]]

     modi_w = psg.Window("작품 정보 수정", modi_layout, size = (500,400))
  

     while True:
          e,v = modi_w.read()
          if e == psg.WIN_CLOSED:
               break
          elif e == "Load Image":
               filename = v["Open"]
               if os.path.exists(filename):
                    image = Image.open(filename)
                    image.thumbnail((150,150))
                    bio = io.BytesIO()
                    image.save(bio, format = "PNG")
                    modi_w["IMAGE"].update(data = bio.getvalue())
                    change_image = True
          elif e == "modi_ok":
               if change_image == True :
                    bucket = storage.bucket()
                    filetype = os.path.splitext(v['Open'])
                    now = time.localtime()
                    filename = str(now.tm_year)+"_"+str(now.tm_mon)+"_"+str(now.tm_mday)+"_"+str(now.tm_hour)+"_"+str(now.tm_min)+"_"+str(now.tm_sec)+filetype[1]

                    blob = bucket.blob(filename)
                    blob.upload_from_filename(v['Open'])
                    blob.make_public()

                    search = db.collection('artdb').where('name', '==', name).where('title', '==', title).get()
                    for i in search:
                         db.collection('artdb').document(i.id).update({
                              'name': v["name_input"],
                              'title': v["title_input"],
                              'year': v["year_input"],
                              'material': v["material_input"],
                              'size': v["size_input"],
                              'description' : v["description_input"],
                              'thumb' : blob.public_url
                         })
               elif change_image == False:
                    search = db.collection('artdb').where('name', '==', name).where('title', '==', title).get()
                    for i in search:
                         db.collection('artdb').document(i.id).update({
                              'name': v["name_input"],
                              'title': v["title_input"],
                              'year': v["year_input"],
                              'material': v["material_input"],
                              'size': v["size_input"],
                              'description' : v["description_input"]
                         })    
               break
     modi_w.close()   


def Main():
     mylayout = [[psg.Combo(values=myselect, key="select_combo", size=(10, 1), default_value='전체'), psg.In(key="inputdata", expand_x=True), psg.Button("검색", key="search"),psg.Button("작품추가", key="add")], 
     [psg.Table(values=data, headings=index, key="myresult", expand_x=True, expand_y = True,header_text_color = '#17277C', auto_size_columns=False, justification="center", enable_events=True)]]

     win = psg.Window("메인 페이지", mylayout, size =(600,400))
     while True:
          e,v = win.read()
          if e == psg.WIN_CLOSED:
               break
          elif e == 'add': 
               win.alpha_channel=0
               add_win()
               win.alpha_channel=1
               data.clear()
               search = db.collection('artdb').get()
               for i in search:
                    data.append([i.to_dict()['name'],i.to_dict()['title'],i.to_dict()['year']])
               win['myresult'].update(values=data)

          # 검색 기능 구현 코드      
          elif e == 'search':
               data.clear()
               if v['select_combo'] == '전체':
                    search = db.collection('artdb').get()
                    for i in search:
                         data.append([i.to_dict()['name'],i.to_dict()['title'],i.to_dict()['year']])
               elif v['select_combo'] == '작가명':
                    search = db.collection('artdb').where('name','==',v['inputdata']).get()
                    for i in search:
                         data.append([i.to_dict()['name'],i.to_dict()['title'],i.to_dict()['year']])          
               elif v['select_combo'] == '작품명':
                    search = db.collection('artdb').where('title','==',v['inputdata']).get()
                    for i in search:
                         data.append([i.to_dict()['name'],i.to_dict()['title'],i.to_dict()['year']])
               elif v['select_combo'] == '제작연도':
                    search = db.collection('artdb').where('year','==',v['inputdata']).get()
                    for i in search:
                         data.append([i.to_dict()['name'],i.to_dict()['title'],i.to_dict()['year']])
               win['myresult'].update(values=data)

          # 작품 클릭시 옵션 선택 창 호출     
          elif e == 'myresult': 
               if len(v['myresult']) != 0:
                    name = data[v['myresult'][0]][0]
                    title = data[v['myresult'][0]][1]
                    win.alpha_channel = 0
                    Option(name,title)
                    win.alpha_channel = 1
                    data.clear()
                    search = db.collection('artdb').get()
                    for i in search:
                         data.append([i.to_dict()['name'],i.to_dict()['title'],i.to_dict()['year']])
                    win['myresult'].update(values=data)
     win.close()


while True:
     e,v = start_win.read()
     if e == psg.WIN_CLOSED:
          break
     elif e == "start":
          start_win.alpha_channel = 0
          Main()
          break
     start_win.close()
