from flask import render_template, request, redirect, url_for
from FlaredUI.App import app

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login form submission here (verify credentials)
        # If successful, login_user(...)
        return redirect(url_for('index'))  # Or the desired page after login
    return render_template('login.html')