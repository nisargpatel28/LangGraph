from fastapi import FastAPI
from fastapi.responses import JSONResponse
import openai
from pydantic import BaseModel
from agent import DoctorAppointmentAgent
from langchain_core.messages import HumanMessage
import os

os.environ.pop("SSL_CERT_FILE", None)


app = FastAPI()

# Define Pydantic model to accept request body


class UserQuery(BaseModel):
    id_number: int
    messages: str


agent = DoctorAppointmentAgent()


@app.post("/execute")
def execute_agent(user_input: UserQuery):
    app_graph = agent.workflow()

    # Prepare agent state as expected by the workflow
    input = [
        HumanMessage(content=user_input.messages)
    ]
    query_data = {
        "messages": input,
        "id_number": user_input.id_number,
        "next": "",
        "query": "",
        "current_reasoning": "",
    }

    try:
        response = app_graph.invoke(query_data, config={"recursion_limit": 20})
        return {"messages": response["messages"]}
    except Exception as e:
        # Prefer to catch OpenAI quota/rate-limit errors specifically
        err_name = type(e).__name__
        err_str = str(e)
        if hasattr(openai, "RateLimitError") and isinstance(e, openai.RateLimitError):
            return JSONResponse(status_code=503, content={"error": "OpenAI quota exceeded or rate limited. Check account billing/usage."})
        # Fallback: if the exception class name indicates rate limit, return 503
        if "RateLimit" in err_name or "quota" in err_str.lower():
            return JSONResponse(status_code=503, content={"error": "OpenAI quota exceeded or rate limited. Check account billing/usage.", "detail": err_str})
        # Otherwise return a generic 500 with message
        return JSONResponse(status_code=500, content={"error": "Internal server error", "detail": err_str})
