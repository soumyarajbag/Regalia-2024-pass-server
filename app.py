from flask import Flask, request, jsonify
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from dotenv import load_dotenv
import os
import io
from PIL import Image, ImageDraw, ImageFont
import requests
import pyqrcode
import json
from pass_gen import pass_gen

app = Flask(__name__)
load_dotenv()

# Set up the email parameters
sender = "rcciit.regalia.official@gmail.com"
subject = "Regalia 2024 - Pass Details"
template = Image.open("pass_template.png")
detailsFont = ImageFont.truetype("Poppins-Regular.ttf", 40)
allowedFont = ImageFont.truetype("Poppins-SemiBold.ttf", 40)

app_password = os.getenv("APP_PASSWORD")
sender_email = os.getenv("SENDER_EMAIL")

def makeQR(data):
    qr = pyqrcode.create(data)
    qr.png('qr_code.png', scale=10, module_color='#151515', background='#ffc82f')
    return qr.get_png_size(12)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Regalia 2024 Pass Generator"}), 200

@app.route('/generate-pass', methods=['POST'])
def generate_pass():
    try:
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        roll = data.get('roll')

        # Add data to the QR code
        qr_data = json.dumps({"name": name, "phone": phone, "email": email, "roll": roll})
        cert = template.copy().convert("RGBA")  # Convert to RGBA
        draw = ImageDraw.Draw(cert)

        # Generate and paste the QR code
        size = makeQR(qr_data)
        pos = ((600 - int(size / 2)), 50)
        qr_code_image = Image.open('qr_code.png').convert("RGBA")  # Convert to RGBA
        cert.paste(qr_code_image, pos, qr_code_image)  # Use the image as a mask for transparency

        # Draw the name
        max_width = 1242  # Adjust this according to your template and requirements
        nameFont = 150
        text_width = draw.textlength(name.upper(), ImageFont.truetype("Poppins-Bold.ttf", nameFont))
        difference = text_width - max_width

        # Adjust font size based on text width
        if difference <= 0:
            nameFont = 60
        elif 0 < difference <= max_width * 0.1:
            nameFont = 70
        elif max_width * 0.1 < difference <= max_width * 0.2:
            nameFont = 55
        elif max_width * 0.2 < difference <= max_width * 0.3:
            nameFont = 45
        elif difference > max_width * 0.3:
            nameFont = 45

        draw.text(xy=(180, 850), text=name.upper(), fill='black', font=ImageFont.truetype("Poppins-Bold.ttf", nameFont))
        draw.text(xy=(180, 950), text=roll, fill='black', font=detailsFont)
        draw.text(xy=(180, 1020), text=phone.upper(), fill='black', font=detailsFont)

        # Save image to buffer
        img_buffer = io.BytesIO()
        cert.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Upload image to Imgur
        url = "https://api.imgur.com/3/image"
        headers = {
            'Authorization': f'Client-ID {os.getenv("IMGUR_CLIENT_ID")}'  # Replace with your actual Imgur client ID
        }
        files = {
            'image': ('pass_qr.png', img_buffer, 'image/png')
        }
        response = requests.post(url, headers=headers, files=files)

        # Ensure successful upload
        if response.status_code == 200:
            imgur_data = response.json()
            imgur_link = imgur_data['data']['link']

            # Create email message
            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = email
            msg["Subject"] = name.upper() + ' - ' + subject

            # Attach email content and QR code image from Imgur
            msg.attach(MIMEText(pass_gen(name, phone, roll), "html"))

            # Reset buffer position and attach QR code image
            img_buffer.seek(0)
            msg.attach(MIMEImage(img_buffer.read(), name="pass_qr.png"))

            # Log in to the SMTP server and send the email
            server = smtplib.SMTP(sender_email, 587)
            server.starttls()
            server.login(sender, app_password)
            server.sendmail(sender, email, msg.as_string())
            server.quit()

            return jsonify({
                "message": "Pass generated, uploaded to Imgur, and email sent successfully",
                "imgur_response": imgur_data,
                "status_code": 200
            }), 200
        else:
            return jsonify({
                "message": "Failed to upload image to Imgur",
                "error": response.text,
                "status_code": response.status_code
            }), 500

    except Exception as e:
        return jsonify({"message": "Failed to generate pass or send email", "error": str(e)}), 500
    
@app.route('/gen-pass', methods=['POST'])
def generate_png():
    try:
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        roll = data.get('roll')

        # Add data to the QR code
        qr_data = json.dumps({"name": name, "phone": phone, "email": email, "roll": roll})
        cert = template.copy().convert("RGBA")  # Convert to RGBA
        draw = ImageDraw.Draw(cert)

        # Generate and paste the QR code
        size = makeQR(qr_data)
        pos = ((600 - int(size / 2)), 50)
        qr_code_image = Image.open('qr_code.png').convert("RGBA")  # Convert to RGBA
        cert.paste(qr_code_image, pos, qr_code_image)  # Use the image as a mask for transparency

        # Draw the name
        max_width = 1242  # Adjust this according to your template and requirements
        nameFont = 150
        text_width = draw.textlength(name.upper(), ImageFont.truetype("Poppins-Bold.ttf", nameFont))
        difference = text_width - max_width

        # Adjust font size based on text width
        if difference <= 0:
            nameFont = 60
        elif 0 < difference <= max_width * 0.1:
            nameFont = 70
        elif max_width * 0.1 < difference <= max_width * 0.2:
            nameFont = 55
        elif max_width * 0.2 < difference <= max_width * 0.3:
            nameFont = 45
        elif difference > max_width * 0.3:
            nameFont = 45

        draw.text(xy=(180, 850), text=name.upper(), fill='black', font=ImageFont.truetype("Poppins-Bold.ttf", nameFont))
        draw.text(xy=(180, 950), text=roll, fill='black', font=detailsFont)
        draw.text(xy=(180, 1020), text=phone.upper(), fill='black', font=detailsFont)

        # Save image to buffer
        img_buffer = io.BytesIO()
        cert.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Upload image to Imgur
        url = "https://api.imgur.com/3/image"
        headers = {
            'Authorization': f'Client-ID {os.getenv("IMGUR_CLIENT_ID")}'
        }
        files = {
            'image': ('pass_qr.png', img_buffer, 'image/png')
        }
        response = requests.post(url, headers=headers, files=files)

        # Ensure successful upload
        if response.status_code == 200:
            imgur_data = response.json()
            return jsonify({
                "imgur_response": imgur_data,
                "status_code": 200
            }), 200
        else:
            return jsonify({
                "message": "Failed to upload image to Imgur",
                "error": response.text,
                "status_code": response.status_code
            }), 500

    except Exception as e:
        return jsonify({"message": "Failed to generate PNG or upload to Imgur", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
