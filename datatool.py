import json

main = json.load(open("haupt.json", "r"))
auth = json.load(open("auth.json", "r"))
verlangsamung = json.load(open("verlangsamung.json", "r"))

# Statistics!
total_users = 0
activated_users = 0
installed_users = 0
past_subscriptions = 0
changed = 0

for idr in main:
    total_users += 1
    if main[idr]["activated"]:
        activated_users += 1
    if main[idr]["installed"]:
        installed_users += 1
        if 'server_id' not in main[idr].keys():
            main[idr]['server_id'] = 0
            changed += 1

    if not main[idr]["activated"] and main[idr]['port'] != 0:
        past_subscriptions += 1


http_authorized = 0

for idr in auth:
    http_authorized += 1


print(f"Total users: {total_users}")
print(f"Activated users: {activated_users}")
print(f"Installed users: {installed_users}")
print(f"Past subscriptions: {past_subscriptions}")
print(f"HTTP authorized: {http_authorized}")

if changed > 0:
    print(f"Changed {changed} entries")
    with open("haupt.json", "w", encoding='utf-8') as f:
        json.dump(main, f, indent=4)
