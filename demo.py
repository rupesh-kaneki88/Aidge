import requests
import time
import hmac
import hashlib
import json
import base64
from dotenv import load_dotenv
import os
from base64 import b64encode


def convert_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

load_dotenv()
access_key_name = os.getenv('key_name')
access_key_secret = os.getenv('key_secret')

class ApiConfig:
    """
    API configuration class
    """
    # The name and secret of your api key. e.g. 512345 and S4etzZ73nF08vOXVhk3wZjIaLSHw0123
    access_key_name = access_key_name
    access_key_secret = access_key_secret

    # The domain of the API.
    # for api purchased on global site. set api_domain to "api.aidc-ai.com"
    # 中文站购买的API请使用"cn-api.aidc-ai.com"域名 (for api purchased on chinese site) set api_domain to "cn-api.aidc-ai.com"
    api_domain = "api.aidc-ai.com"

    # We offer trial quota to help you familiarize and test how to use the Aidge API in your account
    # To use trial quota, please set use_trial_resource to True
    # If you set use_trial_resource to False before you purchase the API
    # You will receive "Sorry, your calling resources have been exhausted........"
    # 我们为您的账号提供一定数量的免费试用额度可以试用任何API。请将use_trial_resource设置为True用于试用。
    # 如设置为False，且您未购买该API，将会收到"Sorry, your calling resources have been exhausted........."的错误提示
    use_trial_resource = True


def invoke_api(api_name, data):
    timestamp = str(int(time.time() * 1000))

    # Calculate sha256 sign
    sign_string = ApiConfig.access_key_secret + timestamp
    sign = hmac.new(ApiConfig.access_key_secret.encode('utf-8'), sign_string.encode('utf-8'),
                    hashlib.sha256).hexdigest().upper()

    url = f"https://{ApiConfig.api_domain}/rest{api_name}?partner_id=aidge&sign_method=sha256&sign_ver=v2&app_key={ApiConfig.access_key_name}&timestamp={timestamp}&sign={sign}"

    # Add "x-iop-trial": "true" for trial
    headers = {
        "Content-Type": "application/json",
        "x-iop-trial": str(ApiConfig.use_trial_resource).lower()
    }

    # Http request
    response = requests.post(url, data=data, headers=headers)
    # FAQ:https://app.gitbook.com/o/pBUcuyAewroKoYr3CeVm/s/cXGtrD26wbOKouIXD83g/getting-started/faq
    # FAQ(中文/Simple Chinese):https://aidge.yuque.com/org-wiki-aidge-bzb63a/brbggt/ny2tgih89utg1aha
    print(response.text)
    return response.text


if __name__ == '__main__':
    # Call submit api
    api_name = "/ai/virtual/tryon-pro"
    

    # image_base64 = convert_image_to_base64("./shopping.webp")
    # Constructor request Parameters
    request_params = [{
        "clothesList": [{
            # URL of the clothing image should be accessible from the public network.
            # The resolution should be greater than 500x500 pixels and up to a maximum of 3000x3000 pixels
            "imageUrl": "https://res.cloudinary.com/dnilsui8j/image/upload/v1751091524/tshirt-2_fvtmfy.jpg",
            "type": "tops"
        }],
        "model": {
            "base": "General",
            "gender": "female",
            "style": "universal_1",
            "body": "slim",
            "age": "youngadult"
        },
        "viewType": "fullbody",
        "inputQualityDetect": 0,
        "generateCount": 1
    }]

    # Convert parameters to JSON string
    submit_request = {
        "requestParams": json.dumps(request_params)
    }

    # Convert parameters to JSON string
    submit_request_json = json.dumps(submit_request)

    submit_result = invoke_api(api_name, submit_request_json)

    submit_result_json = json.loads(submit_result)
    task_id = submit_result_json.get("data", {}).get("result", {}).get("taskId")

    # Query task status
    query_api_name = "/ai/virtual/tryon-results"
    query_request = json.dumps({"task_id": task_id})
    query_result = None
    while True:
        try:
            query_result = invoke_api(query_api_name, query_request)
            query_result_json = json.loads(query_result)
            task_status = query_result_json.get("data", {}).get("taskStatus")
            if task_status == "finished":
                break
            time.sleep(1)
        except KeyboardInterrupt:
            break

    # Final result
    print(query_result)


