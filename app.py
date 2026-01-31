from flask import Flask, render_template, request, redirect
import pandas as pd
import os
import random

app = Flask(__name__)

# -------------------------------
# CAREER DATA (GLOBAL)
# -------------------------------
CAREER_MAP = {
    "Computer Science / IT": {
        "jobs": ["Software Developer", "Data Analyst", "AI Engineer"],
        "skills": ["Python", "Java", "SQL", "Problem Solving"]
    },
    "Engineering / Science": {
        "jobs": ["Mechanical Engineer", "Civil Engineer", "Research Assistant"],
        "skills": ["Maths", "Physics", "Analytical Thinking"]
    },
    "Creative / Design": {
        "jobs": ["UI/UX Designer", "Graphic Designer", "Content Creator"],
        "skills": ["Creativity", "Design Tools", "Communication"]
    },
    "Commerce / Management": {
        "jobs": ["Business Analyst", "Accountant", "Marketing Executive"],
        "skills": ["Finance", "Management", "Communication"]
    }
}

AI_QUESTION_BANK = {
    "medical":[
        "are u interested in medical?",
        "do u like studying medical books?",
    ],
    "technology": [
        "Do you enjoy coding or working with computers?",
        "Do you like solving logical problems?",
        "Are you interested in AI or data science?"
    ],
    "creative": [
        "Do you enjoy design or creative work?",
        "Do you like visual storytelling?",
        "Do you enjoy creating content?"
    ],
    "business": [
        "Are you interested in business strategies?",
        "Do you like managing people or projects?",
        "Do you enjoy analyzing markets?"
    ]
}

def generate_ai_questions():
    category = random.choice(list(AI_QUESTION_BANK.keys()))
    questions = random.sample(AI_QUESTION_BANK[category], 2)
    return category, questions

# -------------------------------
# HOME
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------------
# REGISTER
# -------------------------------
@app.route("/start")
def start():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"]
    interest = request.form["interest"]
    marks = request.form["marks"]

    data = {
        "name": name,
        "email": email,
        "interest": interest,
        "marks": marks
    }

    file = "students.xlsx"
    if os.path.exists(file):
        df = pd.read_excel(file)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_excel(file, index=False)

    return redirect("/interest-test")

# -------------------------------
# INTEREST TEST
# -------------------------------
@app.route("/interest-test")
def interest_test():
    category, questions = generate_ai_questions()
    return render_template(
        "interest_test.html",
        questions=questions,
        category=category
    )

@app.route("/submit-interest-test", methods=["POST"])
def submit_interest_test():
    email = request.form["email"]
    score = 0

    for key in request.form:
        if key.startswith("q") and request.form[key] == "yes":
            score += 1

    data = {"email": email, "interest_score": score}

    file = "interest_scores.xlsx"
    if os.path.exists(file):
        df = pd.read_excel(file)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_excel(file, index=False)

    return redirect("/aptitude-test")

# -------------------------------
# APTITUDE TEST
# -------------------------------
@app.route("/aptitude-test")
def aptitude_test():
    return render_template("aptitude_test.html")

# -------------------------------
# FINAL RESULT (STEP 6)
# -------------------------------
@app.route("/final-result", methods=["POST"])
def final_result():
    email = request.form["email"]
    academic_score = int(request.form["academic"])

    interest_df = pd.read_excel("interest_scores.xlsx")
    aptitude_df = pd.read_excel("aptitude_scores.xlsx")

    interest_score = interest_df.loc[
        interest_df["email"] == email, "interest_score"
    ].values[0]

    aptitude_score = aptitude_df.loc[
        aptitude_df["email"] == email, "aptitude_score"
    ].values[0]

    # Recommendation logic
    if interest_score >= 3 and aptitude_score >= 2 and academic_score >= 70:
        field = "Computer Science / IT"
    elif academic_score >= 70:
        field = "Engineering / Science"
    elif interest_score >= 3:
        field = "Creative / Design"
    else:
        field = "Commerce / Management"

    result = {
        "email": email,
        "interest_score": interest_score,
        "aptitude_score": aptitude_score,
        "academic_score": academic_score,
        "recommended_field": field
    }

    career_info = CAREER_MAP.get(field, {
        "jobs": [],
        "skills": []
    })

    return render_template(
        "final_result.html",
        result=result,
        career=career_info
    )

# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)