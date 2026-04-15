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
TOTAL_TARGET = 405
PROGRESS_FILE = "progress.json"

# Questions Mapping
QUESTIONS = {
    "status": "entry.1030249141",
    "region": "entry.764644756",
    "ease_access": "entry.828104733",
    "platforms": "entry.390222346",
    "relation": "entry.347484670",
    "obstacles": "entry.647055580",
    "help": "entry.130308681",
    "familiarity": "entry.1653954732",
    "training_topics": "entry.935519728",
    "training_format": "entry.2036554560",
    "likelihood": "entry.789367973",
    "previous": "entry.384454512",
    "network": "entry.299656661",
    "channels": "entry.70686218",
    "impact": "entry.2087326437"
}

# Profile Definitions
PROFILES = {
    "student_skeptic": {
        "status": "Φοιτητής/τρια ή νέος/α εργαζόμενος/η",
        "region_bias": ["Κοζάνη", "Φλώρινα", "Γρεβενά"],
        "ease_bias": ["Σχετικά δύσκολα", "Πολύ δύσκολα", "Σχετικά εύκολα"],
        "relation_bias": ["Θα ήθελα περισσότερη πρόσβαση αλλά δεν ξέρω πώς", "Έχω προσπαθήσει αλλά δεν βρήκα αυτό που έψαχνα"],
        "impact_bias": ["Λίγο", "Ναι, σε κάποιο βαθμό"],
        "tech_familiarity": ["Αρκετά — τα έχω χρησιμοποιήσει κάποιες φορές", "Λίγο — γνωρίζω ότι υπάρχουν"],
        "channels": ["Instagram", "Facebook", "Email / Newsletter"]
    },
    "public_official": {
        "status": "Δημόσιος υπάλληλος / Στέλεχος ΟΤΑ",
        "region_bias": ["Κοζάνη", "Γρεβενά", "Καστοριά"],
        "ease_bias": ["Πολύ εύκολα", "Σχετικά εύκολα", "Σχετικά δύσκολα"],
        "relation_bias": ["Αισθάνoμαι ότι έχω πρόσβαση σε ό,τι χρειάζομαι", "Θα ήθελα περισσότερη πρόσβαση αλλά δεν ξέρω πώς"],
        "impact_bias": ["Ναι, σε μεγάλο βαθμό", "Ναι, σε κάποιο βαθμό"],
        "tech_familiarity": ["Πολύ — τα χρησιμοποιώ τακτικά", "Αρκετά — τα έχω χρησιμοποιήσει"],
        "channels": ["Email / Newsletter", "Website", "Τοπικά ΜΜΕ"]
    },
    "activist_ngo": {
        "status": "Μέλος/στέλεχος Οργάνωσης Κοινωνίας Πολιτών (ΟΚοιΠ)",
        "region_bias": ["Κοζάνη", "Φλώρινα", "Καστοριά"],
        "ease_bias": ["Σχετικά δύσκολα", "Πολύ δύσκολα", "Σχετικά εύκολα"],
        "relation_bias": ["Έχω προσπαθήσει αλλά δεν βρήκα αυτό που έψαχνα", "Θα ήθελα περισσότερη πρόσβαση"],
        "impact_bias": ["Ναι, σε μεγάλο βαθμό", "Ναι, σε κάποιο βαθμό"],
        "tech_familiarity": ["Πολύ — τα χρησιμοποιώ τακτικά"],
        "channels": ["Email / Newsletter", "Website", "Facebook", "Twitter / X"]
    },
    "general_citizen": {
        "status": "Ενεργός πολίτης",
        "region_bias": ["Κοζάνη", "Γρεβενά", "Καστοριά", "Φλώρινα"],
        "ease_bias": ["Δεν έχω προσπαθήσει ποτέ", "Σχετικά εύκολα", "Σχετικά δύσκολα"],
        "relation_bias": ["Δεν έχω ασχοληθεί μέχρι τώρα", "Θα ήθελα περισσότερη πρόσβαση"],
        "impact_bias": ["Ναι, σε κάποιο βαθμό", "Λίγο"],
        "tech_familiarity": ["Λίγο — γνωρίζω ότι υπάρχουν", "Καθόλου", "Αρκετά — τα έχω χρησιμοποιήσει"],
        "channels": ["Facebook", "Τοπικά ΜΜΕ", "Website"]
    }
}

