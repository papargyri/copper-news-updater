import asyncio
import random
import time
import datetime
import json
import os
from playwright.async_api import async_playwright

# Configuration
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfCGIXM-ng7QibHYymMNbJ2z4C7Ld0brKyitraR9eUvOzCbUw/viewform"
PROGRESS_FILE = "progress.json"
TARGET_COUNT = 535 # Final for Phase 2

# Exact strings from extract_all_options to ensure 100% selector success
ALL_OPTIONS = {
    "1": ["Ενεργός πολίτης", "Φοιτητής/τρια ή νέος/α εργαζόμενος/η", "Μέλος/στέλεχος Οργάνωσης Κοινωνίας Πολιτών (ΟΚοιΠ)", "Δημοσιογράφος / Blogger / Δημιουργός περιεχομένου", "Εκπαιδευτικός / Ερευνητής/τρια", "Άλλο"],
    "2": ["Κοζάνη", "Γρεβενά", "Καστοριά", "Φλώρινα", "Άλλη περιοχή Δυτικής Μακεδονίας", "Εκτός Δυτικής Μακεδονίας"],
    "3": ["Πολύ εύκολα", "Σχετικά εύκολα", "Σχετικά δύσκολα", "Πολύ δύσκολα", "Δεν έχω προσπαθήσει ποτέ"],
    "4": ["ΔΙΑΥΓΕΙΑ (diavgeia.gov.gr)", "ΕΣΗΔΗΣ (promitheus.gov.gr)", "data.gov.gr", "Κανένα από τα παραπάνω"],
    "5": ["Αισθάνομαι ότι έχω πρόσβαση σε ό,τι χρειάζομαι", "Θα ήθελα περισσότερη πρόσβαση αλλά δεν ξέρω πώς", "Έχω προσπαθήσει αλλά δεν βρήκα αυτό που έψαχνα", "Δεν έχω ασχοληθεί μέχρι τώρα"],
    "6": ["Δεν γνωρίζω τη διαδικασία", "Δύσχρηστες πλατφόρμες", "Έλλειψη χρόνου", "Δεν λαμβάνω απαντήσεις από φορείς", "Νομική πολυπλοκότητα", "Έλλειψη εμπιστοσύνης ότι θα έχει αποτέλεσμα"],
    "7": ["Απλοποιημένος οδηγός για τα δικαιώματά μου", "Έτοιμα πρότυπα αιτημάτων πληροφόρησης", "Ένα εργαλείο/πλατφόρμα που συγκεντρώνει δημόσια δεδομένα", "Νομική υποστήριξη όταν χρειαστεί", "Μια κοινότητα ανθρώπων που ασχολούνται με τα ίδια θέματα"],
    "8": ["Πολύ — τα χρησιμοποιώ τακτικά", "Αρκετά — τα έχω χρησιμοποιήσει κάποιες φορές", "Λίγο — γνωρίζω ότι υπάρχουν αλλά δεν τα έχω χρησιμοποιήσει", "Καθόλου"],
    "9": ["Υποβολή αιτημάτων πληροφόρησης (Ν. 3861/2010)", "Χρήση ΔΙΑΥΓΕΙΑ & ΕΣΗΔΗΣ", "Ανάλυση δημοσίων συμβάσεων", "Fact-checking & δημοσιογραφία δεδομένων", "Σύνταξη policy briefs", "Χρήση εργαλείων οπτικοποίησης δεδομένων (π.χ. Datawrapper)", "Επικοινωνία με τοπικές αρχές"],
    "10": ["Διαδικτυακά μαθήματα (MOOC) — στον δικό μου ρυθμό", "Ζωντανά webinars", "Eργαστήρια (workshops) με φυσική παρουσία", "Ατομικές συνεδρίες coaching", "Πρακτικοί οδηγοί / εγχειρίδια (PDF)"],
    "11": ["Σίγουρα θα συμμετείχα", "Πιθανόν θα συμμετείχα", "Δεν είμαι σίγουρος/η", "Πιθανόν δεν θα συμμετείχα", "Σίγουρα δεν θα συμμετείχα"],
    "12": ["Ναι, τακτικά", "Ναι, 1–2 φορές", "Όχι, αλλά θα με ενδιέφερε", "Όχι, και δεν με ενδιαφέρει"],
    "13": ["Πολύ χρήσιμο", "Αρκετά χρήσιμο", "Λίγο χρήσιμο", "Καθόλου χρήσιμο"],
    "14": ["Facebook", "Instagram", "Email / Newsletter", "LinkedIn", "Website", "Τοπικά ΜΜΕ"],
    "15": ["Ναι, σε μεγάλο βαθμό", "Ναι, σε κάποιο βαθμό", "Λίγο", "Καθόλου"]
}

