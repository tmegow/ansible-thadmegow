import os
import requests
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Mail, To, Content
from flask import Flask, render_template, request, redirect, abort
from google.cloud import recaptchaenterprise_v1
from google.cloud.recaptchaenterprise_v1 import Assessment, Event


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
    # payload = {'response': captcha_response, 'secret': secret}
    # response = requests.post(
    #         "https://recaptchaenterprise.googleapis.com", payload)
    # project_name = f"projects/215 NE Blvd Home Security"
    # event = Event(site_key="6LcA6hwaAAAAAEEkE37mE5h1FphvYOeif8fj8x3t", token=secret, user_ip_address=request.remote_addr)
    # assessment = Assessment(event=event)
    project = os.environ.get('RECAPTCHA_PROJECT')
    secret = os.environ.get('RECAPTCHA_SECRET')
    return create_assessment(project_id=f"projects/215 NE Blvd Home Security", recaptcha_site_key=secret, token=captcha_response, user_ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent'), recaptcha_action="LOGIN")
    # rrequest = recaptchaenterprise_v1.CreateAssessmentRequest(parent=project_name, assessment=assessment)
    # return client.create_assessment(request=rrequest)
    # response_text = json.loads(response.text)
    # return response_text['success']


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



def create_assessment(
    project_id: str,
    recaptcha_site_key: str,
    token: str,
    recaptcha_action: str,
    user_ip_address: str,
    user_agent: str,
    #ja3: str,
) -> Assessment:
    """Create an assessment to analyze the risk of a UI action.
    Args:
        project_id: GCloud Project ID
        recaptcha_site_key: Site key obtained by registering a domain/app to use recaptcha services.
        token: The token obtained from the client on passing the recaptchaSiteKey.
        recaptcha_action: Action name corresponding to the token.
        user_ip_address: IP address of the user sending a request.
        user_agent: User agent is included in the HTTP request in the request header.
        ja3: JA3 associated with the request.
    """

    client = recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient()

    # Set the properties of the event to be tracked.
    event = recaptchaenterprise_v1.Event()
    event.site_key = recaptcha_site_key
    event.token = token
    event.user_ip_address = user_ip_address
    event.user_agent = user_agent
    #event.ja3 = ja3

    assessment = recaptchaenterprise_v1.Assessment()
    assessment.event = event

    project_name = f"projects/{project_id}"

    # Build the assessment request.
    request = recaptchaenterprise_v1.CreateAssessmentRequest()
    request.assessment = assessment
    request.parent = project_name

    response = client.create_assessment(request)

    # Check if the token is valid.
    if not response.token_properties.valid:
        print(
            "The CreateAssessment call failed because the token was "
            + "invalid for for the following reasons: "
            + str(response.token_properties.invalid_reason)
        )
        return

    # Check if the expected action was executed.
    if response.token_properties.action != recaptcha_action:
        print(
            "The action attribute in your reCAPTCHA tag does"
            + "not match the action you are expecting to score"
        )
        return
    else:
        # Get the risk score and the reason(s)
        # For more information on interpreting the assessment,
        # see: https://cloud.google.com/recaptcha-enterprise/docs/interpret-assessment
        for reason in response.risk_analysis.reasons:
            print(reason)
        print(
            "The reCAPTCHA score for this token is: "
            + str(response.risk_analysis.score)
        )
        # Get the assessment name (id). Use this to annotate the assessment.
        assessment_name = client.parse_assessment_path(response.name).get("assessment")
        print(f"Assessment name: {assessment_name}")
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0')
