from flask import Flask, render_template, request
from operator import index
import base64
import os
from dotenv import load_dotenv
import json
from requests import get, post



app = Flask(__name__)
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_byte = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_byte), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    
    

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len (json_result) == 0 :
        print("Uhm are you sure thats your favorite artist? Cuz we dont know them ")
        return None
    
    return json_result[0]


def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get (url, headers=headers)
    json_results = json.loads(result.content)["tracks"]
    return json_results


@app.route("/")
def homepage():
    return render_template("index.html")



# getting data from HTLM and sending it 
@app.route('/process', methods=['POST']) 
def process():
    
    artist_input = request.form['artistInput']
    token = get_token()
    result = search_for_artist(token, artist_input)
    if result:
        artist_id = result['id']
        tracks = get_songs_by_artist(token, artist_id)
        return render_template('index.html', result=result, tracks=tracks, error_message=None)
    else:
        error_message = "Oops! Are you sure that's your favorite artist? We couldn't find them."

        return render_template('index.html', result=None, tracks=[], error_message=error_message)    
    
    
 

if __name__ == '__main__':
    app.run(debug=True)
