const form = document.querySelector('#form')
const photoIdInputEl = document.querySelector('#face-pic-input')
const photoIdImgEl = document.querySelector('#face-pic')
const headshotWrapper = document.querySelector('#headshot-wrapper')
const cameraPreviewEl = document.querySelector('#camera-preview')
const cameraDevicesEl = document.querySelector('#camera-devices')
const captureHeadshotBtn = document.querySelector('#capture-headshot-btn')
const capturedHeadshotImgEl = document.querySelector('#captured-headshot')
const submitBtn = document.querySelector('#submit-button')
const resultEl = document.querySelector('#result');

photoIdInputEl.addEventListener('change', displayUploadedImage)
form.addEventListener('submit', uploadImage)
cameraDevicesEl.addEventListener('change', switchCamera)
captureHeadshotBtn.addEventListener('click', captureHeadshot)

function displayUploadedImage(e) {
  const base64ImageURL = URL.createObjectURL(e.target.files[0])
  photoIdImgEl.width = 640
  photoIdImgEl.height = 480
  photoIdImgEl.src = base64ImageURL;
}

async function switchCamera() {
  const deviceId = cameraDevicesEl.value
  try {
    const mediaStream = await window.navigator.mediaDevices.getUserMedia({ video: { deviceId: deviceId ? { exact: deviceId } : undefined } });
    if ('srcObject' in cameraPreviewEl) {
      cameraPreviewEl.srcObject = mediaStream;
    } else {
      cameraPreviewEl.src = URL.createObjectURL(mediaStream);
    }
  } catch (error) {
    console.log("Error capturing headshot: ", error)
  }
}

async function captureHeadshot() {
  resultEl.textContent = '';
  if (captureHeadshotBtn.textContent == 'Retake picture') {
    capturedHeadshotImgEl.src = ""
    captureHeadshotBtn.textContent = 'Take picture';
    cameraPreviewEl.style.display = 'block'
    submitBtn.style.display = 'none';
    return;
  }
  const canvas = document.createElement("canvas");
  canvas.width = cameraPreviewEl.videoWidth;
  canvas.height = cameraPreviewEl.videoHeight;

  // Draw the video frame on the canvas
  const context = canvas.getContext("2d");
  context.drawImage(cameraPreviewEl, 0, 0, canvas.width, canvas.height);
  cameraPreviewEl.style.display = 'none'
  // Convert the canvas to a data URL and set it as the img src
  capturedHeadshotImgEl.src = canvas.toDataURL("image/png");
  captureHeadshotBtn.textContent = 'Retake picture'
  submitBtn.style.display = 'block'
}

async function getCameraInputDevices() {
  try {
    const devices = await window.navigator.mediaDevices.enumerateDevices();
    for (const device of devices) {
      if (device.kind == 'videoinput') {
        const optionEl = document.createElement('option');
        optionEl.textContent = device.label;
        optionEl.value = device.deviceId;
        cameraDevicesEl.append(optionEl)
      }
    } 
  } catch (error) {
    console.log('Error getting camera input devices: ', error)
  }
}

async function startCapturingHeadshot() {
  headshotWrapper.style.display = 'flex';
  await switchCamera();
  await getCameraInputDevices()
}

async function uploadImage(e) {
  e.preventDefault();
  const inputEl = e.target[0]
  const files = inputEl.files
  if (!files.length) {
    alert("Please upload a face pic")
    return;
  }
  if (!capturedHeadshotImgEl.src) {
    alert("Please take your live headshot")
    return;
  }
  try {
    resultEl.textContent = 'Matching faces. Please wait...';
    const fd = new FormData();
    fd.append('uploaded_face_pic', files[0]);
    // Since the backend API expects a BLOB, here's a convenient way to convert data URL to BLOB
    fd.append('live_headshot', await (await fetch(capturedHeadshotImgEl.src)).blob());

    const response = await fetch("/upload-image", {
      method: 'POST',
      body: fd,
    });
    const data = await response.json()
    if (!response.ok) {
      resultEl.textContent = data.detail;
      return;
    }
    
    resultEl.textContent = `
      Result:
      Your uploaded face pic and live headshot are similar by ${data['Similarity'].toFixed(2)}%
    `
  } catch (error) {
    console.log(error)
  }
}

startCapturingHeadshot()