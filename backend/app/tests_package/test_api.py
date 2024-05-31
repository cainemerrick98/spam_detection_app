import json, unittest
from fastapi.testclient import TestClient
from main import app


class TestApi(unittest.TestCase):

    def setUp(self) -> None:
        self.client = TestClient(app)
        return super().setUp()

    def test_read_root(self):
        """
        if we send a request to the root of the api we expect a response 
        that is a dictionary. The dictionary will have a key called "message" 
        and its value will be "Welcome to the spam detection api"
        """
        response = self.client.get('/')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json() == {'message':'Welcome to the spam detection api'})

    def test_predict_no_data(self):
        """
        if we dont send any content in the post request we expect a status code of 
        422 - Unprocessable entity
        """
        response = self.client.post(
            url='/predict/', 
        )
        self.assertTrue(response.status_code == 422)

    def test_predict_incorrect_data(self):
        """
        If the data does not match the structure expected by the pydantic model for 
        a prediction request then we expect a 422 error again.

        The structure expected is a dictionary like object with a key called content 
        and a value that is a string
        """
        #key is incorrect
        data = json.dumps({'email': 'some text'})
        response = self.client.post(
            url='/predict/',
            content=data
        )
        self.assertTrue(response.status_code == 422)
        
        data = json.dumps({'content':400})

        #value is a number
        response = self.client.post(
            url='/predict/',
            content=data
        )
        self.assertTrue(response.status_code == 422)
        

    def test_predict_correct_data(self):
        """
        If the content is of the correct structure then we expect a response code of 200
        We also expect a dictionary to be returned with the classification of the email as
        spam or ham and the probability of the email being spam
        """
        data = json.dumps({'content': 'Hi, you have won £1 million pounds please click the <a>link<a> below to find out more.'})
        response = self.client.post(
            url = '/predict/',
            content = data
        )
        self.assertTrue(response.status_code == 200)
        response_content = response.content
        
