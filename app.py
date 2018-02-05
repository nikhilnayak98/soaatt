import sys
import json
import getpass
import httplib2
from flask import Flask
from datetime import datetime
app = Flask(__name__)

http = httplib2.Http()

@app.route('/')
def homepage():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")
    DEBUG = 0
	if(len(sys.argv) >= 2):
		DEBUG = 1
	
	# endpoint
	URL = 'http://111.93.164.203/CampusPortalSOA'
	reglov = 'ITERRETD1711A0000002'

	username = input('Username - ')
	password = getpass.getpass('Password - ')

	body = json.dumps({'username':username,'password':password})

	headers = {'Content-type': 'application/json'}
	response, logincontent = http.request(URL + '/login', 'POST', headers=headers, body=body)

	if(DEBUG):
		print('Response Status - ', response.status)
		print('Length of Login content - ', len(logincontent))
		
	if(len(logincontent) > 112):
		print('Login Successful!')
	
	if(DEBUG):
		print('Login content - ', logincontent)
	
	body = json.dumps({'registerationid':reglov})

	headers = {'Cookie': response['set-cookie']}
	response, attendancecontent = http.request(URL + '/attendanceinfo', 'POST', headers=headers, body=body)
		
	if(DEBUG):
		print('Response Status - ', response.status)
		
	print(attendancecontent)
		
	response, logoutcontent = http.request(URL + '/logout', 'GET', headers=headers, body=body)
	if(DEBUG):
		print(logoutcontent)
	else:
		print("Username or Password may be wrong!")
		if(DEBUG):
			print('Response Status - ', response.status)

    return """
    
    """.format(time=the_time)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
