from flask import Flask, render_template, jsonify,redirect, url_for, request, session
import json 
import utils

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the random string'


with open('details.json', 'r') as f:
    users = json.load(f)

news_list = utils.get_news()["articles"][:6]

class Post:
    def __init__(self, title, image_url):
        self.title = title
        self.image_url = image_url


posts = []
for i in range(len(news_list)):
    posts.append(Post(news_list[i]["title"], news_list[i]["urlToImage"]))


@app.route('/', methods=['GET', 'POST'])
def login():
  
    if request.method == 'POST':
        global latitude
        global longitude
       
        # data = request.get_json()
        longitude = request.form['longitude']
        latitude = request.form['latitude']

        username = request.form['email']
        password = request.form['password']

        print('user {username} password {password} ')
        
        if username in users.keys() and users[username] == password:
            return redirect(url_for('weatherDetails'))
        
        error = 'Invalid username or password'
        return render_template('Login.html', error=error)
    
    return render_template('Login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirm-password']

        print('user {email} password {password} confirm passs {confirmPassword}')

        users[email] = password
        with open('details.json', 'w') as jf:
            json.dump(users, jf)

        return redirect(url_for('login'))
    
    return render_template('Signup.html')



@app.route('/weatherDetails', methods=['GET', 'POST'])
def weatherDetails():
    #send data in this format after reciving fron the api (converet the api data to this json format and then send to front end)
    data = utils.get_current_weather_data()
    return render_template('Weather.html',data=data)


# @app.route('/floodzone', methods=['POST', 'GET'])
# def floodzone():
#     return render_template('FloodZone.html' ,map={"map1": "", "map2": " "})

def get_map(zone):
    maps = {
        "flood Map": utils.get_flood_map(),
        "lake": utils.get_lake_zones(),
        "drainage": utils.get_drinage_lines(),
    }
    return maps.get(zone, "default_map_url_if_zone_not_found")



@app.route('/floodzone', methods=['POST', 'GET'])
def floodzone():
    if request.method == 'POST':
        selected_zone = request.form.get('zone')
        map_image_url = get_map(selected_zone)
        return render_template('FloodZone.html', map=map_image_url)
    else:
        return render_template('FloodZone.html', map=None)


@app.route('/alert', methods=['POST', 'GET'])
def alert():    
    return render_template('Alert.html', posts=posts)


# @app.route('/shelter', methods=['POST', 'GET'])
# def Shelter():    

#     if request.method == 'POST':
#         print("POST METHOD INVOKED")
#         return redirect(url_for('shelter_map_page'))
#         # location = request.get_json()
#         # print(location['data'])
#         # latitude, longitude = utils.get_lat_long_for_ip()
#         # map_html = utils.shelter_map(latitude, longitude)
#         # # print(map_html)
#         # # return render_template('map.html', map=map_html)
#         # return jsonify({'map':map_html})

#     return render_template('Shelter.html')


# @app.route('/shelter_map_page', methods=['GET'])
# def shelter_map_page():

#     location = request.get_json()
#     print(location['data'])
#     latitude, longitude = utils.get_lat_long_for_ip()
#     map_html = utils.shelter_map(latitude, longitude)
#     print(map_html)

#     return render_template('map2.html', map=map_html)


@app.route('/shelter', methods=['POST', 'GET'])
def shelter():
    if request.method == 'POST':
        location_data = request.json  # Assuming JSON data is sent
        session['location_data'] = location_data  # Store the data in session
        return redirect(url_for('shelter_map_page'))

    return render_template('Shelter.html')

@app.route('/shelter_map_page', methods=['GET'])
def shelter_map_page():
    location_data = session.get('location_data')  # Retrieve the data from session
    if location_data:
        latitude, longitude = utils.get_lat_long_for_ip()
        map_html = utils.shelter_map(latitude, longitude)
        return render_template('map.html', map=map_html)
    return "No location data found", 404


@app.route('/sos' , methods=['POST','GET'])
def sos():
   if request.method=='POST':
       name = request.form['name']
       situation = request.form['situation']
       contact = request.form['contact']
       utils.send_email(name, situation, contact)

   return render_template('Sos.html')


if __name__ == '__main__':
    app.run(debug=True)