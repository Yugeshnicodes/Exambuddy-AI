import os
import json
import re
from pathlib import Path
from datetime import datetime, timezone

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from google import genai
from groq import Groq

import firebase_admin
from firebase_admin import credentials, firestore


# =========================================================
# BASIC CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)


# =========================================================
# GEMINI CONFIGURATION
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3-flash-preview"
)

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing in .env file."
    )

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# GROQ BACKUP CONFIGURATION
# =========================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

if not GROQ_API_KEY:

    print(
        "WARNING: GROQ_API_KEY is missing. "
        "Gemini will work, but Groq backup will not."
 firebase_key_path = (
   )

groq_client = None

if GROQ_API_KEY:

    groq_client = Groq(
        api_key=GROQ_API_KEY
    )


# =========================================================
# FIREBASE CONFIGURATION
# =========================================================

    BASE_DIR
    / "firebase"
    / "serviceAccountKey.json"
)

if not firebase_admin._apps:

    if firebase_key_path.exists():

        credential = credentials.Certificate(
            str(firebase_key_path)
        )

        firebase_admin.initialize_app(
            credential
        )

    else:

        firebase_config = os.getenv(
            "FIREBASE_SERVICE_ACCOUNT_JSON"
        )

        if firebase_config:

            service_account_info = json.loads(
                firebase_config
            )

            credential = credentials.Certificate(
                service_account_info
            )

            firebase_admin.initialize_app(
                credential
            )

        else:

            raise RuntimeError(
                "Firebase credentials are missing."
            )


db = firestore.client()


# =========================================================
# STUDY / EXAM TOPIC FILTER
# =========================================================

STUDY_KEYWORDS = [

    # General academic terms
    "study",
    "studies",
    "student",
    "exam",
    "exams",
    "examination",
    "question",
    "answer",
    "subject",
    "chapter",
    "unit",
    "syllabus",
    "lesson",
    "academic",
    "education",
    "college",
    "school",
    "university",
    "semester",
    "revision",
    "revise",
    "notes",
    "assignment",
    "homework",
    "project",
    "viva",
    "mcq",
    "quiz",
    "question paper",
    "previous year",
    "important questions",

    # Marks
    "2 mark",
    "2 marks",
    "5 mark",
    "5 marks",
    "10 mark",
    "10 marks",
    "13 mark",
    "13 marks",
    "15 mark",
    "15 marks",
    "16 mark",
    "16 marks",
    "20 mark",
    "20 marks",
    "50 mark",
    "50 marks",

    # Learning
    "explain",
    "define",
    "definition",
    "meaning",
    "difference",
    "advantages",
    "disadvantages",
    "features",
    "characteristics",
    "types",
    "importance",
    "applications",
    "principle",
    "principles",
    "example",
    "examples",
    "concept",
    "learn",
    "learning",
    "prepare",
    "preparation",
    "timetable",
    "study plan",

    # Common technical / academic subjects
    "python",
    "java",
    "c programming",
    "c++",
    "javascript",
    "html",
    "css",
    "database",
    "dbms",
    "sql",
    "operating system",
    "os",
    "computer network",
    "networking",
    "machine learning",
    "artificial intelligence",
    "ai",
    "data science",
    "data structures",
    "algorithm",
    "cloud computing",
    "cyber security",
    "cybersecurity",
    "software engineering",
    "web development",
    "iot",
    "embedded systems",
    "distributed computing",
    "statistics",
    "mathematics",
    "probability"
]


def is_study_exam_question(question):

    text = question.lower().strip()

    # -----------------------------------------------------
    # Direct keyword check
    # -----------------------------------------------------

    for keyword in STUDY_KEYWORDS:

        if keyword in text:

            return True

    # -----------------------------------------------------
    # Common academic question patterns
    # -----------------------------------------------------

    academic_patterns = [

        r"\bwhat is\b",
        r"\bwhat are\b",
        r"\bdefine\b",
        r"\bexplain\b",
        r"\bdescribe\b",
        r"\bdiscuss\b",
        r"\bcompare\b",
        r"\bdifferentiate\b",
        r"\bhow does\b",
        r"\bhow do\b",
        r"\bwhy is\b",
        r"\bwhy are\b",
        r"\bwrite about\b",
        r"\bshort note\b",
        r"\blong answer\b",
        r"\bsolve\b",
        r"\bcalculate\b",
        r"\bderive\b",
        r"\bprogram\b",
        r"\bcode\b"
    ]

    for pattern in academic_patterns:

        if re.search(pattern, text):

            return True

    return False


# =========================================================
# ANSWER TYPE DETECTION
# =========================================================

