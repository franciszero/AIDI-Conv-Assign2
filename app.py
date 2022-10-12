from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)
app.debug = True


@app.route("/")
def hello():
    dic = {
        "name": "Fangji Chen",
        "Student ID": 200520598,
    }
    s = json.dumps(dic, indent=4)
    return s


@app.route("/webpage")
def webpage():
    return render_template("1.html")


# see: https://github.com/rbigelow/flask-intro/blob/main/app.py
@app.route("/ross")
def ross():
    return "<p> Hi I'm Ross. </p><img src='https://bigelow.cc/wp-content/uploads/sites/3/cropped-ross-bigelow.png'> "


def request_open_weather(city):
    appId = '9ae09c8334e9478b8e50f3b396a222a7'
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
    #     reply = '''{"fulfillmentMessages":
    # [{
    #   "telegram": {
    #     "text": "Pick a color",
    #     "reply_markup": {
    #       "inline_keyboard": [
    #         [
    #           {
    #             "text": "Red",
    #             "callback_data": "Red"
    #           }
    #         ],
    #         [
    #           {
    #             "text": "Green",
    #             "callback_data": "Green"
    #           }
    #         ],
    #         [
    #           {
    #             "text": "Yellow",
    #             "callback_data": "Yellow"
    #           }
    #         ],
    #         [
    #           {
    #             "text": "Blue",
    #             "callback_data": "Blue"
    #           }
    #         ],
    #         [
    #           {
    #             "text": "Pink",
    #             "callback_data": "Pink"
    #           }
    #         ]
    #       ]
    #     }
    #   }
    # }]
    # }'''
    return reply


def request_nasa_searching(query_program, description):
    req_url = "https://images-api.nasa.gov/search?q=%s&description=%s&media_type=image" % (query_program, description)
    r = requests.get(req_url, headers={'Content-Type': 'application/json'}).json()
    example_response = """
    {
        "collection": {
            "href": "https://images-api.nasa.gov/search?q=apollo%2011...",
            "items": [{
                "data": [{
                    "center": "JSC",
                    "date_created": "1969-07-21T00:00:00Z",
                    "description": "AS11-40-5874 (20 July 1969) ",
                    "keywords": [
                        "APOLLO 11 FLIGHT",
                        "MOON",
                        "LUNAR SURFACE",
                        "LUNAR BASES",
                        "LUNAR MODULE",
                        "ASTRONAUTS",
                        "EXTRAVEHICULAR ACIVITY"
                    ],
                    "media_type": "image",
                    "nasa_id": "as11-40-5874",
                    "title": "Apollo 11 Mission image - Astronaut Edwin Aldrin poses beside th "
                }],
                "href": "https://images-assets.nasa.gov/image/as11-40-5874/collection.json",
                "links": [{
                    "href": "https://images-assets.nasa.gov/image/as11-40-5874/as11-40-5874~thumb.jpg",
                    "rel": "preview",
                    "render": "image"
                }]
            }],
            "links": [{
                "href": "https://images-api.nasa.gov/search?q=apollo+11...&page=2",
                "prompt": "Next",
                "rel": "next"
            }],
            "metadata": {
                "total_hits": 336
            },
            "version": "1.0"
        }
    }
    """
    nasa_id = None
    items = r["collection"]["items"]
    if len(items) > 0 :
        data = items[0]['data']
        if len(data) > 0 :
            nasa_id = str(data[0]['nasa_id'])
    if nasa_id is None:
        return '{"fulfillmentMessages": [{ \
                    "text": {\
                        "text": ["Fail. Please offer some other searching queries and descriptions."] \
                    } \
                }]}'
    else:
        req_url = "https://images-api.nasa.gov/asset/%s" % nasa_id
        r = requests.get(req_url, headers={'Content-Type': 'application/json'}).json()
        example_response = """
        {
            "collection": {
                "version": "1.0",
                "href": "http://images-api.nasa.gov/asset/PIA18906",
                "items": [{
                    "href": "http://images-assets.nasa.gov/image/PIA18906/PIA18906~orig.jpg"
                }]
            }
        }
        """
        img = str(r["collection"]["items"][0]['href'])
        reply = '{ "fulfillmentMessages": [{ \
            "card": { \
                "title": "title1", \
                "imageUri": "%s" \
            }] \
        }' % img
        return reply


@app.route('/webhook', methods=['POST'])
def index():
    # Get the geo-city entity from the dialogflow fullfilment request.
    body = request.json
    params = body['queryResult']['parameters']
    if 'geo-city' in params.keys():
        city = params['geo-city']
        reply = request_open_weather(city)
    elif 'nasa_program' in params.keys():
        query_program = params['nasa_program']
        description = params['description']
        reply = request_nasa_searching(query_program, description)
    else:
        reply = '{"fulfillmentMessages": [ {"text": {"text": ["route responses nothing"] } } ]}'
    return str(reply)


myData = {
    "name": 'Ross Bigelow',
    "dream": "To inspire others to fulfil thier dreams.",
    'age': 1,
    'birthdate': "2020-01-01"
}


@app.route("/json")
def myJson():
    return myData
