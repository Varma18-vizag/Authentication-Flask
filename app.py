from flask import Flask, request, jsonify
from supabase import create_client
import bcrypt
import jwt
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
SUPABASE_URL = "https://jmuxeilfjmzrxeiimjco.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptdXhlaWxmam16cnhlaWltamNvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEzNzc2OTksImV4cCI6MjA4Njk1MzY5OX0.yi5EuAYV1hNolmj1otlL27A1cosJW_PUduFNsACVyHk"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
JWT_SECRET = "MY_SECRET_KEY"
EMAIL_USER = "userotpauth@gmail.com"
EMAIL_PASS = "focawtqddoxdpnat"

# REGISTER

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        name = data.get("name")
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

        if not all([name, username, password, email]):
            return jsonify({"message": "Some fields are empty"}), 401

        # Check existing user
        existing = supabase.table("secure-auth") \
            .select("*") \
            .or_(f'username.eq.{username},email.eq.{email}') \
            .execute()

        if existing.data:
            return jsonify({"message": "Username or Email Already Exists"}), 409

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        supabase.table("secure-auth").insert({
            "name": name,
            "username": username,
            "password": hashed_pw,
            "email": email
        }).execute()

        return jsonify({"message": "User Registered Successfully"}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# LOGIN

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        result = supabase.table("secure-auth") \
            .select("*") \
            .eq("username", username) \
            .execute()

        if not result.data:
            return jsonify({
                "message": "Username does not exist"
            }), 409

        user = result.data[0]

        if bcrypt.checkpw(password.encode(), user["password"].encode()):
            token = jwt.encode({"username": username}, JWT_SECRET, algorithm="HS256")
            return jsonify({"jwtToken": token}), 200
        else:
            return jsonify({"message": "Password is incorrect"}), 401

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# CHECK BEFORE UPDATE


@app.route("/checkbeforeupdate", methods=["POST"])
def check_before_update():
    try:
        data = request.json
        name = data.get("name")
        username = data.get("username")
        email = data.get("email")

        result = supabase.table("secure-auth") \
            .select("name,username,email") \
            .eq("name", name) \
            .eq("username", username) \
            .eq("email", email) \
            .execute()

        if not result.data:
            return jsonify({
                "message": "Unauthorized user"
            }), 401

        return jsonify({
            "user data": [{
                "username": username,
                "email": email
            }]
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# OTP GENERATE

@app.route("/otpgenerate", methods=["POST"])
def generate_otp():
    try:
        data = request.json
        username = data.get("username")
        email = data.get("email")

        otp = str(random.randint(10000, 99999))

        # Send Email
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = email
        msg["Subject"] = "Your Secure-auth OTP"
        msg.attach(MIMEText(otp, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        hashed_otp = bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()

        supabase.table("Otp-auth").insert({
            "username": username,
            "email": email,
            "otp": hashed_otp
        }).execute()

        return jsonify({
            "username": username,
            "email": email
        }), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# OTP VERIFY


@app.route("/otpverify", methods=["POST"])
def verify_otp():
    try:
        data = request.json
        username = data.get("username")
        email = data.get("email")
        otp = data.get("otp")

        result = supabase.table("Otp-auth") \
            .select("otp") \
            .eq("username", username) \
            .eq("email", email) \
            .execute()

        if not result.data:
            return jsonify({"message": "OTP not found"}), 404

        stored_otp = result.data[0]["otp"]

        if bcrypt.checkpw(otp.encode(), stored_otp.encode()):
            return jsonify({
                "username": username,
                "email": email,
                "isVerified": True
            }), 200
        else:
            return jsonify({
                "message": "OTP verification error",
                "isVerified": False
            }), 401

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# DELETE OTP
@app.route("/deleteOtpApi", methods=["DELETE"])
def delete_otp():
    try:
        data = request.json
        username = data.get("username")
        email = data.get("email")

        supabase.table("Otp-auth") \
            .delete() \
            .eq("username", username) \
            .eq("email", email) \
            .execute()

        return jsonify({
            "message": "User OTP deleted"
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# CHANGE PASSWORD

@app.route("/changethepassword", methods=["PUT"])
def change_password():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        supabase.table("secure-auth") \
            .update({"password": hashed_pw}) \
            .eq("username", username) \
            .execute()

        return jsonify({"message": "Successful"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=3000)