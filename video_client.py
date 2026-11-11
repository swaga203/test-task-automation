import os
import requests

def UploadVideo(server_url: str, video_path: str, company_name: str) -> str:
    """Uploads a video file to the server and returns its URL."""
    url = f"{server_url.rstrip('/')}/upload"
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at {video_path}")
    
    with open(video_path, "rb") as f:
        files = {"file": (os.path.basename(video_path), f)}
        data = {"company_name": company_name}
        response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        res_json = response.json()
        return res_json.get("video_url")
    else:
        raise Exception(f"Failed to upload video: {response.status_code} - {response.text}")

def GetVideoURL(server_url: str, company_name: str) -> str:
    """Returns the video URL for the given company name."""
    url = f"{server_url.rstrip('/')}/get_video_url"
    params = {"company_name": company_name}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        res_json = response.json()
        return res_json.get("video_url")
    elif response.status_code == 404:
        raise Exception(f"Company '{company_name}' not found on server.")
    else:
        raise Exception(f"Failed to get video URL: {response.status_code} - {response.text}")