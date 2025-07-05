import requests
from datetime import datetime, timedelta
# from newsapi.newsapi_client import NewsApiClient
from email.message import EmailMessage
import ssl
import smtplib
from email.mime.image import MIMEImage
import folium
import random
import json 
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


def get_current_weather_data(lat=13.069457, lon=80.215355):

    now = datetime.now()
    today_date = now.date()
    current_day = now.strftime("%A")

    API_KEY = "8cfc54d6b4cc06795c8e314dcb7de780"
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()

    sunrise_timestamp = response['sys']['sunrise']
    sunset_timestamp = response['sys']['sunset']

    # Convert to datetime objects
    timezone_offset = 19800  # 5.5 hours

    # Convert to datetime objects in UTC
    sunrise_time_utc = datetime.utcfromtimestamp(sunrise_timestamp)
    sunset_time_utc = datetime.utcfromtimestamp(sunset_timestamp)

    # Convert to local time by adding the timezone offset
    sunrise_time_local = sunrise_time_utc + timedelta(seconds=timezone_offset)
    sunset_time_local = sunset_time_utc + timedelta(seconds=timezone_offset)

    # Format the time in the desired format (e.g., "5:30 PM")
    sunrise_formatted = sunrise_time_local.strftime("%I:%M %p")
    sunset_formatted = sunset_time_local.strftime("%I:%M %p")

    data= {
        "temp": f"{response['main']['temp']}", #give this in celcius only
        "date": today_date,
        "day": current_day,
        "wind":f"{response['wind']['speed']*10} km/hr",
        "humidity": response['main']['humidity'],
        "type": response['weather'][0]['description'],
        "Sunrise":f"{sunrise_formatted}",
        "Sunset":f"{sunset_formatted}"
    }

    return data


from geopy.geocoders import Nominatim

def address_to_lat_lng(address):
    geolocator = Nominatim(user_agent="address_to_lat_lng")
    
    try:
        location = geolocator.geocode(address)
        if location:
            lat = location.latitude
            lng = location.longitude
            return lat, lng
        else:
            print("Geocoding failed. Address not found.")
            return None
    except Exception as e:
        print(f"Error in geocoding: {str(e)}")
        return None
    

def shelter_map(lat, lng):
    m = folium.Map(location=[lat, lng], zoom_start=16)

    shelter_data = random.sample(get_nearest_shelter(lat, lng)['results'], 5)
    # with open('./data/shelters.json', 'r') as json_file:
    #     shelter_data = random.sample(json.load(json_file)['results'], 5)
        
    geojson_path = "./data/chennai_data.json"
    with open(geojson_path, 'r') as f:
        json_data = json.load(f)

    for feature in json_data['features']:
        region_name = feature['properties']['AC_NAME']
        if region_name.lower()=='egmore (sc)':
            shape = folium.GeoJson(
                feature,
                style_function=lambda feature: {
                    'fillColor': '#ff0000',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.6
                },
                tooltip=region_name,
            )
            shape.add_to(m)


    for location in shelter_data:
        lat = location['location']["lat"]
        lon = location['location']["lng"]
        name = location["name"]
        folium.Marker([lat, lon], popup=name, icon=folium.Icon(icon="school", prefix="fa")).add_to(m)

    return m._repr_html_()


