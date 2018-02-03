from flaskexample import app # init file

import pandas as pd
import numpy as np
from flask import render_template, jsonify, request
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
# from xgboost import XGBClassifier
# from sqlalchemy import create_engine
# from sqlalchemy_utils import database_exists, create_database
from datetime import datetime, timedelta
import json
import pickle
import os
import googlemaps

gmaps=googlemaps.Client(key="AIzaSyDI1tQyI4NkA-8AD9idSOGjIokrU2bbtxc")

##@app.route('/sheila')
##def index():
##	return render_template('master.html')

@app.route('/slides')
def slides():
        return render_template('slides.html')

@app.route('/__background_process')
def background_process():

    # calculates the probabilities and reports back to python
    # can calculate waiting times as well
    
    try:
        # get the user input coordinates from Python
        toPython=request.args.get('toPython')
        
        # parse the string to get the start and end points
        regexand=toPython.find("AANNDD")
        pointA=toPython[0:regexand]
        pointB=toPython[regexand+6:]

        # only run the code if user has input two valid places
        if (pointA != "null" and pointB != "null"):
                # print("LOADING STATIONS")
                # loading station data
                # print(os.getcwd()+"/data/STATIONS.snek")
                # stations=pickle.load(open("data/STATIONS.snek",'rb'))
                stations = joblib.load("data/STATIONS.snek")
                # print("LOADED STATIONS")
                # converting user entry into coordinates
                geocode_pointA=gmaps.geocode(pointA)
                geocode_pointB=gmaps.geocode(pointB)
                coordA=geocode_pointA[0]['geometry']['location']
                coordB=geocode_pointB[0]['geometry']['location']

                # find two nearest stations
                nodes=np.asarray(stations[['Latitude','Longitude']])
                distA=np.sum((nodes-np.array([coordA['lat'],coordA['lng']]))**2,axis=1)
                distB=np.sum((nodes-np.array([coordB['lat'],coordB['lng']]))**2,axis=1)
                # print(np.argmin(distA))
                # print(distA.argsort()[:3])
                # print(stations.iloc[distA.argsort()[:3]])
                Astations = stations.iloc[distA.argsort()[:3]]
                Bstations = stations.iloc[distB.argsort()[:3]]
                # print(Astations.iloc[1,])
                # print(Astations.iloc[2,])
                # print(Astations.iloc[3,])
                # print(stations.iloc[np.argmin(distA),])
                # infoA=stations.iloc[np.argmin(distA),]
                # infoB=stations.iloc[np.argmin(distB),]

                # nearest start station
                stat1name=Astations.iloc[0,][0]
                stat1lat=Astations.iloc[0,][1]
                stat1lng=Astations.iloc[0,][2]
                
                # backup start station 1
                stat1aname=Astations.iloc[1,][0]
                stat1alat=Astations.iloc[1,][1]
                stat1alng=Astations.iloc[1,][2]

                # backup start station 2
                stat1bname=Astations.iloc[2,][0]
                stat1blat=Astations.iloc[2,][1]
                stat1blng=Astations.iloc[2,][2]

                # nearest end station
                stat2name=Bstations.iloc[0,][0]
                stat2lat=Bstations.iloc[0,][1]
                stat2lng=Bstations.iloc[0,][2]
                
                # backup end station 1
                stat2aname=Bstations.iloc[1,][0]
                stat2alat=Bstations.iloc[1,][1]
                stat2alng=Bstations.iloc[1,][2]

                # backup end station 2
                stat2bname=Bstations.iloc[2,][0]
                stat2blat=Bstations.iloc[2,][1]
                stat2blng=Bstations.iloc[2,][2]

                # max1=infoA[3]
                # max2=infoB[3]

                max1=Astations.iloc[0,][3]
                max1a=Astations.iloc[1,][3]
                max1b=Astations.iloc[2,][3]
                max2=Bstations.iloc[0,][3]
                max2a=Bstations.iloc[1,][3]
                max2b=Bstations.iloc[2,][3]

                # get the current time (on server this is UTC)
                now=datetime.now()

                # walking directions to nearest station
                trip1=gmaps.directions(str(coordA['lat'])+","+str(coordA['lng']),str(stat1lat)+","+str(stat1lng),mode="walking",departure_time=now)
                walktime1=trip1[0]['legs'][0]['duration']['value']

                time1=now+timedelta(seconds=walktime1)

                # biking directions from station to station
                trip2=gmaps.directions(str(stat1lat)+","+str(stat1lng),str(stat2lat)+","+str(stat2lng),mode="bicycling",departure_time=time1)
                biketime=trip2[0]['legs'][0]['duration']['value']

                time2=now+timedelta(seconds=biketime)
                
                # walking directions from station to end point
                trip3=gmaps.directions(str(stat2lat)+","+str(stat2lng),str(coordB['lat'])+","+str(coordB['lng']),mode="walking",departure_time=time2)
                walktime2=trip3[0]['legs'][0]['duration']['value']

                # print("WALK TIME 1 " + str(walktime1))
                # print("BIKE TIME " + str(biketime))
                # print("WALK TIME 2 " + str(walktime2))

                # print(time1)
                # print(time2)

                # convert to EST
                time1=time1-timedelta(hours=4)
                time2=time2-timedelta(hours=4)

                # print(time1)
                # print(time2)
                
                hour1=time1.hour
                min1=hour1*60+time1.minute
                month1=time1.month
                day1=time1.day
                weekday1=time1.weekday()
                year1=time1.year

                s1winter=0
                s1spring=0
                s1summer=0
                s1fall=0

                weekend1=0
                
                if (month1==12 or month1<=2):
                    # s="winter"
                    s1winter=1
                elif (month1>=3 and month1<=5):
                    # s="spring"
                    s1spring=1
                elif (month1>=6 and month1<=8):
                    # s="summer"
                    s1summer=1
                elif (month1>=9 and month1<=11):
                    # s="fall"
                    s1fall=1

                if (weekday1==5 or weekday1==6):
                    weekend1=1
                
                dtest1=pd.DataFrame()
                dtest1['year']=pd.Series(year1)
                dtest1['month']=month1
                dtest1['day']=day1
                # dtest1['hour']=hour1
                dtest1['min']=min1
                dtest1['lat']=stat1lat
                dtest1['lng']=stat1lng
                dtest1['weekend']=weekend1
                # dtest1['fall']=s1fall
                # dtest1['spring']=s1spring
                # dtest1['summer']=s1summer

                dtest1a=pd.DataFrame()
                dtest1a['year']=pd.Series(year1)
                dtest1a['month']=month1
                dtest1a['day']=day1
                # dtest1['hour']=hour1
                dtest1a['min']=min1
                dtest1a['lat']=stat1alat
                dtest1a['lng']=stat1alng
                dtest1a['weekend']=weekend1
                # dtest1['fall']=s1fall
                # dtest1['spring']=s1spring
                # dtest1['summer']=s1summer

                dtest1b=pd.DataFrame()
                dtest1b['year']=pd.Series(year1)
                dtest1b['month']=month1
                dtest1b['day']=day1
                # dtest1['hour']=hour1
                dtest1b['min']=min1
                dtest1b['lat']=stat1blat
                dtest1b['lng']=stat1blng
                dtest1b['weekend']=weekend1
                # dtest1['fall']=s1fall
                # dtest1['spring']=s1spring
                # dtest1['summer']=s1summer

                hour2=time2.hour
                min2=hour2*60+time2.minute
                month2=time2.month
                day2=time2.day
                weekday2=time2.weekday()
                year2=time2.year

                s2winter=0
                s2spring=0
                s2summer=0
                s2fall=0

                weekend2=0
                
                if (month2==12 or month2<=2):
                    # s="winter"
                    s2winter=1
                elif (month2>=3 and month2<=5):
                    # s="spring"
                    s2spring=1
                elif (month2>=6 and month2<=8):
                    # s="summer"
                    s2summer=1
                elif (month2>=9 and month2<=11):
                    # s="fall"
                    s2fall=1

                if (weekday2==5 or weekday2==6):
                    weekend2=1                

                dtest2=pd.DataFrame()
                dtest2['year']=pd.Series(year2)
                dtest2['month']=month2
                dtest2['day']=day2
                # dtest2['hour']=hour2
                dtest2['min']=min2
                dtest2['lat']=stat2lat
                dtest2['lng']=stat2lng
                dtest2['weekend']=weekend2
                # dtest2['fall']=s2fall
                # dtest2['spring']=s2spring
                # dtest2['summer']=s2summer

                dtest2a=pd.DataFrame()
                dtest2a['year']=pd.Series(year2)
                dtest2a['month']=month2
                dtest2a['day']=day2
                # dtest2['hour']=hour2
                dtest2a['min']=min2
                dtest2a['lat']=stat2alat
                dtest2a['lng']=stat2alng
                dtest2a['weekend']=weekend2
                # dtest2['fall']=s2fall
                # dtest2['spring']=s2spring
                # dtest2['summer']=s2summer

                dtest2b=pd.DataFrame()
                dtest2b['year']=pd.Series(year2)
                dtest2b['month']=month2
                dtest2b['day']=day2
                # dtest2['hour']=hour2
                dtest2b['min']=min2
                dtest2b['lat']=stat2blat
                dtest2b['lng']=stat2blng
                dtest2b['weekend']=weekend2
                # dtest2['fall']=s2fall
                # dtest2['spring']=s2spring
                # dtest2['summer']=s2summer


                # print(dtest1)
                # print(dtest1a)
                # print(dtest1b)
                # print(dtest2)
                # print(dtest2a)
                # print(dtest2b)
                # print(os.getcwd()+"/data/RF0.snek")
                # load random forest
                # rf = joblib.load(os.getcwd()+"/data/RF0.snek")
                rf = joblib.load("data/RF0.snek")
                print("LOADED MODEL")
                # rf = joblib.load("/home/ubuntu/hhtm/data/RF0.snek")

                b1=max(min(int(round(rf.predict(dtest1)[0])),max1),0)
                b1a=max(min(int(round(rf.predict(dtest1a)[0])),max1a),0)
                b1b=max(min(int(round(rf.predict(dtest1b)[0])),max1b),0)
                b2=max(min(int(round(rf.predict(dtest2)[0])),max2),0)
                b2a=max(min(int(round(rf.predict(dtest2a)[0])),max2a),0)
                b2b=max(min(int(round(rf.predict(dtest2b)[0])),max2b),0)

                ampm1=" AM"
                ampm2=" AM"
                
                # hour1=hour1-4
                # hour2=hour2-4

                # if (hour1<0):
                #         hour1=hour1+24
                # if (hour2<0):
                #         hour2=hour2+24

                if (hour1>=12):
                        ampm1=" PM"
                if (hour2>=12):
                        ampm2=" PM"

                hour1=hour1%12
                hour2=hour2%12
                
                if (hour1==0):
                        hour1=12
                if (hour2==0):
                        hour2=12

                t1 = str(hour1) + ":" + str('{:02d}'.format(time1.minute)) + ampm1
                t2 = str(hour2) + ":" + str('{:02d}'.format(time2.minute)) + ampm2
                
                # b1 = "At " + str(hour1) + ":" + str('{:02d}'.format(time1.minute)) + ampm1 + ", " + stat1name + " is predicted to have " + str(b1) + " out of " + str(max1) + " bikes"
                # b2 = "At " + str(hour2) + ":" + str('{:02d}'.format(time2.minute)) + ampm2 + ", " + stat2name + " is predicted to have " + str(b2) + " out of " + str(max2) + " bikes"
                # print(b)
                # print(b2)

                b1 = str(b1) + " out of " + str(max1) + " bikes"
                b2 = str(b2) + " out of " + str(max2) + " bikes"
                b1a = str(b1a) + " out of " + str(max1a) + " bikes"
                b1b = str(b1b) + " out of " + str(max1b) + " bikes"
                b2a = str(b2a) + " out of " + str(max2a) + " bikes"
                b2b = str(b2b) + " out of " + str(max2b) + " bikes"

        return (jsonify(t1=t1,t2=t2,b1=b1,b2=b2,b1a=b1a,b1b=b1b,b2a=b2a,b2b=b2b,
                startlat=coordA['lat'],startlng=coordA['lng'],
                endlat=coordB['lat'],endlng=coordB['lng'],
                stat1name=stat1name,stat2name=stat2name,
                stat1aname=stat1aname,stat2aname=stat2aname,
                stat1bname=stat1bname,stat2bname=stat2bname,
                stat1lat=stat1lat,stat1lng=stat1lng,
                stat1alat=stat1alat,stat1alng=stat1alng,
                stat1blat=stat1blat,stat1blng=stat1blng,
                stat2lat=stat2lat,stat2lng=stat2lng,
                stat2alat=stat2alat,stat2alng=stat2alng,
                stat2blat=stat2blat,stat2blng=stat2blng))
    except Exception as e:
        return(str(e))

@app.route('/')
@app.route('/index')
def testing():
    return render_template("ggmaps.html")

@app.route('/about')
def about():
    return render_template("about2.html")

##@app.route('/contact')
##def contact():
##    return render_template("contact.html")
