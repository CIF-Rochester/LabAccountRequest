from flask import Flask, redirect, render_template
from accountForm import AccountForm, create_request
from config import config
import sqlite3

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = config.web.secret_key


@app.route('/', methods=['GET', 'POST'])
def index():
    form = AccountForm()
    if form.validate_on_submit():
        with sqlite3.connect(config.db.db_file) as conn:
            create_request(conn, form)
        return redirect('/success')
    return render_template('index.html', form=form)


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/requests')
def requests():
    with sqlite3.connect(config.db.db_file) as conn:
        cur = conn.execute('SELECT * FROM active_requests')
        requests = cur.fetchall()
    return render_template('requests.html', requests=requests)


if __name__ == '__main__':
    app.run(debug=True)
