# Prompts for the LLM

EXPLAIN_PROMPT = """
You are an expert tutor. Explain the following to a student clearly and simply:

Context:
{context}

Question:
{question}

Explanation:
"""

QUIZ_PROMPT = """
Given the following material:

{context}

Create a quiz with 3 multiple-choice questions, each with 4 options and the correct answer indicated.
"""

HINT_PROMPT = """
Provide a hint for the question below based on the provided context. Do not give the full answer.

Context:
{context}

Question:
{question}

Hint:
"""

def generate_prompt(template: str, context: str, question: str) -> str:
    return template.format(context=context, question=question)
