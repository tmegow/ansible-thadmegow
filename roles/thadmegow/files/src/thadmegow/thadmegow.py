import os
import requests
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Mail, To, Content
from flask import Flask, render_template, request, redirect, abort

app = Flask(__name__)


def send_email(replyto_email, to_emails, content):
    """ Submits send_email jobs to SendGrid API
    """
    from_email = Email("website-submission@em5812.thadmegow.net")
    to_emails = To("tmegow@gmail.com")
    subject = "Website message from: " + replyto_email
    content = Content("text/plain", content)
    message = Mail(from_email, to_emails, subject, content)
    message.reply_to = replyto_email
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        return render_template('50x.html')


def is_human(captcha_response):
    """ Validating recaptcha response from google server
        Returns True captcha test passed for submitted form else returns False.
    """
    secret = os.environ.get('RECAPTCHA_SECRET')
    payload = {'response': captcha_response, 'secret': secret}
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']


@ app.route('/')
def index():
    return render_template('index.html')


@ app.route('/sendemail', methods=["POST"])
def sendmail():
    recaptcha_response = request.form.get('g-recaptcha-response')
    if is_human(recaptcha_response):
        send_email(request.form.get('email'), "tmegow@gmail.com",
                   request.form.get('message'))
        return render_template('thankyou.html')
    else:
        abort(403, "Bots not allowed!")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
