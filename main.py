import boto3
import uvicorn
from typing import Annotated
from fastapi import FastAPI, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from mangum import Mangum

app = FastAPI()
"""
  The "/static" path is used to serve the external CSS and JavaScript files used by the index.html file
"""
app.mount("/static", StaticFiles(directory="static"), name="static")

handler = Mangum(app) # Handler for AWS Lambda

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

  headshot = { "Bytes": uploaded_headshot }
  compare_faces_result = rekognition_client.compare_faces(
    SourceImage=photo_id,
    TargetImage=headshot
  )
  [face_match] = compare_faces_result['FaceMatches']
  
  # Only accept the face match if the similarity is greater than 90
  if face_match['Similarity'] < 90:
    raise HTTPException(status_code=422, detail="We could not verify your identity. Please try again with a different photo ID or headshot")
  return face_match

@app.get("/hello")
def hello_world():
  return { "details": "Hello World! Connected to server successfully" }

if __name__ == "__main__":
  uvicorn.run("main:app", port=8000, log_level="info", reload=True)