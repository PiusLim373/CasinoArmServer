from flask import Flask, render_template, request, jsonify
import requests
import time
import json
import os
#from arm_pos import ik

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/StartGame')
def StartGame():
	os.system('python FaceRecog\FaceRecog.py')
	return "yo"

if __name__ == '__main__':
	app.run(debug = True)