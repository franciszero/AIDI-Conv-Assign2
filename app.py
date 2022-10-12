from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)
app.debug = True

reply = """
{
	"fulfillmentMessages": [{
		"payload": {
			"telegram": {
			    "text": "https://www.baidu.com/img/pc_79bff59263430e2e42693b50cf376490.png\\nhttps://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png5",
				"entities": [{
					"type": "text_link",
					"url": "https://www.baidu.com/img/pc_79bff59263430e2e42693b50cf376490.png"
				}]
			}
		}
	}]
}
 """
jobj = json.loads(reply)
i = None


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
    reply = """
{
	"fulfillmentMessages": [{
		"payload": {
			"telegram": {
			    "text": "https://www.baidu.com/img/pc_79bff59263430e2e42693b50cf376490.png\\nhttps://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
				"entities": [{
					"type": "text_link",
					"url": "https://www.baidu.com/img/pc_79bff59263430e2e42693b50cf376490.png"
				}]
			}
		}
	}]
}
     """
    return json.dumps(json.loads(reply))


def request_nasa_searching(query_program, description):
    req_url = "https://images-api.nasa.gov/search?q=%s&description=%s&media_type=image" % (query_program, description)
    r = requests.get(req_url, headers={'Content-Type': 'application/json'}).json()
    total_hits = r["collection"]["metadata"]["total_hits"]
    if total_hits == 0:
        return '{"fulfillmentMessages": [{ \
                    "text": {\
                        "text": ["total_hits: 0. href: %s. Please retry."] \
                    } \
                }]}' % r["collection"]["href"]

    nasa_id = str(r["collection"]["items"][0]['data'][0]['nasa_id'])
    req_url = "https://images-api.nasa.gov/asset/%s" % nasa_id
    r = requests.get(req_url, headers={'Content-Type': 'application/json'}).json()

    images = []
    items = r["collection"]["items"]
    for _, item in enumerate(items):
        images.append(str(item['href']))
    reply = '{ "fulfillmentMessages": [{ \
            "text": {\
                "text": %s \
            } \
        }]}' % json.dumps(images)
    return reply


@app.route('/webhook', methods=['POST'])
# for webhook examples, see: https://cloud.google.com/dialogflow/es/docs/fulfillment-webhook
# for Custom payload responses, see: https://cloud.google.com/dialogflow/es/docs/integrations/telegram
# for Telegram msg doc, see: https://core.telegram.org/bots/api#message
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
