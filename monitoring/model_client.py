import requests

MODEL_BASE_URL = "https://model.sui-ru.com"
HATE_ANALYZE_ENDPOINT = "/hate/analyze"
MISINFORMATION_ANALYZE_ENDPOINT = "/misinformation/analyze"

def analyze_hate(content, user_id=None, platform=None, store_result=True):
    """
    Sends content to the hate analysis model endpoint.
    Args:
        content (str): The text/content to analyze.
        user_id (str, optional): The user ID.
        platform (str, optional): The platform name.
        store_result (bool, optional): Whether to store the result.
    Returns:
        dict: The model's response or error info.
    """
    payload = {
        "text": content,
        "store_result": store_result
    }
    if user_id:
        payload["user_id"] = user_id
    if platform:
        payload["platform"] = platform
    print(f"[analyze_hate] Sending payload: {payload}")  # Debug print
    try:
        response = requests.post(
            MODEL_BASE_URL + HATE_ANALYZE_ENDPOINT,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def analyze_misinformation(content):
    """
    Sends content to the misinformation analysis model endpoint.
    Args:
        content (str): The text/content to analyze.
    Returns:
        dict: The model's response or error info.
    """
    payload = {
        "text": content
    }
    print(f"[analyze_misinformation] Sending payload: {payload}")  # Debug print
    try:
        response = requests.post(
            MODEL_BASE_URL + MISINFORMATION_ANALYZE_ENDPOINT,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
