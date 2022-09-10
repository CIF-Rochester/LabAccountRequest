/*
This lambda function expects to be called from a function URL. If it is not, it
will complain about missing parameters, probably. Just use a function URL.

Expected request:

```
POST
Content-Type: application/JSON

{
  "to": ["list of email addresses to send to"],
  "from": "email address in from line",
  "subject": "subject line here",
  "message": "email body here"
}
```
*/

const { SendEmailCommand, SESClient } = require('@aws-sdk/client-ses');

const sesClient = new SESClient({ region: 'us-east-2' });

function createSendEmailCommand(toAddresses, fromAddress, subjectText, messageText) {
  return new SendEmailCommand({
    Destination: {
      CcAddresses: [],
      ToAddresses: toAddresses,
    },
    Message: {
      Subject: {
        Charset: "UTF-8",
        Data: subjectText,
      },
      Body: {
        Text: {
          Charset: "UTF-8",
          Data: messageText,
        }
      }
    },
    Source: fromAddress,
  })
}

function error400(code, message, details = undefined) {
  return {
    statusCode: 400,
    body: JSON.stringify({ success: false, code, message, details }),
  };
}

exports.handler = async (event) => {
  // Check headers
  if (event.http.method !== "POST") {
    return {
      statusCode: 405,
      body: JSON.stringify({ success: false }),
    };
  }
  if (event.headers['Content-Type'] !== 'application/json') {
    return {
      statusCode: 415,
      body: JSON.stringify({ success: false }),
    };
  }

  // Parse body JSON
  const bodyText = event.body;
  let body = undefined;
  try {
    body = JSON.parse(bodyText);
  } catch (e) {
    return error400(1, 'Malformed JSON', e.message);
  }

  // Validate body contents
  if (!Array.isArray(body.to)) {
    return error400(2, 'Invalid body', '"to" should be an array of email addresses');
  }
  const toAddresses = body.to;

  if (!(typeof body.from === 'string')) {
    return error400(2, 'Invalid body', '"from" should be an email address');
  }
  const fromAddress = body.from;

  if (!(typeof body.subject === 'string')) {
    return error400(2, 'Invalid body', '"subject" should be a string');
  }
  const subjectText = body.subject;

  if (!(typeof body.message === 'string')) {
    return error400(2, 'Invalid body', '"message" should be a string');
  }
  const messageText = body.message;

  const cmd = createSendEmailCommand(toAddresses, fromAddress, subjectText, messageText);
  try {
    await sesClient.send(cmd);
    return {
      statusCode: 200,
      body: JSON.stringify({ success: true, message: 'Email sent' }),
    };
  } catch (e) {
    return {
      statusCode: 500,
      body: JSON.stringify({ success: false, message: e }),
    };
  }
};
