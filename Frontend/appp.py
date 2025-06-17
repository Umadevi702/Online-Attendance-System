from flask import Flask, render_template, request, redirect
import urllib3

app = Flask(__name__)
http = urllib3.PoolManager()

@app.route('/')
def home():
    return render_template("index2.html")

@app.route('/signupform', methods=['POST'])
def signupform():
    username = request.form['username']
    password = request.form['password']
    url = f'http://127.0.0.1:3000/signup?username={username}&password={password}'
    response = http.request('GET', url)
    if response.status == 200 and b'success' in response.data.lower():
        return render_template("index2.html", res="Signup successful. Please log in.")
    else:
        return render_template("index2.html", err="Signup failed. Try again.")

@app.route('/loginform', methods=['POST'])
def loginform():
    username = request.form['username1']
    password = request.form['password1']
    url = f'http://127.0.0.1:3000/login?username={username}&password={password}'
    response = http.request('GET', url)
    if response.status == 200 and b'success' in response.data.lower():
        # ✅ Render the storeattendance page with the username
        return render_template("storeAttendence.html", username=username)
    else:
        return render_template("index2.html", err="Login failed. Invalid credentials.")

if __name__ == '__main__':
    app.run(debug=True)