def generate_answers(profile_name, forced_region=None):
    p = PROFILES[profile_name]
    answers: dict[str, Any] = {}
    
    # 1. Status
    answers[QUESTIONS["status"]] = [p["status"]]
    
    # 2. Region
    answers[QUESTIONS["region"]] = forced_region if forced_region else random.choice(p["region_bias"])
    
    # 3. Ease
    answers[QUESTIONS["ease_access"]] = random.choice(p["ease_bias"])
    
    # 4. Platforms
    plats = ["ΔΙΑΥΓΕΙΑ (diavgeia.gov.gr)"]
    if random.random() < 0.25: plats.append("ΕΣΗΔΗΣ (promitheus.gov.gr)")
    if random.random() < 0.45: plats.append("data.gov.gr")
    if random.random() < 0.40: plats.append("Ιστοσελίδες Δήμων / Περιφερειών")
    answers[QUESTIONS["platforms"]] = plats
    
    # 5. Relation
    answers[QUESTIONS["relation"]] = random.choice(p["relation_bias"])
    
    # 6. Obstacles
    answers[QUESTIONS["obstacles"]] = random.choice(["Δεν γνωρίζω τη διαδικασία", "Δύσχρηστες πλατφόρμες", "Έλλειψη χρόνου", "Νομική πολυπλοκότητα"])
    
    # 7. Help
    answers[QUESTIONS["help"]] = random.choice(["Απλοποιημένος οδηγός για τα δικαιώματά μου", "Έτοιμα πρότυπα αιτημάτων πληροφόρησης", "Ένα εργαλείο/πλατφόρμα που συγκεντρώνει δημόσια δεδομένα"])
    
    # 8. Familiarity
    answers[QUESTIONS["familiarity"]] = random.choice(p["tech_familiarity"])
    
    # 9. Topics
    answers[QUESTIONS["training_topics"]] = random.sample(["Υποβολή αιτημάτων πληροφόρησης (Ν. 3861/2010)", "Χρήση ΔΙΑΥΓΕΙΑ & ΕΣΗΔΗΣ", "Ανάλυση δημοσίων συμβάσεων"], k=random.randint(1, 2))
    
    # 10. Format
    formats = []
    if random.random() < 0.25: formats.append("Ζωντανά webinars")
    if random.random() < 0.40: formats.append("Διαδικτυακά μαθήματα (MOOC) — στον δικό μου ρυθμό")
    if random.random() < 0.40: formats.append("Εργαστήρια (workshops) με φυσική παρουσία")
    if random.random() < 0.60: formats.append("Ατομικές συνεδρίες coaching")
    if random.random() < 0.50: formats.append("Πρακτικοί οδηγοί / εγχειρίδια (PDF)")
    if not formats: formats = ["Ατομικές συνεδρίες coaching"]
    answers[QUESTIONS["training_format"]] = formats
    
    # 11. Likelihood
    answers[QUESTIONS["likelihood"]] = random.choice(["Σίγουρα θα συμμετείχα", "Πιθανόν θα συμμετείχα", "Δεν είμαι σίγουρος/η"])
    
    # 12. Previous
    answers[QUESTIONS["previous"]] = random.choice(["Ναι, 1–2 φορές", "Όχι, αλλά θα με ενδιέφερε", "Όχι, και δεν με ενδιαφέρει"])
    
    # 13. Network
    answers[QUESTIONS["network"]] = random.choice(["Πολύ χρήσιμο", "Αρκετά χρήσιμο"])
    
    # 14. Channels
    chans = []
    if random.random() < 0.12: chans.append("Instagram")
    if random.random() < 0.35: chans.append("Website")
    if random.random() < 0.60: chans.append("Facebook")
    if random.random() < 0.40: chans.append("Email / Newsletter")
    if random.random() < 0.25: chans.append("Τοπικά ΜΜΕ")
    if not chans: chans = ["Facebook"]
    answers[QUESTIONS["channels"]] = chans
    
    # 15. Impact
    answers[QUESTIONS["impact"]] = [random.choice(p["impact_bias"])]
    
    return answers

def submit():
    with open(PROGRESS_FILE, 'r') as f:
        state = json.load(f)
        submitted_count = state.get("count", 0)
        start_time = datetime.datetime.fromisoformat(state.get("start_time"))
    
    rand = random.random()
    if rand < 0.50: profile, region = "student_skeptic", "Κοζάνη"
    elif rand < 0.65: profile, region = random.choice(["public_official", "activist_ngo", "general_citizen"]), "Κοζάνη"
    elif rand < 0.76: profile, region = "general_citizen", "Εκτός Δυτικής Μακεδονίας"
    else: profile, region = "general_citizen", random.choice(["Γρεβενά", "Φλώρινα", "Καστοριά"])

    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": FORM_URL.replace("/formResponse", "/viewform")
        })
        res_get = session.get(FORM_URL.replace("/formResponse", "/viewform"))
        fbzx = re.search(r'name="fbzx" value="([^"]+)"', res_get.text)
        fbzx_val = fbzx.group(1) if fbzx else "1017048205989082887"

        data = generate_answers(profile, forced_region=region)
        payload = []
        for q_id, val in data.items():
            if isinstance(val, list):
                for v in val: payload.append((q_id, v))
            else: payload.append((q_id, val))
            payload.append((f"{q_id}_sentinel", ""))
        
        payload.extend([
            ("fvv", "1"), ("pageHistory", "0"), ("fbzx", fbzx_val),
            ("partialResponse", json.dumps([None, None, fbzx_val])),
            ("submissionTimestamp", str(int(time.time() * 1000)))
        ])
        
        response = session.post(FORM_URL, data=payload)
        if response.status_code == 200:
            print(f"Success: {profile} in {region} at {datetime.datetime.now()}")
            return True
        else:
            print(f"Error: {response.status_code}. Snippet: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    while True:
        with open(PROGRESS_FILE, 'r') as f:
            state = json.load(f)
            count = state["count"]
            start_time = datetime.datetime.fromisoformat(state["start_time"])
        
        if count >= TOTAL_TARGET: break
        
        # New Rule: Max 5 per hour (min 12-minute interval)
        interval = random.randint(720, 900) # 12 to 15 minutes
        
        if submit():
            count += 1
            with open(PROGRESS_FILE, 'w') as f:
                json.dump({"count": count, "start_time": start_time.isoformat()}, f)
            print(f"Progress: {count}/{TOTAL_TARGET} at {datetime.datetime.now()}")
        
        print(f"Waiting {interval}s... Next at ~{datetime.datetime.now() + datetime.timedelta(seconds=interval)}")
        time.sleep(interval)

if __name__ == "__main__":
    main()
