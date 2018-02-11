import json
import base64
import getpass
import httplib2

from flask import Flask, request, render_template, make_response, redirect, url_for
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
	# global var
	global headers
	global body
	
	response, logoutcontent = http.request(URL + '/logout', 'GET', headers=headers, body=body)
	return redirect(url_for('my_form'))
	
@app.route('/schedule')
def schedule():
	# global var
	global headers
	global body
	
	body = json.dumps({'regid':reglov})
	response, scheduledata = http.request(URL + '/timetable', 'POST', headers=headers, body=body)
	response = make_response(scheduledata)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = \
		'inline; filename=Schedule.pdf'
	return response

@app.route('/admitcard')
def get_pdf():
	# global var
	global headers
	global body
	
	# get course details
	response, course = http.request(URL + '/stdrst', 'POST', headers=headers, body='')
	course = json.loads(course)
	programdesc = course["info"][0]["programdesc"]
	branchdesc = course["info"][0]["branchdesc"]
	lateralentry = course["info"][0]["lateralentry"]
	name = course["info"][0]["name"]
	username = course["info"][0]["enrollmentno"]
	
	# get exam type id
	response, examtype = http.request(URL + '/examtype', 'POST', headers=headers, body=body)
	examtype = json.loads(examtype)
	exam = examtype["studentdata"][1]["EXAMTYPEID"]
	
	#get exam event id
	body = json.dumps({'examid':exam,'regid':reglov})
	response, examidi = http.request(URL + '/exameventtype', 'POST', headers=headers, body=body)
	exameventid = json.loads(examidi)
	exameventid = exameventid["studentdata"][0]["EXAMEVENTID"]
	
	# download file
	body = json.dumps({'examid':reglov,
						'regid':reglov,
						'exameventid':exameventid,
						'studentname':name,
						'enrollmentno':username,
						'programdesc': programdesc,
						'branchdesc':branchdesc,
						'lateralentry':lateralentry})
	
	response, studentdata = http.request(URL + '/downExameSchedulepdf', 'POST', headers=headers, body=body)
	response = make_response(studentdata)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = \
		'inline; filename=AdmitCard.pdf'
	return response

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
