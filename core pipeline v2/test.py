def get_meetings_by_title(title: str) -> str:
    """
    Custom scraper for fetching and cleaning email data for a specific sender.

    Args:
        sender (str): The email sender address.

    Returns:
        str: The cleaned response text (HTML tags removed), or an error message.
    """
    import requests
    import re
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    try:
        # Build the URL for the fixed endpoint
        url = f"https://1b988f973611.ngrok-free.app/api/meetings/title/{title}"

        

        # Retry strategy
        retry_strategy = Retry(
            total=3,                # retry up to 3 times
            backoff_factor=2,       # wait 2s, 4s, 8s between retries
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)

        # Fetch response (ignores SSL errors, allows retries)
        response = http.get(url, verify=False, timeout=30)
        response.raise_for_status()

        raw_text = response.text
        clean_text = re.sub(r"<.*?>", "", raw_text)  # remove HTML tags

        return clean_text.strip()

    except requests.exceptions.Timeout:
        return "Unable to retrieve data: Connection timed out."
    except requests.exceptions.SSLError:
        return "Unable to retrieve data due to SSL error."
    except requests.exceptions.RequestException as e:
        return f"Unable to retrieve data: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

 