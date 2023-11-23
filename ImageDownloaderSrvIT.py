import unittest
import ImageDownloaderSrv
import json
import requests
import os

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

class ImageDownloaderSrvIT(unittest.TestCase):
    image_dir_path = "./testDir"
    test_data = {}
    with open('test_images.json', 'r') as f:
        test_data = json.load(f)
    
        
        
    def test_everything(self):
        # POST images from a file to the server
        print(self.test_data)
        response = requests.post("http://127.0.0.1:5000/images", json=self.test_data)
        
        self.assertEqual(response.status_code, 200)
        
        # GET a list of the images that were posted
        response = requests.get("http://127.0.0.1:5000/images")
        json_data = response.json()
        url_list = json_data.get('url_list')
        self.assertEqual(len(url_list.keys()), 3)
        
        # GET an image from the list
        test_imgage_url = "https://marketplace.canva.com/EAEhuJyFkeY/1/0/1600w/canva-katze-vor-kaffee-nach-kaffee-zwei-fotos-und-text-meme-z-0fS-n3yf0.jpg"
        response = requests.get("http://127.0.0.1:5000/image?url="+ test_imgage_url)
        self.assertEqual(response.status_code, 200)
        
        extension = response.headers.get('content-type').split('/')[-1]
        testfile_path = f'testfile.{extension}'
        with open (testfile_path, 'wb')as f:
            f.write(response.content)
            
    
        self.assertTrue(os.path.exists(testfile_path),True)
                        
        # maybe show the image?
        img = mpimg.imread(testfile_path)
        imgplot = plt.imshow(img)
        plt.show()
          
    
        
        
if __name__ == '__main__':
    unittest.main()