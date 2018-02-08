import sys
import json
import getpass
import httplib2
from flask import Flask, request, render_template
app = Flask(__name__)

http = httplib2.Http()

# endpoint parameters
URL = 'http://111.93.164.203/CampusPortalSOA'
reglov = 'ITERRETD1711A0000002'
membertype = 's'
headers = 0
body = 0

@app.route('/')
def my_form():
	return render_template('login.html', msghandler=0)

@app.route('/', methods=['POST'])
def homepage():
	
	# global var
	global headers
	global body
	
	# html content
	htmlcontent = '<html> <head> <title>Attendance Info</title><meta name="viewport" content="width=device-width, initial-scale=1"><link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"> <link type="text/css" rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.97.5/css/materialize.min.css" media="screen,projection"/> <meta name="viewport" content="width=device-width, initial-scale=1.0"/> </head> <body>'
	
	# html footer
	htmlfooter = '</table><script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.2.1/jquery.min.js"></script> <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.97.5/js/materialize.min.js"></script> </body> </html>'

	username = request.form['username']
	password = request.form['password']

	body = json.dumps({'username':username,'password':password,'MemberType':membertype})

	headers = {'Content-type': 'application/json'}
	response, logincontent = http.request(URL + '/login', 'POST', headers=headers, body=body)
		
	if(len(logincontent) > 112):
		print('Login Successful!')
		
		logindata = json.loads(logincontent)
		
		# html body
		htmlbody = '<h3>Hello ' + logindata["name"].lower().title() + '!</h3><br>'
		htmlbody += '<img src="' + URL + '/image/studentPhoto'  + '"></img>'
	
		body = json.dumps({'registerationid':reglov})

		headers = {'Cookie': response['set-cookie']}
		response, attendancecontent = http.request(URL + '/attendanceinfo', 'POST', headers=headers, body=body)
	
		data = json.loads(attendancecontent)
		data_size = len(data["griddata"])
		
		htmlbody += '<center><div class="z-depth-1 grey lighten-4 row" style="display: inline-block; padding: 32px 48px 0px 48px; border: 1px solid #EEE;">'
		htmlbody += '<table class="bordered"> <tr> <th>Subject</th> <th>Theory</th> <th>Lab</th> <th>Attendance</th> <th>Last updated on</th> </tr>'
		
		for i in range(0, data_size): 
			htmlbody += '<tr><td>' + data["griddata"][i]["subject"] + '</td><td>' + data["griddata"][i]["Latt"] + '</td><td>' + data["griddata"][i]["Patt"] + '</td><td>' + str(data["griddata"][i]["TotalAttandence"]) + '%</td>' + '<td>' + data["griddata"][i]["lastupdatedon"] + '</td></tr>'
		
		htmlbody += '</table></div></center>'
		
		htmlcontent += htmlbody + htmlfooter
		
		# response, logoutcontent = http.request(URL + '/logout', 'GET', headers=headers, body=body)
		
		return (htmlcontent)
	else:
		error = 1
		return render_template('login.html', msghandler=error)

if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)
