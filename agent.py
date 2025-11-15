from typing import Literal, List, Any
from langchain_core.tools import tool
from langgraph.types import Command
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from langchain_core.prompts.chat import ChatPromptTemplate
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from prompt_library.prompt import system_prompt
from utils.llms import LLMModel
from toolkit.toolkits import *


class Router(TypedDict):
    next: Literal["information_node", "booking_node", "FINISH"]
    reasoning: str


class AgentState(TypedDict):
    messages: Annotated[list[Any], add_messages]
    id_number: int
    next: str
    query: str
    current_reasoning: str


class DoctorAppointmentAgent:
    def __init__(self):
        llm_model = LLMModel()
        self.llm_model = llm_model.get_model()

    def supervisor_node(self, state: AgentState) -> Command[Literal['information_node', 'booking_node', '__end__']]:
        print("**************************below is my state right after entering****************************")
        print(state)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",
                "content": f"user's identification number is {state['id_number']}"},
        ] + state["messages"]

        print("***********************this is my message*****************************************")
        print(messages)

        # query = state['messages'][-1].content if state["messages"] else ""
        query = ''
        if len(state['messages']) == 1:
            query = state['messages'][0].content

        print("************below is my query********************")
        print(query)

        response = self.llm_model.with_structured_output(
            Router).invoke(messages)

        goto = response["next"]

        print("********************************this is my goto*************************")
        print(goto)

        print("********************************")
        print(response["reasoning"])

        if goto == "FINISH":
            goto = END

        print("**************************below is my state****************************")
        print(state)

        if query:
            return Command(goto=goto, update={'next': goto,
                                              'query': query,
                                              'current_reasoning': response["reasoning"],
                                              'messages': [HumanMessage(content=f"user's identification number is {state['id_number']}")]
                                              })
        return Command(goto=goto, update={'next': goto,
                                          'current_reasoning': response["reasoning"]}
                       )

    def information_node(self, state: AgentState) -> Command[Literal['supervisor']]:
        print("*****************called information node************")

        system_prompt = "You are specialized agent to provide information related to availability of doctors or any FAQs related to hospital based on the query. You have access to the tool.\n Make sure to ask user politely if you need any further information to execute the tool.\n For your information, Always consider current year is 2024."

        system_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt
                ),
                (
                    "placeholder",
                    "{messages}"
                ),
            ]
        )

        information_agent = create_react_agent(model=self.llm_model, tools=[
                                               check_availability_by_doctor, check_availability_by_specialization], prompt=system_prompt)

        result = information_agent.invoke(state)

        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=result["messages"]
                              [-1].content, name="information_node")
                    # HumanMessage(content=result["messages"][-1].content, name="information_node")
                ]
            },
            goto="supervisor",
        )

    def booking_node(self, state: AgentState) -> Command[Literal['supervisor']]:
        print("*****************called booking node************")

        system_prompt = "You are specialized agent to set, cancel or reschedule appointment based on the query. You have access to the tool.\n Make sure to ask user politely if you need any further information to execute the tool.\n For your information, Always consider current year is 2024."

        system_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt
                ),
                (
                    "placeholder",
                    "{messages}"
                ),
            ]
        )
        booking_agent = create_react_agent(model=self.llm_model, tools=[
                                           set_appointment, cancel_appointment, reschedule_appointment], prompt=system_prompt)

        result = booking_agent.invoke(state)

        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=result["messages"]
                              [-1].content, name="booking_node")
                    # HumanMessage(content=result["messages"][-1].content, name="booking_node")
                ]
            },
            goto="supervisor",
        )

    def workflow(self):
        self.graph = StateGraph(AgentState)
        self.graph.add_node("supervisor", self.supervisor_node)
        self.graph.add_node("information_node", self.information_node)
        self.graph.add_node("booking_node", self.booking_node)
        self.graph.add_edge(START, "supervisor")
        self.app = self.graph.compile()
        return self.app
