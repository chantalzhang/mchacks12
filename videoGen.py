import os
import time
import requests
import json

api_key = "Fill in the API Key"

def get_next_video_number():
    """Find the next available video number by checking existing files"""
    i = 1
    while True:
        if not os.path.exists(f"McHacksVideo{i}.mp4"):
            return i
        i += 1

def generate_video(prompt_text: str, model_type: str = "T2V-01") -> bool:
    """
    Generate a video using the Minimax API
    Args:
        prompt_text (str): Description of the video to generate
        model_type (str): Model to use for generation
    Returns:
        bool: True if video generation was successful, False otherwise
    """
    # Get the next available number and create filename
    video_number = get_next_video_number()
    output_path = f"McHacksVideo{video_number}.mp4"

    def invoke_video_generation() -> str:
        print("-----------------Submit video generation task-----------------")
        url = "https://api.minimaxi.chat/v1/video_generation"
        payload = json.dumps({
            "prompt": prompt_text,
            "model": model_type
        })
        headers = {
            'authorization': 'Bearer ' + api_key,
            'content-type': 'application/json',
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        task_id = response.json()['task_id']
        print("Video generation task submitted successfully, task ID："+task_id)
        return task_id

    def query_video_generation(task_id: str):
        url = "https://api.minimaxi.chat/v1/query/video_generation?task_id="+task_id
        headers = {
            'authorization': 'Bearer ' + api_key
        }
        response = requests.request("GET", url, headers=headers)
        status = response.json()['status']
        if status == 'Preparing':
            print("...Preparing...")
            return "", 'Preparing'   
        elif status == 'Queueing':
            print("...In the queue...")
            return "", 'Queueing'
        elif status == 'Processing':
            print("...Generating...")
            return "", 'Processing'
        elif status == 'Success':
            return response.json()['file_id'], "Finished"
        elif status == 'Fail':
            return "", "Fail"
        else:
            return "", "Unknown"

    def fetch_video_result(file_id: str):
        print("---------------Video generated successfully, downloading now---------------")
        url = "https://api.minimaxi.chat/v1/files/retrieve?file_id="+file_id
        headers = {
            'authorization': 'Bearer '+api_key,
        }

        response = requests.request("GET", url, headers=headers)
        print(response.text)

        download_url = response.json()['file']['download_url']
        print("Video download link：" + download_url)
        with open(output_path, 'wb') as f:
            f.write(requests.get(download_url).content)
        print("The video has been downloaded in："+os.getcwd()+'/'+output_path)

    try:
        task_id = invoke_video_generation()
        print("-----------------Video generation task submitted -----------------")
        while True:
            time.sleep(10)
            file_id, status = query_video_generation(task_id)
            if file_id != "":
                fetch_video_result(file_id)
                print("---------------Successful---------------")
                return True
            elif status == "Fail" or status == "Unknown":
                print("---------------Failed---------------")
                return False
    except Exception as e:
        print(f"Error generating video: {str(e)}")
        return False

if __name__ == '__main__':
    # Example usage when running the file directly
    # When no prompt is provided, the default prompt is used
    generate_video("A beautiful sunset over the ocean")