def detect_answer_type(question):

    text = question.lower().strip()

    # Explicit marks

    if re.search(
        r"\b2\s*marks?\b|\b2\s*mark\b",
        text
    ):
        return "2"

    if re.search(
        r"\b5\s*marks?\b|\b5\s*mark\b",
        text
    ):
        return "5"

    if re.search(
        r"\b10\s*marks?\b|\b10\s*mark\b",
        text
    ):
        return "10"

    if re.search(
        r"\b13\s*marks?\b|\b13\s*mark\b",
        text
    ):
        return "13"

    if re.search(
        r"\b15\s*marks?\b|\b15\s*mark\b",
        text
    ):
        return "15"

    if re.search(
        r"\b16\s*marks?\b|\b16\s*mark\b",
        text
    ):
        return "16"

    if re.search(
        r"\b20\s*marks?\b|\b20\s*mark\b",
        text
    ):
        return "20"

    if re.search(
        r"\b50\s*marks?\b|\b50\s*mark\b",
        text
    ):
        return "50"

    # Special requests

    if (
        "mcq" in text
        or "multiple choice" in text
    ):
        return "mcq"

    if "quiz" in text:
        return "quiz"

    if "revision" in text:
        return "revision"

    if "question paper" in text:
        return "question_paper"

    if "assignment" in text:
        return "assignment"

    # Definition

    if (
        text.startswith("define ")
        or text.startswith("what is ")
        or "define " in text
    ):
        return "definition"

    return "short"


# =========================================================
# EXAMBUDDY AI INSTRUCTION
# =========================================================

SYSTEM_INSTRUCTION = """

You are ExamBuddy AI.

You are ONLY an academic and exam preparation assistant.

Your purpose is to help students with STUDY, EDUCATION,
ACADEMIC and EXAM related questions.

You MUST answer questions related to:

- Exams
- Exam preparation
- Academic subjects
- College subjects
- School subjects
- University subjects
- Definitions
- 2 mark answers
- 5 mark answers
- 10/13/15/16 mark answers
- Long answers
- MCQs
- Quizzes
- Revision notes
- Question papers
- Assignments
- Programming questions for learning
- Academic projects
- Study plans
- Study timetables
- Academic concepts
- Technical subjects
- Mathematics
- Science
- Computer Science
- Engineering subjects

IMPORTANT:

If the question is NOT related to study, education,
academics or exams, DO NOT answer it.

For unrelated questions, respond ONLY with:

Sorry, I can help only with study and exam-related questions. Please ask an academic or exam-related question.

Examples of questions that MUST be rejected:

- Tell me a joke.
- What is today's weather?
- Who is the best actor?
- Tell me a movie story.
- What is the latest sports news?
- Give me a random story.
- What should I eat?
- Tell me about celebrities.
- General chatting.
- Entertainment questions.

Do NOT answer unrelated questions even if the user asks
for an explanation or detailed answer.

IMPORTANT ANSWER RULES:

1. Always understand the exact academic question.

2. If the student asks a simple definition such as:

Define database
What is AI?
Define operating system

Give only a short definition.
Maximum 2 or 3 sentences.

3. If the student does NOT mention marks:

Give a short and useful academic answer.

Do NOT automatically give a 5-mark or 10-mark answer.

4. If the student specifically asks for 2 marks:

Give a very short exam-ready answer.

5. If the student specifically asks for 5 marks:

Give a medium-length answer with important points.

6. If the student specifically asks for 10, 13, 15, 16, 20
or 50 marks:

Give a detailed answer suitable for that mark level.

7. If the student asks for an assignment:

Give an assignment-style academic response.

8. If the student asks for a question paper:

Generate a proper academic question paper with sections and marks.

9. If the student asks for MCQs:

Give questions with four options and clearly show the correct answer.

10. If the student asks for revision notes:

Give concise bullet-point notes.

11. If the student asks a programming question:

Explain it simply and provide correct code when needed.

12. Always stay relevant to the exact academic question.

13. Never add unnecessary information.

14. Never ask the student to send another question.

15. Never repeat the student's question unnecessarily.

16. Do not use unnecessary Markdown symbols.

Do not use:

**
***
###
>>
_
---

Use simple headings such as:

Definition:
Key Points:
Example:
Answer:
Conclusion:

17. Never change the topic.

18. Never answer non-academic questions.

19. Always behave like an exam preparation chatbot.
"""


# =========================================================
# CLEAN AI RESPONSE
# =========================================================

def clean_ai_answer(ai_answer):

    if not ai_answer:

        return ""

    ai_answer = ai_answer.strip()

    ai_answer = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        ai_answer
    )

    ai_answer = re.sub(
        r"###\s*",
        "",
        ai_answer
    )

    ai_answer = re.sub(
        r"^\s*>\s?",
        "",
        ai_answer,
        flags=re.MULTILINE
    )

    return ai_answer.strip()


# =========================================================
# GEMINI RESPONSE
# =========================================================

def get_gemini_answer(prompt):

    response = gemini_client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt
    )

    answer = response.text or ""

    if not answer.strip():

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return clean_ai_answer(answer)


# =========================================================
# GROQ BACKUP RESPONSE
# =========================================================

def get_groq_answer(prompt):

    if not groq_client:

        raise RuntimeError(
            "Groq backup API key is missing."
        )

    completion = groq_client.chat.completions.create(

        model=GROQ_MODEL,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTION
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3,

        max_completion_tokens=4096
    )

    answer = (
        completion
        .choices[0]
        .message
        .content
    )

    if not answer or not answer.strip():

        raise RuntimeError(
            "Groq returned an empty response."
        )

    return clean_ai_answer(answer)


