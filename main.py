from flask import request, Flask, redirect, render_template, url_for
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
        req = cur.fetchone()
        cur = cur.execute('SELECT COUNT(*) FROM active_requests')
        n_remaining = cur.fetchone()

    return render_template('review.html', n_remaining=n_remaining, request=req, request_id=request_id)


@app.route('/review/<request_id>/submit', methods=['POST'])
def submit_review(request_id):
    '''
    Body should be form encoded with "approved" bool parameter
    '''
    # TODO authenticate

    approved = request.form.get('approved') == 'true'
    reviewed_by = 'admin'
    reviewer_ip = request.remote_addr
    temporary_password = 'cif314!'  # TODO generate random string

    with sqlite3.connect(config.db.db_file) as conn:
        # Select and delete the active_request
        cur = conn.execute(
            'SELECT created_at, first_name, last_name, net_id, student_id, lcc, reason FROM active_requests WHERE id = ?',
            (request_id,)
        )
        req = cur.fetchone()
        cur = cur.execute(
            'DELETE FROM active_requests WHERE id = ?', (request_id,))

        # Insert the reviewed_request and get its ID
        cur = cur.execute(
            'INSERT INTO reviewed_requests (created_at, reviewed_by, approved, temporary_password, first_name, last_name, net_id, student_id, lcc, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (req[0], reviewed_by, approved, temporary_password,
             req[1], req[2], req[3], req[4], req[5], req[6])
        )
        cur = cur.execute(
            'SELECT last_insert_rowid()'
        )
        reviewed_request_id = cur.fetchone()[0]

        # Add to audit log
        cur = cur.execute(
            'SELECT id FROM event_types WHERE event_name = ?', (
                'review_approve' if approved else 'review_deny',)
        )
        event_type_id = cur.fetchone()[0]
        cur = cur.execute(
            'INSERT INTO audit_log (actor, actor_ip, event_type, event_data) VALUES (?, ?, ?, ?)',
            (reviewed_by, reviewer_ip, event_type_id, '{}')
        )

        # Find ID for next active_request (if there is one)
        cur = cur.execute(
            'SELECT id FROM active_requests ORDER BY id LIMIT 1')
        next_request_id = cur.fetchmany()

        # Finish transaction
        conn.commit()

    # TODO if approved, create lab account

    url = url_for('confirm_review', request_id=reviewed_request_id)
    if len(next_request_id) > 0:
        url = url_for('confirm_review', request_id=reviewed_request_id,
                      next_request_id=next_request_id[0][0])

    return redirect(url)


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
            (request_id,)
        )
        req = cur.fetchone()
        first_name = req[0]
        last_name = req[1]
        net_id = req[2]
        temporary_password = req[3]
        approved = req[4]

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
