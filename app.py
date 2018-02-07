import sys
import json
import getpass
import httplib2
from flask import Flask, request, render_template, jsonify
from datetime import datetime
app = Flask(__name__)

http = httplib2.Http()

@app.route('/')
def my_form():
    return render_template('login.html')

@app.route('/', methods=['POST'])
def homepage():
	the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")
	DEBUG = 0
	# endpoint
	URL = 'http://111.93.164.203/CampusPortalSOA'
	reglov = 'ITERRETD1711A0000002'

	username = request.form['username']
	password = request.form['password']

	body = json.dumps({'username':username,'password':password})

	headers = {'Content-type': 'application/json'}
	response, logincontent = http.request(URL + '/login', 'POST', headers=headers, body=body)
		
	if(len(logincontent) > 112):
		print('Login Successful!')
		
		logindata = json.loads(logincontent)
		
		message = '<html> <head> <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"> <link type="text/css" rel="stylesheet" href="static/material/css/materialize.css" media="screen,projection"/> <meta name="viewport" content="width=device-width, initial-scale=1.0"/> </head> <body>'
		
		message += 'Hello ' + logindata["name"] + '!<br>'
	
		body = json.dumps({'registerationid':reglov})

		headers = {'Cookie': response['set-cookie']}
		response, attendancecontent = http.request(URL + '/attendanceinfo', 'POST', headers=headers, body=body)
	
		data = json.loads(attendancecontent)
		data_size = len(data["griddata"])
		
		message += '<table class="striped"> <tr> <th>Subject</th> <th>Attendance</th> <th>Last updated on</th> </tr>'
		
		for i in range(0, data_size): 
			message += '<tr><td>' + data["griddata"][i]["subject"] + '</td><td>' + str(data["griddata"][i]["TotalAttandence"]) + '%</td>' + '<td>' + data["griddata"][i]["lastupdatedon"] + '</td></tr>'
		
		message += '</table><script type="text/javascript" src="https://code.jquery.com/jquery-3.2.1.min.js"></script> <script type="text/javascript" src="static/material/js/materialize.js"></script> </body> </html>'
		return message
		
		response, logoutcontent = http.request(URL + '/logout', 'GET', headers=headers, body=body)
	else:
		return ("Username or Password may be wrong!")
		if(DEBUG):
			print('Response Status - ', response.status)

if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)
