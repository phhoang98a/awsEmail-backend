from flask import Flask, request
from get_comments import extract_email
from flask_cors import CORS
import boto3
import requests
from decouple import config
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

s3 = boto3.client(
  "s3",
  aws_access_key_id=os.environ.get('AMAZON_ACCESS_KEY'),
  aws_secret_access_key=os.environ.get('AMAZON_SECRET_KEY')
)


@app.route('/extract-email', methods=['POST', 'GET'])
def extractMail():
  if request.method == 'POST':
      body = request.json
      print(body)
      link = body['postLink']
      emails = extract_email(link)
      return ({
          "status": 200,
          "emails": emails
      })


@app.route('/send-email', methods=['POST', 'GET'])
def sendMail():
  if request.method == 'POST':
      files = request.files
      body = request.form.to_dict(flat=False)
      contentMail = body['content'][0]
      emails = body['emails']
      sender = body['sender'][0]
      subject = body['subject'][0]
      files = files.to_dict(flat=False)
      filesName = []
      if len(files) > 0:
          files = files['files']
          for file in files:
              file.filename = secure_filename(file.filename)
              filesName.append(file.filename)
              s3.upload_fileobj(
                  file,
                  os.environ.get('S3_BUCKET_NAME'),
                  file.filename,
                  ExtraArgs={
                      "ContentType": file.content_type
                  }
              )
      response = requests.post('https://6d5qn4knee.execute-api.us-east-2.amazonaws.com/prod/send-email',
                                json={'filenames': filesName, 'content': contentMail, 'emails':  emails, 'sender': sender, 'subject': subject})
      response = response.json()
      if (response['statusCode'] == 200):
          return ({
              "statusCode": 200,
              "msg": "Emails were sent successfully"
          })
      else:
          return ({
              "statusCode": 400,
              "msg": "Emails were not sent"
          })

if __name__ == '__main__':
    app.run()