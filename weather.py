from flask import Flask,render_template,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
import requests

app=Flask(__name__)
app.config["DEBUG"]= True
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:Asutosh@1@localhost/weather'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["SECRET_KEY"]="thisissecret"

db=SQLAlchemy(app)

class City(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False,unique=True)

def get_weather_data(city):
    url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid=adfe6d188e7bc7df6724edb9b8eeaf98"
    r=requests.get(url).json()
    return r
@app.route('/')
def index_get():
    cities=City.query.all()
    weather_data=[]
    for city in cities:
        r=get_weather_data(city.name)
        weather={"city":city.name,"temperature":r["main"]["temp"],"description":r["weather"][0]["description"],"icon":r["weather"][0]["icon"]}
        weather_data.append(weather)
    return render_template("weather.html",weather_data=weather_data)

@app.route('/',methods=["POST"])
def index_post():
    err_msg=""
    new_city=request.form.get("city")
    if new_city:
        existing_city=City.query.filter_by(name=new_city).first()
        if not existing_city:
            new_city_data=get_weather_data(new_city)
            if new_city_data["cod"] ==200:
                print(new_city_data)
                new_city_obj=City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                return "City does not exist in the world!"
        else:
            return "City already exists in the database!"
    return redirect(url_for("index_get"))

@app.route("/delete/<name>")
def delete_city(name):
    city=City.query.filter_by(name=City.name).first()
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for("index_get"))
