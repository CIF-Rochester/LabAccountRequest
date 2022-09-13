from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Regexp
from sqlite3 import Connection


class AccountForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    net_id = StringField('Net ID', validators=[DataRequired()])
    student_id = StringField(
        'Student ID',
        validators=[DataRequired(), Regexp(
            r'\d{8}', message='Student ID should be 8 numbers')]
    )
    lcc = StringField(
        'LCC',
        validators=[DataRequired(), Regexp(
            r'\d{2}', message='LCC should be a 2 digit number')]
    )
    reason = TextAreaField(
        'Please briefly explain what you plan to use your account for.',
        validators=[DataRequired()]
    )


def create_request(conn: Connection, form: AccountForm):
    conn.execute(
        "INSERT INTO active_requests (first_name, last_name, net_id, student_id, lcc, reason) VALUES (?, ?, ?, ?, ?, ?)",
        (form.first_name.data, form.last_name.data, form.net_id.data,
         form.student_id.data, form.lcc.data, form.reason.data)
    )
    conn.commit()
