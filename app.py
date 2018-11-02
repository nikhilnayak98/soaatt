import json, base64, httplib2, requests, re
import flask_monitoringdashboard as dashboard
from bs4 import BeautifulSoup
from flask import Flask, request, render_template, make_response, redirect, url_for

app = Flask(__name__)

http = httplib2.Http()
dashboard.bind(app)

# endpoint parameters
URL = 'http://111.93.164.90:8282/CampusPortalSOA'
# default reglov
reglov = 'ITERRETD1711A0000002'
membertype = 'S'
headers = 0
body = 0
data_not_available = "Data for current semester is not available on the server yet."


@app.route('/')
def my_form():
    return render_template('login.html', msghandler=0)


@app.route('/logout')
def logout():
    try:
        response, logoutcontent = http.request(URL + '/logout', 'POST', headers=headers, body=body)
        return redirect(url_for('my_form'))
    except AttributeError:
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

    try:
        # get exam type id
        response, examtype = http.request(URL + '/examtype', 'POST', headers=headers, body=body)
        examtype = json.loads(examtype)
        exam = examtype["studentdata"][0]["EXAMTYPEID"]

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
    except KeyError:
        return data_not_available
    except AttributeError:
        return "Refresh this web page"


@app.route('/details')
def details():
    pass


@app.route('/home', methods=['POST'])
def homepage():
    # global var
    global headers
    global body
    global reglov

    username = request.form['username']
    password = request.form['password']

    body = json.dumps({'username':username,'password':password,'MemberType':membertype})

    headers = {'Content-type': 'application/json'}
    response, logincontent = http.request(URL + '/login', 'POST', headers=headers, body=body)

    if(len(logincontent) > 112):
        logindata = json.loads(logincontent)
        name = logindata["name"].lower().title()

        headers = {'Cookie': response['set-cookie']}

        # get current sem id
        resp, semcontent = http.request(URL + '/studentSemester/lov', 'POST', headers=headers, body="")
        semcontent = json.loads(semcontent)
        reglov = semcontent['studentdata'][0]['REGISTRATIONID']

        body = json.dumps({'registerationid': reglov})

        response, attendancecontent = http.request(URL + '/attendanceinfo', 'POST', headers=headers, body=body)

        resp, image = http.request(URL + '/image/studentPhoto', 'GET', headers=headers)
        image = str(base64.b64encode(image).decode("utf-8"))

        data = json.loads(attendancecontent)
        try:
            jsondata = json.dumps(data["griddata"], sort_keys=True, indent=4)
            return render_template('attendance.html', data=data["griddata"], jsondata=jsondata, name=name, image=image)
        except KeyError:
            return render_template('attendance_null.html',
                                   data=data_not_available,
                                   jsondata=data,
                                   name=name,
                                   image=image)
    else:
        error = 1
        return render_template('login.html', msghandler=error)


def check_ip(address):
    prog = re.compile(
        '^http[s]?:\/\/((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])')
    if prog.match(address):
        return True
    else:
        return False


# scrape portal address from the website
'''
r = requests.get('http://www.soa.ac.in/iter')
soup = BeautifulSoup(r.text, "html.parser")
for link in soup.find_all('a'):
    if check_ip(link.get('href')) is True:
        URL = str(link.get('href'))
        if URL.endswith('index#/'):
            URL = URL[:-8]
        break
'''

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
