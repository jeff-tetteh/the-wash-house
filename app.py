from flask import Flask, render_template, request
import random
import string
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        weight = float(request.form["weight"])
        price = weight * 5  # ₵5 per kg

        # Generate tracking code
        tracking_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Save booking info
        with open("bookings.txt", "a") as file:
            file.write(f"{tracking_code},{name},{phone},{weight},{price},In progress\n")

        # Send confirmation SMS
        try:
            account_sid = os.getenv("TWILIO_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

            client = Client(account_sid, auth_token)

            message_body = (
                f"Hi {name}, your booking at The Wash House was successful.\n"
                f"Total: ₵{price:.2f}\n"
                f"Tracking Code: {tracking_code}\n"
                f"Thank you for choosing us!"
            )

            client.messages.create(
                body=message_body,
                from_=twilio_number,
                to=phone  # Make sure this is in E.164 format e.g. +233...
            )
        except Exception as e:
            print("Failed to send SMS:", e)

        return f"<h3>Thank you, {name}! Your total is ₵{price:.2f}.<br>Your tracking code is <b>{tracking_code}</b>.</h3>"

    return render_template("booking.html")

@app.route("/track", methods=["GET", "POST"])
def track():
    if request.method == "POST":
        code = request.form["code"].strip()
        with open("bookings.txt", "r") as file:
            for line in file:
                fields = line.strip().split(",")
                if fields[0] == code:
                    status = fields[5]
                    return render_template("track.html", status=status)
        return render_template("track.html", not_found=True)

    return render_template("track.html")

@app.route("/test-logo")
def test_logo():
    return '''
    <h2>Testing Logo</h2>
    <img src="/static/logo.jpg" alt="Test Logo" style="border: 2px solid blue; width: 200px;">
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81)

