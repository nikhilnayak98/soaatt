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
    return render_template('my-form.html')

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

	if(DEBUG):
		return ('Response Status - ', response.status)
		return ('Length of Login content - ', len(logincontent))
		
	if(len(logincontent) > 112):
		print('Login Successful!')
	
	print ('Login content - ', logincontent)
	
	body = json.dumps({'registerationid':reglov})

	headers = {'Cookie': response['set-cookie']}
	response, attendancecontent = http.request(URL + '/attendanceinfo', 'POST', headers=headers, body=body)
		
	if(DEBUG):
		print('Response Status - ', response.status)
	
	mydata = attendancecontent.get("grid")
	
	return (mydata)
		
	response, logoutcontent = http.request(URL + '/logout', 'GET', headers=headers, body=body)
	if(DEBUG):
		print(logoutcontent)
	else:
		return ("Username or Password may be wrong!")
		if(DEBUG):
			print('Response Status - ', response.status)

if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)
