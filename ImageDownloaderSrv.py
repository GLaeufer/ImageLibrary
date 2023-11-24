
''' 
####### Instructions
Task

Implement a web service with a REST interface (preferably in python). The service should offer 3 REST operations.

1) upload of a list of image urls and download of the corresponding images

Given a list of image urls. When the user sends this list to the service via http, the service starts downloading the images. The service puts the images into a storage, so that they can be listed by and retrieved from the service, see below operation 2) & 3). There is no need to handle download errors: should a link to the image be wrong or the image can not be downloaded, it is just left out. The storage should be persistent, i.e. not in memory.

2) get list of available images

When the user calls this operation via http,the service replies with a list of all images that had been (sucessfully) processed via calls to the previous operation 1). 

3) retrieve an image

Given that there were previously images processed via operation 1), when the user calls this operation with an url as an input-parameter, then the service sends the corresponding image, if it was stored previously via operation 1).

Throughout operation 1)-3), the key of images should always be the full url that was used in the original input list for operation 1) 
'''

from flask import Flask, json, request, jsonify, send_file
import os
import requests
import hashlib


### Initialize server
app = Flask(__name__)

# Create a directory for the Images
image_dir_path = "./ImageDir"
os.makedirs(image_dir_path, exist_ok=True)

# Load urls into memory from a file
image_map_file = 'saved_images.json'
image_map = {}

def init_server():
    global image_map
    image_map = load_image_map()
    
    app.run(debug=True)

def load_image_map():
    try:
        with open(image_map_file, 'r') as f:
            return json.load(f)
        
    except FileNotFoundError:
        return {}

# Save all processed urls to a file
def save_image_map():
    with open(image_map_file, 'w') as f:
        json.dump(image_map, f)
        
def process_image(response, url):
    # hash the image for a unique name
    image_hash = hashlib.sha256(response.content).hexdigest()
    
    # retrieve the file extension from the response
    extension = response.headers.get('content-type').split('/')[-1]
    
    # Could exclude non-image extensions here or right after the download request
    # For now assuming that all urls passed to the url_list are links to images
    filename = f'{image_hash}.{extension}'
    file_location = os.path.join(image_dir_path, filename)
    
    
    # store the image in the image folder and update map
    with open(file_location, 'wb') as f:
        f.write(response.content)
    
    image_map[url] = file_location
        
# Default route responds with info message
@app.route('/')
def index():
    return jsonify({'message': 'server is running'})

# Process all images if a url_list was given
@app.route('/images', methods=['POST'])
def process_images():
    data = request.get_json()
    if 'url_list' not in data:
        return jsonify({'error': 'no url_list parameter found'}), 400
    
    urls = data['url_list']
    for url in urls:
        try:
            if url not in image_map: 
                download_response = requests.get(url)
            
                if download_response.status_code == 200:
                    process_image(download_response, url)
                else:
                    print(f"{url} could not get processed")
                
        except:
            print("BadURL") # Leaving out further error handling due to instructions
            
        save_image_map()
        
    return jsonify({'message':'OK'}), 200

# load all currently saved images and return them as a list (Assuming that "a list of all images" means returning a list of Urls and not a list of image files)
# For simplicity's sake returning the whole map here.
@app.route('/images', methods=['GET'])
def get_all_images():
    image_map = load_image_map()
    return jsonify({'url_list': image_map}), 200

# Retrieve one saved image from a url
@app.route('/image', methods=['GET'])
def get_image():
    image_map = load_image_map()
    
    full_path = request.full_path
    url = full_path.split("url=")[1]
    
    if url is None: 
        return jsonify({'error': "no url given"}), 400
    elif url in image_map:
        return send_file(image_map[url], as_attachment=True)
    else:
        return jsonify({'error': "Image not found"}), 404
    

    
    
if __name__ == '__main__':
    init_server()