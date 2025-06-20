import requests

MODEL_BASE_URL = "https://model.sui-ru.com"
HATE_ANALYZE_ENDPOINT = "/hate/analyze/"
MISINFORMATION_ANALYZE_ENDPOINT = "/misinformation/analyze/"

def analyze_hate(content):
    """
    Sends content to the hate analysis model endpoint.
    Args:
        content (str): The text/content to analyze.
    Returns:
        dict: The model's response or error info.
    """
    try:
        response = requests.post(
            MODEL_BASE_URL + HATE_ANALYZE_ENDPOINT,
            json={"content": content},
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
    try:
        response = requests.post(
            MODEL_BASE_URL + MISINFORMATION_ANALYZE_ENDPOINT,
            json={"content": content},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
