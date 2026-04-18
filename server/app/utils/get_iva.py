import requests

async def get_iva():
    response = requests.request(method="", url="")
    if response.status_code != 200: return {"message":"No response allowed"}
    data = response.json()
    return data