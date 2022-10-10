from flask import Flask, render_template, request
import requests

app = Flask(__name__)
app.debug = True


@app.route("/")
def hello():
    return "<p>Hello 111</p>"


@app.route("/webpage")
def webpage():
    return render_template("1.html")


# see: https://github.com/rbigelow/flask-intro/blob/main/app.py
@app.route("/ross")
def ross():
    return "<p> Hi I'm Ross. </p><img src='https://bigelow.cc/wp-content/uploads/sites/3/cropped-ross-bigelow.png'> "


@app.route('/webhook', methods=['POST'])
def index():
    # Get the geo-city entity from the dialogflow fullfilment request.
    body = request.json
    city = body['queryResult']['parameters']['geo-city']

    # Uncomment the next 2 lines  if you want to use a simple hard coded random reply.
    # temperature = str(random.randint(-20,35))
    # reply = '{"fulfillmentMessages": [ {"text": {"text": ["The  temperature in '+ city +", "+ country +' it is ' + temperature + '"] } } ]}'

    # To openweather and return a real f orcast note you will need to
    # create an account at openweathermap.com and put your APPID below.
    appId = '9ae09c8334e9478b8e50f3b396a222a7'

    # Connect to the API anf get the JSON file.
    api_url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&appid=' + appId
    headers = {'Content-Type': 'application/json'}  # Set the HTTP header for the API request
    response = requests.get(api_url, headers=headers)  # Connect to openweather and read the JSON response.
    r = response.json()  # Conver the JSON string to a dict for easier parsing.

    # Extract weather data we want from the dict and conver to strings to make it easy to generate the dialogflow reply.
    weather = str(r["weather"][0]["description"])
    temp = str(int(r['main']['temp']))
    humidity = str(r["main"]["humidity"])
    pressure = str(r["main"]["pressure"])
    windSpeed = str(r["wind"]["speed"])
    windDirection = str(r["wind"]["deg"])
    country = str(r["sys"]["country"])
    # build the Dialogflow reply.
    reply = '{"fulfillmentMessages": [ {"text": {"text": ["Currently in ' + city + ', ' + country + ' it is ' + temp + ' degrees and ' + weather + '"] } } ]}'
    return reply


myData = {
    "name": 'Ross Bigelow',
    "dream": "To inspire others to fulfil thier dreams.",
    'age': 1,
    'birthdate': "2020-01-01"
}


@app.route("/json")
def myJson():
    return myData
