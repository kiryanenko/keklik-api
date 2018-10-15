from http.client import responses


def status_text(status_code):
    return responses.get(status_code, '')
