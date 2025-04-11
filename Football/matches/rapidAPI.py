import http.client

conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "cf2d07f4f7mshe149901d2193de2p188d9ejsnef35a0df64ee",
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
}

conn.request("GET", "/v3/leagues", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))