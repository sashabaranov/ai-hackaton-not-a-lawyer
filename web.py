from fasthtml.common import *
import uvicorn
from langchain_community.document_loaders import PyPDFLoader
import tempfile
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel
from enum import Enum
import chromadb


class ColorEnum(str, Enum):
    red = "red"
    yellow = "yellow"
    green = "green"


class LegalAgreementResponse(BaseModel):
    suspicion_color: ColorEnum
    legislation_searches: list[str]
    most_unusual_terms: list[str]


load_dotenv()
app = FastHTML(hdrs=(picolink,))
openai_client = AsyncOpenAI()
openai_client_sync = OpenAI()
chroma_client = chromadb.PersistentClient(path="./chroma.db")
collection = chroma_client.get_collection(name="legislation")


non_html_prompt_intro = """
Only reply with HTML. Don't add any ` symbols such as ```html.
"""

prompt = """
You are Saul, an exceptionally helpful and polite AI assistant who loves working with legal agreements. Your role is to review residential rental agreements for users in the UK, providing a concise yet thorough overview of the agreement's main terms. You are friendly, professional, and careful to guide the user through the process while making recommendations as necessary.

When reviewing the agreement provided, follow these steps:

1. Greeting & Introduction:
   Start by greeting the user in a polite and friendly tone. Introduce yourself as Saul, explain that you’ve read the agreement, if it was provided, or you are happy to read the agreement. Inform them that you're about to give an overview of the main terms and some recomendations. Be clear, concise, and courteous in your tone. Claim that you know a thing or two on UK rental market.

2. Refer to the documents attached to review the terms. Make sure to check against all of the terms mentioned in the attached instructions. 
And return the details on every one of them. 
Give consice short opinion on them - standard/non-standard, benefits tenant, benefits landlord.

4. Make short highlight of the most unusual or not tenant friendly terms.

5. Recommendations to Consult a Lawyer:
   After summarizing the agreement and providing opinions on each key term, always recommend the user seek advice from a qualified lawyer or legal expert as you are not a lawyer. This ensures the user understands that your feedback is informative but not a substitute for professional legal counsel.

6. Empathy and Assistance:
   Throughout the review, maintain a helpful and approachable tone. If certain clauses seem restrictive or potentially problematic, express concern in a supportive way and suggest consulting with a legal professional for a more comprehensive evaluation.

Important Note for the Assistant:
You must not rely on your internal knowledge to determine whether terms are standard or non-standard. Instead, you should pull data from the attached Instructions file.
"""


@app.route("/")
def get():
    add = Form(
        Group(Input(id="myFile", type="file"), Button("Add")),
        hx_post="/",
        target_id="todo-list",
        hx_swap="beforeend",
    )
    card = Div(id="todo-list")
    title = "Not an AI Lawyer"
    return Title(title), Main(H1(title), add, card, cls="container")


@app.route("/")
async def post(myFile: UploadFile):
    print(myFile)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
        contents = await myFile.read()
        temp_pdf.write(contents)
        file_path = temp_pdf.name
        loader = PyPDFLoader(file_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)

        print(f"Pages: {str(pages)[:200]}")

        print("Reaching out to openai")
        text_completion = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": f"{non_html_prompt_intro}{prompt} Here's my contract: {str(pages)}",
                }
            ],
        )

        print("Reaching out to openai [structured]")
        structure_completion = await openai_client.beta.chat.completions.parse(
            model="gpt-4o",  # "o1-preview",
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt} Here's my contract: {str(pages)}",
                }
            ],
            response_format=LegalAgreementResponse,
        )

        output = structure_completion.choices[0].message.parsed

        results = collection.query(
            query_texts=output.legislation_searches or ["rental"], n_results=3
        )
        relevant_docs = []
        for query_docs in results["documents"]:
            for doc in query_docs:
                relevant_docs.append("<p>" + str(doc).replace("\n", "</br>") + "</p>")

        return (
            text_completion.choices[0].message.content
            + "<h2>Relevant documents</h2>"
            + str("".join(relevant_docs))
        )

    return "No response"


serve()
