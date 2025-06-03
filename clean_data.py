import json
import requests
import time

# ----------------------------
# Function Definitions (top)
# ----------------------------

def remove_duplicates(entry):
    for key in ['soft_skills', 'tools', 'frameworks']:
        if key in entry:
            entry[key] = list(set(entry[key]))
    return entry

def is_term_in_jd(term, jd):
    prompt = f"Is the term '{term}' mentioned in the job description below? Answer only 'Yes' or 'No'.\n\n{jd}"
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt, "stream": False}
    )
    return 'yes' in response.json()['response'].lower()

def remove_hallucinations(entry):
    jd = entry.get('job_description', '')
    for key in ['soft_skills', 'tools', 'frameworks']:
        if key in entry:
            original = entry[key]
            filtered = []
            removed = []

            for term in original:
                if is_term_in_jd(term, jd):
                    filtered.append(term)
                else:
                    removed.append(term)
                time.sleep(0.5)
            
            entry[key] = filtered

            # 🖨️ Print what was removed
            if removed:
                print(f"🚫 Removed from {key}: {removed}")
            else:
                print(f"✅ No hallucinations in {key}.")
    
    return entry
def classify_industry(jd):
    prompt = """Based on this job description, what is the most likely industry sector?
Choose only one of: Finance, Healthcare, Education, Government, Retail, Technology, Construction, Other.
Respond with only the industry name.\n\n""" + jd
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt, "stream": False}
    )
    return response.json()['response'].strip()

# ----------------------------
# Main Script Flow
# ----------------------------

# Load the JSON
with open("jobs_sydney.json", "r", encoding="utf-8") as f:
    data = json.load(f)[:5]  # process first 5 for test

print("✅ File loaded successfully.")
print("Total job records:", len(data))

# Step 1: Remove duplicates
data = [remove_duplicates(record) for record in data]

# Step 2: Remove hallucinated items
print("🧠 Removing hallucinations using Ollama...")
data = [remove_hallucinations(record) for record in data]

# Step 3: Classify industry
print("🏷 Classifying industry sectors...")
for i, record in enumerate(data, 1):
    record['industry_sector'] = classify_industry(record.get('job_description', ''))
    print(f"✔️ Processed {i} of {len(data)}")
    time.sleep(0.5)

# Step 4: Save the output
with open("cleaned_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("✅ Cleaned data with Ollama enhancements saved to 'cleaned_data.json'")
def is_federal_gov_job(entry):
    fed_keywords = [
        "australian government", "commonwealth", "department", "agency",
        "services australia", "dfat", "defence", "home affairs", 
        "australian public service", "aps", "gov.au"
    ]

    text = (entry.get('company_name', '') + ' ' + entry.get('job_description', '')).lower()

    return any(keyword in text for keyword in fed_keywords)