def get_nearest_shelter(my_lat, my_long):
    print("GET NEAREST SHELTER")

    url = "https://trueway-places.p.rapidapi.com/FindPlacesNearby"

    querystring = {"location": "{}, {}".format(my_lat, my_long),"type":"school","radius":"180","language":"en"}

    headers = {
        "X-RapidAPI-Key": "ae132bb2c7msh62f4f248dafb0e6p180931jsn53356dfc0c76",
        "X-RapidAPI-Host": "trueway-places.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    print(response.json())

    return response.json()


def get_nearest(my_lat, my_long):
    url = "https://trueway-places.p.rapidapi.com/FindPlacesNearby"

    querystring = {"location": "{}, {}".format(my_lat, my_long), "type": "police_station", "radius": "2000", "language": "en"}

    headers = {
        "X-RapidAPI-Key": "d136a898admsh769a12d85806a56p1d0f24jsna19b023692ae",
        "X-RapidAPI-Host": "trueway-places.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()


def get_news():
    url = "https://newsapi.org/v2/everything?q=weather%20news%20india&apiKey=edaddbc3add54ca8920075e114cfec09"
    response = requests.get(url).json()
    return response


def get_lat_long_for_ip():
    response = requests.get('https://ipinfo.io')
    data = response.json()
    lat, long = map(float, data['loc'].split(','))
    return lat, long


def create_map(response):
    mls = response.json()['route']['geometry']['coordinates']
    points = [(mls[i][0], mls[i][1]) for i in range(len(mls))]
    m = folium.Map()
    for point in [points[0], points[-1]]:
        folium.Marker(point).add_to(m)
    folium.PolyLine(points, weight=5, opacity=1).add_to(m)
    df = pd.DataFrame(mls).rename(columns={0: 'Lon', 1: 'Lat'})[['Lat', 'Lon']]
    sw = df[['Lon', 'Lat']].min().values.tolist()
    ne = df[['Lon', 'Lat']].max().values.tolist()
    m.fit_bounds([sw, ne])
    return m


def get_flood_map():
    m = folium.Map(location=[13.082584, 80.214239], zoom_start=12)
    geojson_path = "./data/chennai_data.json"
    highlighted_regions = ["velachery", "virugampakkam", "royapuram", 'egmore (sc)']

    with open(geojson_path, 'r') as f:
        json_data = json.load(f)

    for feature in json_data['features']:
        region_name = feature['properties']['AC_NAME']
        shape = folium.GeoJson(
            feature,
            style_function=lambda feature: {
                'fillColor': '#ff0000' if feature['properties']['AC_NAME'].lower() in highlighted_regions else '#00FF00',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6
            },
            tooltip=region_name,
        )
        shape.add_to(m)

    m.add_child(folium.Element("""
    <script>
    function highlightFeature(e) {
        var layer = e.target;
        layer.setStyle({
            fillColor: '#00FF00'
        });
        layer.openPopup();
    }
    function resetHighlight(e) {
        var layer = e.target;
        layer.setStyle({
            fillColor: layer.Feature.properties.AC_NAME in highlighted_regions ? '#ff0000' : '#00FF00'
        });
        layer.closePopup();
    }
    geojsonLayer = geojson.getLayers()[0];
    geojson.eachLayer(function(layer) {
        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
        });
    });
    </script>
    """))

    return m._repr_html_()
    

def get_drinage_lines():
    m = folium.Map(location=[13.082584, 80.214239], zoom_start=12, tiles='CartoDB positron')

    with open('./data/gcc-swds.json', 'r') as f:
        area_json_file = json.load(f)
            
    folium.GeoJson(area_json_file).add_to(m)
    return m._repr_html_()


def get_lake_zones():
    m = folium.Map(location=[13.082584, 80.214239], zoom_start=12)

    with open('./data/water_areas.json', 'r') as f:
        area_json_file = json.load(f)
        
    with open('./data/water_lines.json', 'r') as f:
        line_json_file = json.load(f)
            
    folium.GeoJson(area_json_file).add_to(m)
    folium.GeoJson(line_json_file).add_to(m)

    return m._repr_html_()


def get_route(lat1, long1, lat2, long2):
    url = "https://trueway-directions2.p.rapidapi.com/FindDrivingRoute"

    querystring = {"stops":"{0},{1}; {2},{3}".format(lat1, long1, lat2, long2)}

    headers = {
        "X-RapidAPI-Key": "d136a898admsh769a12d85806a56p1d0f24jsna19b023692ae",
        "X-RapidAPI-Host": "trueway-directions2.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response



def send_email(name, situation, contact):

    lat, long = get_lat_long_for_ip()

    mail_sender = os.getenv('mail_sender')
    mail_password = os.getenv('mail_password')
    

    subject = 'Emergency Alert'
    text = f'Emergency Help Request from {name} from location: ({lat}, {long}) \n Type of Situation: {situation} \nContact: {contact}'

    em = EmailMessage()
    em['From'] = mail_sender
    em['To'] = os.getenv('mail_receiver')
    em['Subject'] = subject  # Corrected the key to 'Subject'

    # Set the formatted body content to the email
    em.set_content(text)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(mail_sender, mail_password)
        smtp.send_message(em)