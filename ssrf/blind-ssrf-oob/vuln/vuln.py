import requests

def fetch_product(url, referer):
    headers = {
        "Referer": referer
    }

    r = requests.get(url, headers=headers)
    return r.text

# vulnerable usage
url = "https://vulnerable-lab.net/product"
referer = input("Referer: ")

print(fetch_product(url, referer))
