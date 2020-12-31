import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Mail, To, Content
from flask import Flask, render_template, request, redirect

app = Flask(__name__)


def send_email(replyto_email, to_emails, content):
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
        print(e.message)


@ app.route('/')
def index():
    return render_template('index.html')


@ app.route('/sendemail', methods=["POST"])
def sendmail():
    print("form_subject: {}\n form_message: {}\n".format(
        request.form.get('email'), request.form.get('message')))
    send_email(request.form.get('email'), "tmegow@gmail.com",
               request.form.get('message'))
    return render_template('thankyou.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
