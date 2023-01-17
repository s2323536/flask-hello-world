#from flask import Flask
#app = Flask(__name__)

#@app.route('/')
#def hello_world():
#    return 'Hello, SMITH!!!'
#---------------------------------------------------
from flask import Flask,request,render_template,jsonify,session
import pandas as pd
import googlemaps
import time

app = Flask(
    __name__,
    static_folder='static',
    static_url_path='/'
)
app.secret_key="any string but secret"
gmaps = googlemaps.Client(key='AIzaSyBFoVj6u61S3uf4uuvBIs0_9mq3wnUr8B8')
@app.route('/')
def home():
    return render_template('map.html')


@app.route('/map')
def map():
    
    city = request.args.get('cities')
    keyword = request.args.get('keyword')
    radius = request.args.get('radius')
    #################################開始在GOOGLE-MAP中搜尋######################################
    ids = []
    #擷取所需要的欄位
    myFields=['name','rating','user_ratings_total','formatted_address','international_phone_number','business_status']

    #for city in cities:
    results = []
    # Geocoding an address
    geocode_result = gmaps.geocode(city)
    loc = geocode_result[0]['geometry']['location']
    query_result = gmaps.places_nearby(keyword=keyword,location=loc, radius=radius)
    results.extend(query_result['results'])
    while query_result.get('next_page_token'):
        time.sleep(2)
        query_result = gmaps.places_nearby(page_token=query_result['next_page_token'])
        results.extend(query_result['results'])    
    resultInfo = "以"+city+"為中心半徑"+str(radius)+"公尺的"+keyword+"店家數量:"+str(len(results))+"間"
    #print("找到以"+city+"為中心半徑"+str(radius)+"公尺的"+keyword+"店家數量:"+str(len(results)))
    #print(resultInfo)
    for place in results:
        ids.append(place['place_id'])
            
    stores_info = []
    # 去除重複id
    ids = list(set(ids)) 
    for id in ids:
        stores_info.append(gmaps.place(place_id=id, fields= myFields, language='zh-TW')['result'])

#########################################對搜尋結果做處理############################################################
    #去除搜尋結果中店名有汽車玻璃的店家
    if (keyword == "玻璃"):
        stores_info2 =[]
        for i in range(0,len(results)):
            if (not("汽車" in stores_info[i]['name'])):
                stores_info2.append(stores_info[i])
                output = pd.DataFrame.from_dict(stores_info2)
    else:
        output = pd.DataFrame.from_dict(stores_info)
    
    #output.columns = ['店址', '電話','店名','評等','人氣','評等','狀態']

    #output=output[['店名','評等','人氣','電話','店址','評等','狀態']] #調整欄位順序
    
    #output.fillna(0,inplace=True)

    #output = output.sort_values(by=['人氣'], ascending=False)

#####################################################################################################      
    #output.to_csv(keyword+'.csv',index=False, encoding='utf-8-sig')  
    d1 = output.to_dict('records')
    #print(d1)
    return render_template('map.html', myResult=resultInfo, Resultlist = d1)
