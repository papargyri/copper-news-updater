import requests
import random
import time
import datetime
import re
import json
import os
from typing import Any

# Configuration
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfCGIXM-ng7QibHYymMNbJ2z4C7Ld0brKyitraR9eUvOzCbUw/formResponse"
PROGRESS_FILE = "progress.json"

# Phase 1: 07:50 - 11:50 (Add 100)
# Phase 2: 11:50 - 16:50 (Add 30)
# TOTAL NEW: 130
TARGET_COUNT_P1 = 505
TARGET_COUNT_P2 = 535

# Profiles Quotas for the next 130:
# Journalist: 57
# Educator: 35
# Others: 38 (Student, Public Official, Citizens)

PROFILES = {
    "journalist": {
        "status": "Δημοσιογράφος",
        "region_bias": ["Κοζάνη", "Θεσσαλονίκη", "Αθήνα"],
        "ease_bias": ["Σχετικά εύκολα", "Σχετικά δύσκολα"],
        "relation_bias": ["Θα ήθελα περισσότερη πρόσβαση", "Αισθάνoμαι ότι έχω πρόσβαση"],
        "tech_familiarity": ["Πολύ — τα χρησιμοποιώ τακτικά"],
        "impact_bias": ["Ναι, σε μεγάλο βαθμό", "Ναι, σε κάποιο βαθμό"],
        "channels": ["Twitter / X", "Website", "Email / Newsletter"]
    },
    "educator": {
        "status": "Εκπαιδευτικός / Ερευνητής/τρια",
        "region_bias": ["Κοζάνη", "Φλώρινα", "Θεσσαλονίκη"],
        "ease_bias": ["Σχετικά εύκολα", "Πολύ εύκολα"],
        "relation_bias": ["Αισθάνoμαι ότι έχω πρόσβαση", "Θα ήθελα περισσότερη πρόσβαση"],
        "tech_familiarity": ["Πολύ — τα χρησιμοποιώ τακτικά"],
        "impact_bias": ["Ναι, σε μεγάλο βαθμό"],
        "channels": ["Email / Newsletter", "Website", "LinkedIn"]
    },
    "general": {
        "status": "Ενεργός πολίτης",
        "region_bias": ["Κοζάνη", "Γρεβενά", "Φλώρινα"],
        "ease_bias": ["Σχετικά εύκολα", "Σχετικά δύσκολα"],
        "relation_bias": ["Δεν έχω ασχοληθεί μέχρι τώρα", "Θα ήθελα περισσότερη πρόσβαση"],
        "tech_familiarity": ["Αρκετά — τα έχω χρησιμοποιήσει"],
        "impact_bias": ["Ναι, σε κάποιο βαθμό"],
        "channels": ["Facebook", "Τοπικά ΜΜΕ"]
    }
}

QUESTIONS = {
    "status": "entry.1030249141", "region": "entry.764644756", "ease_access": "entry.828104733",
    "platforms": "entry.390222346", "relation": "entry.347484670", "obstacles": "entry.647055580",
    "help": "entry.130308681", "familiarity": "entry.1653954732", "training_topics": "entry.935519728",
    "training_format": "entry.2036554560", "likelihood": "entry.789367973", "previous": "entry.384454512",
    "network": "entry.299656661", "channels": "entry.70686218", "impact": "entry.2087326437"
}

def generate_answers(profile_name):
    p = PROFILES[profile_name]
    ans = {
        QUESTIONS["status"]: [p["status"]],
        QUESTIONS["region"]: random.choice(p["region_bias"]),
        QUESTIONS["ease_access"]: random.choice(p["ease_bias"]),
        QUESTIONS["relation"]: random.choice(p["relation_bias"]),
        QUESTIONS["familiarity"]: random.choice(p["tech_familiarity"]),
        QUESTIONS["likelihood"]: "Σίγουρα θα συμμετείχα",
        QUESTIONS["previous"]: "Όχι, αλλά θα με ενδιέφερε",
        QUESTIONS["network"]: "Πολύ χρήσιμο",
        QUESTIONS["obstacles"]: random.choice(["Δεν γνωρίζω τη διαδικασία", "Έλλειψη χρόνου"]),
        QUESTIONS["help"]: "Απλοποιημένος οδηγός για τα δικαιώματά μου",
        QUESTIONS["impact"]: [random.choice(p["impact_bias"])],
        QUESTIONS["platforms"]: ["ΔΙΑΥΓΕΙΑ (diavgeia.gov.gr)"],
        QUESTIONS["training_topics"]: ["Χρήση ΔΙΑΥΓΕΙΑ & ΕΣΗΔΗΣ"],
        QUESTIONS["training_format"]: ["Ζωντανά webinars", "Ατομικές συνεδρίες coaching"],
        QUESTIONS["channels"]: [random.choice(p["channels"])]
    }
    return ans

def submit(profile):
    try:
        session = requests.Session()
        res_get = session.get(FORM_URL.replace("/formResponse", "/viewform"))
        fbzx_val = re.search(r'name="fbzx" value="([^"]+)"', res_get.text).group(1)
        data = generate_answers(profile)
        payload = []
        for q_id, val in data.items():
            if isinstance(val, list):
                for v in val: payload.append((q_id, v))
            else: payload.append((q_id, val))
            payload.append((f"{q_id}_sentinel", ""))
        payload.extend([("fvv", "1"), ("pageHistory", "0"), ("fbzx", fbzx_val),
                       ("partialResponse", json.dumps([None, None, fbzx_val])),
                       ("submissionTimestamp", str(int(time.time() * 1000)))])
        return session.post(FORM_URL, data=payload).status_code == 200
    except: return False

def main():
    while True:
        with open(PROGRESS_FILE, 'r') as f: state = json.load(f)
        count = state["count"]
        # Tracker for sub-quotas in state? Or just random weighted?
        # We need exactly 57 journalists and 35 educators over the next 130.
        j_submitted = state.get("j_count", 0)
        e_submitted = state.get("e_count", 0)
        others_count = state.get("others_count", 0)
        
        if count >= TARGET_COUNT_P2: break
        
        now = datetime.datetime.now()
        # PHASE 1 (07:50 - 11:50) -> 100 answers
        if count < TARGET_COUNT_P1:
            interval = random.randint(120, 1500) # 2 to 25 mins
        # PHASE 2 (11:50 - 16:50) -> 30 answers
        else:
            interval = random.randint(600, 1800) # Spread out
            
        # Select Profile based on remaining quotas
        rem_j = 57 - j_submitted
        rem_e = 35 - e_submitted
        rem_o = 38 - others_count
        total_rem = (TARGET_COUNT_P2 - count)
        
        choices = []
        if rem_j > 0: choices.extend(["journalist"] * rem_j)
        if rem_e > 0: choices.extend(["educator"] * rem_e)
        if rem_o > 0: choices.extend(["general"] * rem_o)
        
        p_name = random.choice(choices) if choices else "general"

        if submit(p_name):
            state["count"] += 1
            if p_name == "journalist": state["j_count"] = state.get("j_count", 0) + 1
            elif p_name == "educator": state["e_count"] = state.get("e_count", 0) + 1
            else: state["others_count"] = state.get("others_count", 0) + 1
            with open(PROGRESS_FILE, 'w') as f: json.dump(state, f)
            print(f"Success! {p_name}. Total: {state['count']}")
        
        time.sleep(interval)

if __name__ == "__main__": main()
