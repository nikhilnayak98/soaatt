import json
import base64
import getpass
import httplib2

from flask import Flask, request, render_template
app = Flask(__name__)

http = httplib2.Http()

# endpoint parameters
URL = 'http://111.93.164.202:8282/CampusPortalSOA'
reglov = 'ITERRETD1711A0000002'
membertype = 's'
headers = 0
body = 0

@app.route('/')
def my_form():
	return render_template('login.html', msghandler=0)
	
@app.route('/logout')
def logout():
	response, logoutcontent = http.request(URL + '/logout', 'GET', headers=headers, body=body)
	return render_template('login.html', msghandler=2)

@app.route('/home', methods=['POST'])
def homepage():
	
	# global var
	global headers
	global body

	username = request.form['username']
	password = request.form['password']

	body = json.dumps({'username':username,'password':password,'MemberType':membertype})

	headers = {'Content-type': 'application/json'}
	response, logincontent = http.request(URL + '/login', 'POST', headers=headers, body=body)
		
	if(len(logincontent) > 112):
		logindata = json.loads(logincontent)
		name = logindata["name"].lower().title()
		body = json.dumps({'registerationid':reglov})

		headers = {'Cookie': response['set-cookie']}
		response, attendancecontent = http.request(URL + '/attendanceinfo', 'POST', headers=headers, body=body)
		
		resp, image = http.request(URL + '/image/studentPhoto', 'GET', headers=headers)
		image = str(base64.b64encode(image).decode("utf-8"))
		
		data = json.loads(attendancecontent)
		jsondata = json.dumps(data["griddata"], sort_keys=True, indent=4)
		
		return render_template('attendance.html', data=data["griddata"], jsondata=jsondata, name=name, image=image)
	else:
		error = 1
		return render_template('login.html', msghandler=error)

if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)
