import boto3
from typing import Annotated
from fastapi import FastAPI, File, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()
rekognition_client = boto3.client('rekognition')

@app.get("/")
async def read_index():
  return FileResponse("static/index.html")

@app.post('/upload-image')
def upload_image(
  uploaded_photo_id: Annotated[bytes, File()], 
  uploaded_headshot: Annotated[bytes, File()]
):
  photo_id = {"Bytes": uploaded_photo_id}
  # Validate to make sure there's exactly one face in the uploaded photo_id
  detect_faces_result = rekognition_client.detect_faces(Image=photo_id)
  if len(detect_faces_result['FaceDetails']) > 1:
    raise HTTPException(status_code=422, detail="It seems the photo ID contains more than one face or no faces at all. Please upload a photo ID with exactly one face")
  
  # # face_details = detect_faces_result['FaceDetails'][0]
  # # face_details['Confidence']
  # pprint("detect_faces_result: ", detect_faces_result)

  headshot = { "Bytes": uploaded_headshot }
  compare_faces_result = rekognition_client.compare_faces(
    SourceImage=photo_id,
    TargetImage=headshot
  )
  [face_match] = compare_faces_result['FaceMatches']
  if face_match['Similarity'] < 90:
    raise HTTPException(status_code=422, detail="We could not verify your identity. Please try again with a different photo ID or headshot")
  return face_match
  # print("compare_faces_result: ", compare_faces_result)

@app.get("/hello")
def hello_world():
  return { "details": "Hello World! Connected to server successfully" }

