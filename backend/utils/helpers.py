def build_error(message, status_code=400):
    return {"error": message}, status_code
