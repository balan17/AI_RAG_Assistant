from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
import ollama


# Load embedding model
embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)
chat_memory = []
# Load existing vector database
vector_db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)
def hybrid_search(question):

    # vector search
    vector_docs = vector_db.similarity_search(question, k=3)

    # keyword filter
    keyword_docs = []
    words = question.lower().split()

    all_docs = vector_db.get()['documents']

    for doc in all_docs:
        if any(word in doc.lower() for word in words):
            keyword_docs.append(doc)

    # merge both
    combined = []

    for d in vector_docs:
        combined.append(d.page_content)

    for d in keyword_docs:
        if d not in combined:
            combined.append(d)

    return combined[:3]

def ask_ai(question):

    # Retrieve relevant documents
    docs = hybrid_search(question)
    # If no documents found
    if not docs:
        return "I could not find this issue in the knowledge base."

    # Combine retrieved document chunks
    context = "\n".join(docs)

    # Strict prompt to avoid hallucination
    prompt = f"""
You are a friendly Industrial Hardware Support AI.
Your job is to help technicians solve device problems.
Answer step-by-step using short lines.
IMPORTANT RESPONSE RULES:
- First give a short friendly introduction (1 line).
- Then explain the solution step by step.
- Use short lines, not long paragraphs.
- Do NOT repeat the entire document.
- Explain only the relevant information needed to solve the problem.
- Sound like a human support engineer.

Use this HTML structure exactly:

<div class="ai-response">

<p class="ai-intro">
Give a short helpful introduction.
</p>

<div class="ai-section">
<span class="ai-label">🔧 Solution</span>
<ul>
<li>Step 1 explanation</li>
<li>Step 2 explanation</li>
<li>Step 3 explanation</li>
</ul>
</div>

<div class="ai-section">
<span class="ai-label">⚠️ Possible Cause</span>
<ul>
<li>Cause 1</li>
<li>Cause 2</li>
</ul>
</div>

<p class="ai-footer">
Ask the user if they need more help.
</p>

</div>

Knowledge Base:
{context}

User Question:
{question}

Respond only in the HTML format above.
"""

    # Ask local LLM using Ollama
    response = ollama.chat(
    model="llama3",
    options={
        "temperature": 0.2,
        "num_predict": 300
    },
    messages=[
        {"role": "user", "content": prompt}
    ]
)
    # Extract response text
    answer = response["message"]["content"]

    return answer

def stream_ai(question):
    global chat_memory
    docs = hybrid_search(question)

    if not docs:
        yield "I could not find this issue in the knowledge base."
        return

    context = "\n".join(docs)
    chat_memory.append(f"User: {question}")
    conversation = "\n".join(chat_memory[-6:]) 
    prompt = f"""
You are a friendly Industrial Hardware Support AI.
Your job is to help technicians solve device problems.
Answer step-by-step using short lines.
Use the conversation history to understand follow-up questions.
IMPORTANT RESPONSE RULES:
- First give a short friendly introduction (1 line).
- Then explain the solution step by step.
- Use short lines, not long paragraphs.
- Do NOT repeat the entire document.
- Explain only the relevant information needed to solve the problem.
- Sound like a human support engineer.

Use this HTML structure exactly:

<div class="ai-response">

<p class="ai-intro">
Give a short helpful introduction.
</p>

<div class="ai-section">
<span class="ai-label">🔧 Solution</span>
<ul>
<li>Step 1 explanation</li>
<li>Step 2 explanation</li>
<li>Step 3 explanation</li>
</ul>
</div>

<div class="ai-section">
<span class="ai-label">⚠️ Possible Cause</span>
<ul>
<li>Cause 1</li>
<li>Cause 2</li>
</ul>
</div>

<p class="ai-footer">
Ask the user if they need more help.
</p>

</div>
Conversation History:
{conversation}
Knowledge Base:
{context}

User Question:
{question}

Respond only in the HTML format above.
"""
    stream = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    full_answer = ""
    for chunk in stream:
        token = chunk["message"]["content"]
        full_answer += token
        yield token
    # Save AI reply in memory
    chat_memory.append(f"AI: {full_answer}")