import requests

# Register new webhook for earnings
r = requests.post('https://finnhub.io/api/v1/webhook/add?token=btvkm4748v6uc2r6kpp0', json={'event': 'earnings', 'symbol': 'AAPL'})
res = r.json()
print(res)

webhook_id = res['id']
# List webhook
r = requests.get('https://finnhub.io/api/v1/webhook/list?token=btvkm4748v6uc2r6kpp0')
res = r.json()
print(res)

#Delete webhook
r = requests.post('https://finnhub.io/api/v1/webhook/delete?token=btvkm4748v6uc2r6kpp0', json={'id': webhook_id})
res = r.json()
print(res)
