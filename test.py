import requests
from tabulate import tabulate

BASE_URL = "http://127.0.0.1:5001"


# ---------------- Form Team ----------------
def test_form_team():
    response = requests.post(f"{BASE_URL}/api/form_team", json={"skill": "Teaching", "team_size": 5})
    data = response.json()
    print("\n=== Form Team ===")
    if data:
        print(tabulate(data, headers="keys", tablefmt="grid"))
    else:
        print("No team data available")


# ---------------- Skilled Volunteers ----------------
def test_skilled_volunteers():
    response = requests.post(f"{BASE_URL}/api/skilled_volunteers", json={"skill": "Teaching", "district": "Satara"})
    data = response.json()
    print("\n=== Skilled Volunteers ===")
    if data:
        print(tabulate(data, headers="keys", tablefmt="grid"))
    else:
        print("No skilled volunteers available")


# ---------------- Show-up Prediction ----------------
def test_showup_prediction():
    response = requests.post(f"{BASE_URL}/api/showup_prediction", json={"volunteer_features": [25, 5, 1]})
    print("\n=== Show-up Prediction ===")
    try:
        data = response.json()
        print(data)
    except:
        print("No prediction available")


# ---------------- Recommend Volunteers ----------------
def test_recommend_volunteers():
    response = requests.post(f"{BASE_URL}/api/recommend_volunteers", json={"volunteer_id": 1, "top_n": 5})
    data = response.json()
    print("\n=== Recommend Volunteers ===")
    if data:
        print(tabulate(data, headers="keys", tablefmt="grid"))
    else:
        print("No recommendations available")


# ---------------- Skill Gap Recommendations ----------------
def test_skill_gap():
    response = requests.get(f"{BASE_URL}/api/skill_gap")
    data = response.json()
    print("\n=== Skill Gap Recommendations ===")
    if data:
        table = [{"Skill": k, "Recommendation": v} for k, v in data.items()]
        print(tabulate(table, headers="keys", tablefmt="grid"))
    else:
        print("No skill gap recommendations available")


# ---------------- Feedback Recommendations ----------------
def test_feedback_recommendations():
    response = requests.post(f"{BASE_URL}/api/feedback_recommendations", json={"feedback": "The training session was very useful"})
    print("\n=== Feedback Recommendations ===")
    try:
        data = response.json()
        if data.get("recommendations"):
            table = [{"Recommendation": r} for r in data["recommendations"]]
            print(tabulate(table, headers="keys", tablefmt="grid"))
        else:
            print("No feedback recommendations available")
    except:
        print("No feedback recommendations available")


# ---------------- Volunteer Engagement ----------------
def test_volunteer_engagement():
    response = requests.get(f"{BASE_URL}/api/volunteer_engagement/1")
    print("\n=== Volunteer Engagement ===")
    try:
        data = response.json()
        print(data)
    except:
        print("No engagement data available")


# ---------------- Training Suggestions ----------------
def test_training_suggestions():
    response = requests.get(f"{BASE_URL}/api/training_suggestions/1")
    print("\n=== Training Suggestions ===")
    try:
        data = response.json()
        print(data)
    except:
        print("No training suggestions available")


# ---------------- Run all tests ----------------
if __name__ == "__main__":
    test_form_team()
    test_skilled_volunteers()
    test_showup_prediction()
    test_recommend_volunteers()
    test_skill_gap()
    test_feedback_recommendations()
    test_volunteer_engagement()
    test_training_suggestions()
