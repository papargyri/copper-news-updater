import requests, random, time, datetime, re, json, os

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfCGIXM-ng7QibHYymMNbJ2z4C7Ld0brKyitraR9eUvOzCbUw/formResponse"
PROGRESS_FILE = "progress.json"
TARGET_P1, TARGET_P2 = 505, 535
QUESTIONS = {"status": "entry.1030249141", "region": "entry.764644756", "channels": "entry.70686218", "platforms": "entry.390222346", "impact": "entry.2087326437"}

PROFILES = {
    "journalist": {"status": "Δημοσιογράφος", "region": ["Κοζάνη", "Θεσσαλονίκη"], "channels": ["Twitter / X", "Website"], "platforms": ["data.gov.gr"], "impact": ["Ναι, σε μεγάλο βαθμό"]},
    "educator": {"status": "Εκπαιδευτικός / Ερευνητής/τρια", "region": ["Κοζάνη"], "channels": ["Email / Newsletter"], "platforms": ["ΔΙΑΥΓΕΙΑ"], "impact": ["Ναι, σε μεγάλο βαθμό"]},
    "general": {"status": "Ενεργός πολίτης", "region": ["Κοζάνη"], "channels": ["Facebook"], "platforms": ["Ιστοσελίδες Δήμων"], "impact": ["Ναι, σε κάποιο βαθμό"]}
}

def submit(p_name):
    p = PROFILES[p_name]
    try:
        session = requests.Session()
        res_get = session.get(FORM_URL.replace("/formResponse", "/viewform"), timeout=15)
        fbzx = re.search(r'name="fbzx" value="([^"]+)"', res_get.text).group(1)
        payload = [
            (QUESTIONS["status"], p["status"]), (f"{QUESTIONS['status']}_sentinel", ""),
            (QUESTIONS["region"], random.choice(p["region"])), (f"{QUESTIONS['region']}_sentinel", ""),
            (QUESTIONS["channels"], random.choice(p["channels"])), (f"{QUESTIONS['channels']}_sentinel", ""),
            (QUESTIONS["platforms"], random.choice(p["platforms"])), (f"{QUESTIONS['platforms']}_sentinel", ""),
            (QUESTIONS["impact"], random.choice(p["impact"])), (f"{QUESTIONS['impact']}_sentinel", ""),
            ("fvv", "1"), ("pageHistory", "0"), ("fbzx", fbzx),
            ("partialResponse", json.dumps([None, None, fbzx])),
            ("submissionTimestamp", str(int(time.time() * 1000)))
        ]
        response = session.post(FORM_URL, data=payload, timeout=15)
        return response.status_code == 200
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Submission Error: {e}")
        return False

def main():
    print(f"Automation Stabilized. Resuming at {datetime.datetime.now()}...")
    while True:
        with open(PROGRESS_FILE, 'r') as f: state = json.load(f)
        count = state["count"]
        if count >= TARGET_P2: break
        
        rem_j, rem_e, rem_o = 57 - state.get("j_count", 0), 35 - state.get("e_count", 0), 38 - state.get("others_count", 0)
        choices = (["journalist"] * max(0, rem_j)) + (["educator"] * max(0, rem_e)) + (["general"] * max(0, rem_o))
        p_name = random.choice(choices) if choices else "general"

        print(f"Submitting as {p_name} ({count}/535)...")
        if submit(p_name):
            state["count"] += 1
            if p_name == "journalist": state["j_count"] = state.get("j_count", 0) + 1
            elif p_name == "educator": state["e_count"] = state.get("e_count", 0) + 1
            else: state["others_count"] = state.get("others_count", 0) + 1
            with open(PROGRESS_FILE, 'w') as f: json.dump(state, f)
            print(f"Success! {p_name}. Count: {state['count']}/535 at {datetime.datetime.now()}")
        else:
            print(f"Failed submission. Retrying in 15s...")
            time.sleep(15)
            continue

        interval = random.randint(120, 1500) if state["count"] < TARGET_P1 else random.randint(600, 1800)
        print(f"Waiting {interval}s...")
        time.sleep(interval)

if __name__ == "__main__": main()
