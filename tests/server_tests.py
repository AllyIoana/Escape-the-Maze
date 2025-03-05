import os
import unittest
import sys
import requests
import subprocess
import time
import io
from PIL import Image


class ServerTestCase(unittest.TestCase):

    SERVER_IP = '127.0.0.1'
    SERVER_PORT = '8000'
    SERVER_URL = f'http://{SERVER_IP}:{SERVER_PORT}'

    ROUTE_INDEX = '/'
    ROUTE_MAZE = '/maze'
    ROUTE_AGENTS = '/agents'
    ROUTE_AGENT = '/agent'
    ROUTE_FRIENDLY = '/toggle_friendly_mode'

    def create_agent(self, input):
        response = requests.post(
            self.SERVER_URL + self.ROUTE_INDEX,
            json={
                "input": input
            }
        )
        return response

    def stop_server(self, server_process):
        server_process.terminate()
        server_process.wait()
        if server_process.stdout:
            server_process.stdout.close()  # Close stdout
        if server_process.stderr:
            server_process.stderr.close()  # Close stderr

    def start_server(self):
        server_dir = os.path.abspath('../server')  # Adjust path as needed
        process = subprocess.Popen(
            ['uvicorn', 'server:app', '--host',
                self.SERVER_IP, '--port', self.SERVER_PORT],
            cwd=server_dir,  # Set the working directory
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(10)  # Wait for the server to start
        return process

    def test_index(self):
        server_process = self.start_server()
        try:
            response = self.create_agent("S")

            self.assertEqual(response.status_code, 200)

            # assert that response has fields UUID, x, y, width, height, view, moves
            json = response.json()

            self.assertTrue('UUID' in json)
            self.assertTrue('x' in json)
            self.assertTrue('y' in json)
            self.assertTrue('width' in json)
            self.assertTrue('height' in json)
            self.assertTrue('view' in json)
            self.assertTrue('moves' in json)

            response = requests.post(
                self.SERVER_URL + self.ROUTE_INDEX,
                json={
                    "UUID": json['UUID'],
                    "input": "S"
                }
            )

            self.assertEqual(response.status_code, 200)

            # assert that response has fields name, successful, view, moves
            json = response.json().get('command_1')

            self.assertTrue('name' in json)
            self.assertTrue('successful' in json)
            self.assertTrue('view' in json)
            self.assertTrue('moves' in response.json())

            response = self.create_agent("S")

            self.assertEqual(response.status_code, 200)

            # assert that response has fields UUID, x, y, width, height, view, moves
            # assert that agent id is 1
            json = response.json()

            self.assertTrue('UUID' in json)
            self.assertEqual(int(json['UUID']), 1)
            self.assertTrue('x' in json)
            self.assertTrue('y' in json)
            self.assertTrue('width' in json)
            self.assertTrue('height' in json)
            self.assertTrue('view' in json)
            self.assertTrue('moves' in json)

        finally:
            self.stop_server(server_process)

    def test_server(self):
        server_process = self.start_server()
        try:
            response = requests.get(self.SERVER_URL + self.ROUTE_MAZE)
            self.assertEqual(response.status_code, 200)

            with io.BytesIO(response.content) as img_stream:
                image = Image.open(img_stream)
                image.save("processed_image.png")
                image.close()

            response = requests.post(
                self.SERVER_URL + self.ROUTE_MAZE,
                json={
                    'width': 100,
                    'height': 100,
                })
            self.assertEqual(response.status_code, 200)

            response = requests.get(self.SERVER_URL + self.ROUTE_MAZE)
            self.assertEqual(response.status_code, 200)

            with io.BytesIO(response.content) as img_stream:
                image = Image.open(img_stream)
                image.save("processed_image1.png")
                image.close()

            # assert that the two images are different
            image1 = Image.open("processed_image.png")
            image2 = Image.open("processed_image1.png")
            self.assertNotEqual(image1.tobytes(), image2.tobytes())

            # close images
            image1.close()
            image2.close()

            # delete images
            os.remove("processed_image.png")
            os.remove("processed_image1.png")

        finally:
            self.stop_server(server_process)

    def test_agents(self):
        server_process = self.start_server()
        try:
            response = requests.get(self.SERVER_URL + self.ROUTE_AGENTS)
            self.assertEqual(response.status_code, 200)

            response = self.create_agent("S")
            self.assertEqual(response.status_code, 200)

            response = requests.get(self.SERVER_URL + self.ROUTE_AGENTS)
            self.assertEqual(response.status_code, 200)

            # assert that the agents list has one agent
            self.assertEqual(len(response.json()), 1)

            response = self.create_agent("S")
            self.assertEqual(response.status_code, 200)

            response = requests.get(self.SERVER_URL + self.ROUTE_AGENTS)
            self.assertEqual(response.status_code, 200)

            # assert that the agents list has two agents
            self.assertEqual(len(response.json()), 2)

            response = requests.get(self.SERVER_URL + self.ROUTE_AGENT + '/0')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['uuid'], 0)

            response = requests.get(self.SERVER_URL + self.ROUTE_AGENT + '/1')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['uuid'], 1)

        finally:
            self.stop_server(server_process)

    def test_friendly_server(self):
        server_process = self.start_server()

        try:

            response = self.create_agent("S")
            self.assertEqual(response.status_code, 200)

            # assert that response has fields UUID, x, y, width, height, view, moves
            json = response.json()
            self.assertTrue('UUID' in json)
            self.assertTrue('x' in json)
            self.assertTrue('y' in json)
            self.assertTrue('width' in json)
            self.assertTrue('height' in json)
            self.assertTrue('view' in json)
            self.assertTrue('moves' in json)

            response = requests.post(self.SERVER_URL + self.ROUTE_FRIENDLY)
            self.assertEqual(response.status_code, 200)

            response = self.create_agent("S")
            self.assertEqual(response.status_code, 200)

            # assert that response has fields UUID, view, moves
            json = response.json()
            self.assertTrue('UUID' in json)
            self.assertTrue('view' in json)
            self.assertTrue('moves' in json)
            self.assertTrue('x' not in json)
            self.assertTrue('y' not in json)
            self.assertTrue('width' not in json)
            self.assertTrue('height' not in json)

        finally:
            self.stop_server(server_process)


if __name__ == '__main__':
    unittest.main(verbosity=2)
