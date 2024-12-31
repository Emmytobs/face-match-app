import boto3
import uvicorn
from typing import Annotated
from fastapi import FastAPI, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from mangum import Mangum

app = FastAPI()
"""
  The "/static" path is used to serve the external CSS and JavaScript files used by the index.html file.
  Note: When you make changes to files in the /static directory, you'll need to comment out the line below, restart the server, and add the line back in.
"""
app.mount("/static", StaticFiles(directory="static"), name="static")

handler = Mangum(app) # Handler for AWS Lambda

rekognition_client = boto3.client('rekognition')

@app.get("/")
async def read_index():
  return FileResponse("static/index.html")

@app.post('/upload-image')
def upload_image(
  uploaded_face_pic: Annotated[bytes, File()], 
  live_headshot: Annotated[bytes, File()]
):
  try:
    source_image = {"Bytes": uploaded_face_pic}
    # Validate to make sure there's exactly one face in the uploaded_face_pic
    detect_faces_result = rekognition_client.detect_faces(Image=source_image)
    if len(detect_faces_result['FaceDetails']) > 1:
      raise HTTPException(status_code=422, detail="It seems the uploaded face pic contains more than one face or no faces at all. Please upload a photo with exactly one face")

    target_image = { "Bytes": live_headshot }
    compare_faces_result = rekognition_client.compare_faces(
      SourceImage=source_image,
      TargetImage=target_image,
      SimilarityThreshold=0
    )
    [face_match] = compare_faces_result['FaceMatches']
    return face_match
  except Exception as e:
    raise e

@app.get("/hello")
def hello_world():
  return { "details": "Hello World! Connected to server successfully" }

if __name__ == "__main__":
  uvicorn.run("main:app", port=8000, log_level="info", reload=True)