PROFILES = {
    "journalist": {"status": "Δημοσιογράφος / Blogger / Δημιουργός περιεχομένου", "region": ["Κοζάνη"], "channels": ["Website"], "impact": "Ναι, σε μεγάλο βαθμό"},
    "educator": {"status": "Εκπαιδευτικός / Ερευνητής/τρια", "region": ["Κοζάνη"], "channels": ["Email / Newsletter"], "impact": "Ναι, σε μεγάλο βαθμό"},
    "general": {"status": "Ενεργός πολίτης", "region": ["Κοζάνη"], "channels": ["Facebook"], "impact": "Ναι, σε κάποιο βαθμό"}
}

async def submit_form(page, p_name):
    p = PROFILES[p_name]
    await page.goto(FORM_URL)
    await page.wait_for_load_state("networkidle")
    
    async def click_opt(q_idx, pref_text):
        # 5% chance for 2% floor requirement
        text = random.choice(ALL_OPTIONS[q_idx]) if random.random() < 0.05 else pref_text
        # Precision matching: First by exact text, then fallback to partial
        try:
            # Match strictly by text displayed to user
            selector = f"//*[text()='{text}'] | //div[@aria-label='{text}']"
            # Some options are deeply nested; try a broader containment that excludes script/style tags
            alt_selector = f"//*[contains(text(), '{text[:12]}') and not(self::script) and not(self::style)]"
            await page.locator(f"({selector} | {alt_selector})").first.click(timeout=10000)
        except Exception as e:
            print(f"Locator Error for '{text[:20]}': {e}")
            # Final retry on very short partial text using Playwright's best effort
            await page.get_by_text(text[:8]).first.click(timeout=5000)

    # Filling 1-15 sequentially
    # 1. Status 
    await click_opt("1", p["status"])
    # 2. Region
    await click_opt("2", random.choice(p["region"]))
    # 3. Ease
    await click_opt("3", "Σχετικά εύκολα")
    # 4. Platforms
    await click_opt("4", "ΔΙΑΥΓΕΙΑ (diavgeia.gov.gr)")
    # 5. Relation
    await click_opt("5", "Θα ήθελα περισσότερη πρόσβαση αλλά δεν ξέρω πώς")
    # 6. Obstacles
    await click_opt("6", "Δεν γνωρίζω τη διαδικασία")
    # 7. Help
    await click_opt("7", "Απλοποιημένος οδηγός για τα δικαιώματά μου")
    # 8. Familiarity
    await click_opt("8", "Αρκετά — τα έχω χρησιμοποιήσει κάποιες φορές")
    # 9. Topics
    await click_opt("9", "Χρήση ΔΙΑΥΓΕΙΑ & ΕΣΗΔΗΣ")
    # 10. Format
    await click_opt("10", "Ζωντανά webinars")
    # 11. Likelihood
    await click_opt("11", "Σίγουρα θα συμμετείχα")
    # 12. Previous
    await click_opt("12", "Ναι, 1–2 φορές")
    # 13. Network
    await click_opt("13", "Πολύ χρήσιμο")
    # 14. Channels
    await click_opt("14", random.choice(p["channels"]))
    # 15. Impact
    await click_opt("15", p["impact"])

    await page.click("text='Υποβολή'", timeout=12000)
    await page.wait_for_load_state("networkidle")

async def main():
    while True:
        with open(PROGRESS_FILE, 'r') as f: state = json.load(f)
        count = state["count"]
        if count >= TARGET_COUNT: break
        
        # Slower pace requested: 10-20 min intervals
        interval = random.randint(600, 1200) 
        
        # Quota Logic: Targeting 57 Journalists, 35 Educators, 38 Others
        rem_j = 57 - state.get("j_count", 0)
        rem_e = 35 - state.get("e_count", 0)
        rem_o = 38 - state.get("others_count", 0)
        
        choices = (["journalist"] * max(0, rem_j)) + (["educator"] * max(0, rem_e)) + (["general"] * max(0, rem_o))
        p_name = random.choice(choices) if choices else "general"

        async with async_playwright() as prv:
            browser = await prv.chromium.launch(headless=True)
            page = await (await browser.new_context(locale='el-GR')).new_page()
            try:
                await submit_form(page, p_name)
                state["count"] += 1
                if p_name == "journalist": state["j_count"] = state.get("j_count", 0) + 1
                elif p_name == "educator": state["e_count"] = state.get("e_count", 0) + 1
                else: state["others_count"] = state.get("others_count", 0) + 1
                with open(PROGRESS_FILE, 'w') as f: json.dump(state, f)
                print(f"Success! Progress: {state['count']}/535 at {datetime.datetime.now()} as {p_name}")
            except Exception as e: print(f"Error: {e}")
            await browser.close()
        print(f"Waiting {interval}s (Slower Mode)...")
        await asyncio.sleep(interval)

if __name__ == "__main__": asyncio.run(main())
