from flask import Flask, redirect, render_template, request
from accountForm import AccountForm, create_request
from config import config
import sqlite3
import urllib.parse

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = config.web.secret_key


def url_encode(s: str) -> str:
    return urllib.parse.quote(s, safe='')


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


@app.route('/review/<request_id>')
def review(request_id):
    # TODO authenticate
    with sqlite3.connect(config.db.db_file) as conn:
        cur = conn.execute(
            'SELECT created_at, first_name, last_name, net_id, student_id, lcc, reason FROM active_requests WHERE id = ?',
            request_id
        )
        request = cur.fetchone()
        cur = cur.execute('SELECT COUNT(*) FROM active_requests')
        n_remaining = cur.fetchone()

    return render_template('review.html', n_remaining=n_remaining, request=request)


@app.route('/review/<request_id>/submit', methods=['POST'])
def submit_review(request_id):
    '''
    Body should be form encoded with "approved" bool parameter
    '''
    # TODO authenticate
    # TODO delete review from active_requests and create one in reviewed_requests
    # TODO if approved, create lab account
    # TODO redirect to confirm page
    return ''


@app.route('/confirm/<request_id>')
def confirm_review(request_id):
    '''
    Expects 'next_request_id' query parameter
    '''
    next_request_id = request.args.get('next_request_id')
    # TODO authenticate
    with sqlite3.connect(config.db.db_file) as conn:
        cur = conn.execute(
            'SELECT first_name, last_name, net_id, temporary_password, approved FROM reviewed_requests WHERE id = ?',
            request_id
        )
        request = cur.fetchone()
        first_name = request[0]
        last_name = request[1]
        net_id = request[2]
        temporary_password = request[3]
        approved = request[4]

    mail_template = config.mail.request_approved if approved else config.mail.request_denied
    mail_subject = url_encode(mail_template.subject_template)
    mail_body = url_encode(mail_template.body_template.format(
        first_name=first_name,
        last_name=last_name,
        net_id=net_id,
        temporary_password=temporary_password
    ))

    return render_template(
        'confirm_review.html',
        next_request_id=next_request_id,
        first_name=first_name,
        last_name=last_name,
        net_id=net_id,
        approved=approved,
        mailto_link=f'mailto:{url_encode(net_id)}?subject={mail_subject}&body={mail_body}'
    )


if __name__ == '__main__':
    app.run(debug=True)
