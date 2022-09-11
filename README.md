# Lab Account Request

A simple web-form to request the creation of a lab account.

Features:
- [ ] Request a lab account
- [ ] Trusted lab accounts cany approve or deny requests
- [ ] Email notifications of new requests sent to tech director emails
- [ ] Audit log for actions
- [ ] Form for lab account holders to update their card info
- [ ] Email verification for lab account requests
  - Blocked on restrictions from SES sandbox
- [ ] ReCaptcha for spam prevention

## Development

First, follow the [AWS Configuration Steps](#AWS_Configuration) in a test AWS
account (or production: this is CIF, does it really matter?).

To set up the project for development:

1. Create a venv:

    Install python3 venv according to your platforms instructions. Create the
    venv with `python3 -m venv .venv`

2. Activate it with `source .venv/bin/activate`. If you are not using bash,
    look for instructions for your platform.

3. Install dependencies with `pip3 -r requirements.txt`

4. Create and configure a `config.toml` file:
    
    `cp config.example.toml config.toml` and add the development settings. You
    will need to edit:

    - aws.access_key
    - aws.secret_key
    - aws.sendmail_url
    - web.secret_key
    - mail.*.to_addresses
    - mail.*.from_address

    Feel free to edit other settings. And remember, **never commit config.toml**.

5. Initialize the database with `python3 init_db.py`. You can run this again
    to clear the data in the database and possibly update the database schema.

6. Start the development server with `python3 main.py`. It automatically 
    restarts when you change any python file.

## Deploying

### AWS Configuration

Create an AWS account. This service will stay well within the free tier of the
resources it uses.

#### SES Configuration

First, configure AWS's Simple Email Service (SES). Verify a domain that emails
will be sent from (i.e. `cif.rochester.edu`). Choose Easy-DKIM verification and
create the CNAME records that it requests for the domain.

Next, verify receiving emails. To do this, go to Amazon SES > Verified 
Identities and click Create Identity. Follow the steps to verify an email
identity. Repeat for each email you want to receive mail on.

#### Lambda Configuration

Create a new function called `cifSendMail` with runtime `Node.js 16.x` and
architecture `x86_64`. Expand `Advanced Settings` and check
`Enable function URL` and ensure Auth type is set to `AWS_IAM`.

Go to `lambda/cifSendMail` and run `npm install` to install dependencies.
Create a zip archive of the function with `zip -r cifSendMail.zip .`. In the 
lambda function interface, choose `Upload from .zip file` and find the archive 
you just created.

Now, go to the IAM management console > Policies. Create a JSON policy with
the following content:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*"
        }
    ]
}
```

Give it the name `SESSEndEmail`.

Navigate to the Roles tab in the IAM console and click the role starting with
`cifSendMail` that was automatically created when you made the Lambda function.
Click Add Permissions > Attach policies and find the SESSendEmail policy you
just created.

#### Testing the AWS Configuration

To test that the set-up worked, go back to the lambda function and go to the
Test tab and create a new test event with the JSON:

```json
{
  "http": {
    "method": "POST"
  },
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"to\": [\"TOADDRESS\"], \"from\": \"FROMADDRESS\", \"subject\": \"Test email\", \"message\": \"Hello world\"}"
}
```

Make sure to replace `TOADDRESS` with one of the email addresses you verified
while setting up SES and `FROMADDRESS` with any address ending in
`@DOMAIN.com`, where `DOMAIN.com` is the domain you verified in SES. Create it
and click `Test`. It should give a success response and an email should be
received at the `TOADDRESS`.

If you followed all these steps and it didn't work, good luck!

### Deploying the web application

TODO

#### Updating the database schema in production

Create a `migrate-NAME-DATE.sql` file with commands to migrate the old schema
into the new format. Preserving data is important. Then run the commands in the
file. You should commit the migration script and archive the pre-migration
database somewhere (TODO: describe this process better).

## Architecture

Planned architecture:
- SQLite database
- Flask/python backend
- Amazon AWS Lambda function to call Amazon AWS SES for sending emails
  - Why: SES free tier allows 62k emails/month when called from a Lambda
    function or EC2 instance. Lambda allows 1M reqs and 400k GB-seconds/month
    of compute. So we can easily get up to 62k emails/month for free.

    Note: Each receiving address on an email corresponds to 1 email against the
    quota. I.e. sending the email to 4 addresses counts as 4 emails. Make sure
    to include this fact in quota calculations in app.
- Plain HTML front end

### Spam Protection

This form will be visible to any device on a UoR network, so it is possible
someone will try to spam our form. Since we have a limit of 62k emails per
month, we can't go over that. Realistically, we don't want more than 1 email per
legitimate account request.

As a baseline, we'll have a batch process that checks for new requests every
1 hour (TODO: what time to actually use?) that will send a single email
containing:

- The number of account requests made since the last notification
- A link to a page where all unprocessed (not marked approved or denied) 
  account requests can be reviewed.

Additionally, if more than X (TOOD: what number for X) requests are made since
the last notification, the requests will be moved into a new temporary DB table
and an email notification will be sent for a tech director to review the
suspicious requests.
