# ------------------------------
# app.py (updated version)
# ------------------------------

from flask import Flask, request, jsonify
import pandas as pd
import joblib
import warnings

app = Flask(__name__)

# Load dataset
df = pd.read_csv("NGO_Volunteers_Maharashtra_1000.csv")

# Load ML models
try:
    team_formation_model = joblib.load("models/team_formation_model.pkl")
except:
    warnings.warn("team_formation_model.pkl cannot be loaded. Using fallback function.")
    team_formation_model = None

try:
    skilled_volunteer_filter_function = joblib.load("models/skilled_volunteer_filter_function.pkl")
except:
    warnings.warn("skilled_volunteer_filter_function.pkl cannot be loaded. Using fallback function.")
    skilled_volunteer_filter_function = None

# ------------------------------
# Helper: fallback selection
# ------------------------------
def fallback_selection(skill=None, district=None, top_n=5):
    subset = df.copy()
    if skill:
        subset = subset[subset['Primary_Skill'].str.contains(skill, case=False, na=False)]
    if district:
        subset = subset[subset['District'].str.contains(district, case=False, na=False)]
    # Fallback by Language or Address if subset is too small
    if len(subset) < top_n:
        fallback_subset = df.copy()
        if skill:
            fallback_subset = fallback_subset[fallback_subset['Languages_Known'].str.contains(skill, case=False, na=False)]
        if len(fallback_subset) >= top_n:
            subset = fallback_subset
        else:
            subset = df.sample(min(top_n, len(df)))  # Random fallback
    return subset.head(top_n)[['Volunteer_Name', 'Primary_Skill', 'District']].to_dict(orient='records')

# ------------------------------
# API Endpoints
# ------------------------------

@app.route("/api/form_team", methods=["POST"])
def api_form_team():
    data = request.get_json()
    skill = data.get("skill")
    team_size = data.get("team_size", 5)
    if team_formation_model:
        team = team_formation_model(skill, team_size=team_size)
        if isinstance(team, pd.DataFrame):
            return jsonify(team[['Volunteer_Name', 'Primary_Skill', 'District']].to_dict(orient='records'))
    # Fallback
    return jsonify(fallback_selection(skill=skill, top_n=team_size))

@app.route("/api/skilled_volunteers", methods=["POST"])
def api_skilled_volunteers():
    data = request.get_json()
    skill = data.get("skill")
    district = data.get("district")
    if skilled_volunteer_filter_function:
        df_res = skilled_volunteer_filter_function(skill, district=district)
        if isinstance(df_res, pd.DataFrame) and not df_res.empty:
            return jsonify(df_res[['Volunteer_Name', 'Primary_Skill', 'District']].to_dict(orient='records'))
    # Fallback
    return jsonify(fallback_selection(skill=skill, district=district, top_n=10))

@app.route("/api/showup_prediction", methods=["POST"])
def api_showup_prediction():
    data = request.get_json()
    features = data.get("volunteer_features")
    if features is None or len(features) != 3:
        return jsonify({"error": "Invalid input for showup prediction"})
    # Placeholder prediction
    return jsonify({"prediction": "Likely to Show-up"})

@app.route("/api/recommend_volunteers", methods=["POST"])
def api_recommend_volunteers():
    # Placeholder using random selection
    top_n = request.get_json().get("top_n", 5)
    return jsonify(fallback_selection(top_n=top_n))

@app.route("/api/skill_gap", methods=["GET"])
def api_skill_gap():
    return jsonify({
        "Counseling": "Recommended Counseling Workshop / Online Course",
        "IT Support": "Recommended IT Support Workshop / Online Course",
        "Logistics": "Recommended Logistics Workshop / Online Course"
    })

@app.route("/api/feedback_recommendations", methods=["POST"])
def api_feedback_recommendations():
    return jsonify({"recommendations": ["Workshop A", "Workshop B"]})

@app.route("/api/volunteer_engagement/<int:volunteer_id>", methods=["GET"])
def api_volunteer_engagement(volunteer_id):
    # Placeholder data
    return jsonify({"hours_logged": 12, "events_participated": 3})

@app.route("/api/training_suggestions/<int:volunteer_id>", methods=["GET"])
def api_training_suggestions(volunteer_id):
    # Placeholder data
    return jsonify({"suggestions": ["First Aid Training", "Leadership Workshop"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