# =========================================================
# HOME / LOGIN ROUTES
# =========================================================

@app.route("/")
def login_page():

    return render_template(
        "login.html"
    )


@app.route("/chat")
def application_page():

    return render_template(
        "index.html"
    )


# =========================================================
# CHAT API
# =========================================================

@app.route(
    "/api/chat",
    methods=["POST"]
)
def chat():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "Invalid request."
            }), 400


        user_message = data.get(
            "message",
            ""
        ).strip()


        if not user_message:

            return jsonify({
                "success": False,
                "error": "Please enter a question."
            }), 400


        # =================================================
        # STUDY / EXAM FILTER
        # =================================================

        if not is_study_exam_question(user_message):

            rejected_answer = (
                "Sorry, I can help only with study and "
                "exam-related questions. Please ask an "
                "academic or exam-related question."
            )

            # Save rejected question to Firebase
            try:

                chat_data = {

                    "question":
                        user_message,

                    "answer":
                        rejected_answer,

                    "answer_type":
                        "outside_scope",

                    "model":
                        "ExamBuddy Filter",

                    "timestamp":
                        datetime.now(
                            timezone.utc
                        ),

                    "type":
                        "chat"
                }

                db.collection(
                    "chat_history"
                ).add(
                    chat_data
                )

            except Exception as firebase_error:

                print(
                    "Firebase Save Error:",
                    firebase_error
                )

            return jsonify({

                "success":
                    True,

                "answer":
                    rejected_answer,

                "model":
                    "ExamBuddy Filter"

            })


        # =================================================
        # DETECT ANSWER TYPE
        # =================================================

        answer_type = detect_answer_type(
            user_message
        )


        # =================================================
        # CREATE PROMPT
        # =================================================

        prompt = f"""

{SYSTEM_INSTRUCTION}

ANSWER TYPE:

{answer_type}

STUDENT QUESTION:

{user_message}

The question has already passed the ExamBuddy academic
topic filter.

Now answer the student's exact academic question.

Important:

If the answer type is "definition",
keep it very short.

If the answer type is "short",
keep it concise.

If marks are explicitly requested,
follow that mark level.

Do not add unnecessary sections.

Do not use markdown symbols.

Do not use ** or ### or >.

Do not ask the student to send another question.

Stay strictly within the academic topic asked by the student.
"""


        # =================================================
        # TRY GEMINI FIRST
        # =================================================

        ai_answer = None

        used_model = "Gemini"

        try:

            print(
                "Trying Gemini..."
            )

            ai_answer = get_gemini_answer(
                prompt
            )

            print(
                "Gemini response successful."
            )


        except Exception as gemini_error:

            print(
                "Gemini failed:"
            )

            print(
                gemini_error
            )

            print(
                "Switching to Groq backup..."
            )


            # =================================================
            # TRY GROQ
            # =================================================

            try:

                ai_answer = get_groq_answer(
                    prompt
                )

                used_model = "Groq"

                print(
                    "Groq backup response successful."
                )


            except Exception as groq_error:

                print(
                    "Groq backup also failed:"
                )

                print(
                    groq_error
                )

                return jsonify({

                    "success": False,

                    "error":
                        "Both Gemini and Groq are currently unavailable."

                }), 500


        # =================================================
        # FINAL CHECK
        # =================================================

        if not ai_answer:

            return jsonify({

                "success":
                    False,

                "error":
                    "Unable to generate an answer."

            }), 500


        # =================================================
        # SAVE TO FIREBASE
        # =================================================

        try:

            chat_data = {

                "question":
                    user_message,

                "answer":
                    ai_answer,

                "answer_type":
                    answer_type,

                "model":
                    used_model,

                "timestamp":
                    datetime.now(
                        timezone.utc
                    ),

                "type":
                    "chat"
            }


            db.collection(
                "chat_history"
            ).add(
                chat_data
            )


        except Exception as firebase_error:

            print(
                "Firebase Save Error:",
                firebase_error
            )


        # =================================================
        # RETURN ANSWER
        # =================================================

        return jsonify({

            "success":
                True,

            "answer":
                ai_answer,

            "model":
                used_model

        })


    except Exception as error:

        print(
            "CHAT API ERROR:",
            error
        )

        return jsonify({

            "success":
                False,

            "error":
                str(error)

        }), 500


# =========================================================
# CLEAR CHAT HISTORY
# =========================================================

@app.route(
    "/api/history",
    methods=["DELETE"]
)
def clear_history():

    try:

        documents = (
            db.collection(
                "chat_history"
            ).stream()
        )


        for document in documents:

            document.reference.delete()


        return jsonify({

            "success":
                True,

            "message":
                "Chat history cleared."

        })


    except Exception as error:

        print(
            "Firebase Error:",
            error
        )

        return jsonify({

            "success":
                False,

            "error":
                str(error)

        }), 500


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            5000
        )
    )


    app.run(

        host="0.0.0.0",

        port=port,

        debug=True

    )