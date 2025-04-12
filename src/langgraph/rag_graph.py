from typing import Dict, List, Any, TypedDict, Annotated, Sequence, Literal
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import operator
from langraph import graph, module
from pydantic import BaseModel, Field
from src.utils.index_manager import IndexManager
from src.utils.llm_client import LLMClient
from src.models.prompts import SystemPrompts, PromptTemplates

# Define state types
class RAGState(TypedDict):
    query: str
    user_id: str
    retrieved_docs: List[Dict[str, Any]]
    context: str
    system_prompt: str
    prompt_template: str
    response: str
    recipe_list: List[str]
    structured_suggestions: List[Dict[str, Any]]
    output_type: Literal["text", "recipe_list", "structured"]

# Function to retrieve documents using the index
def retrieve_documents(state: RAGState, index_manager: IndexManager) -> RAGState:
    """
    Retrieve relevant documents from the user's index
    """
    query = state["query"]
    user_id = state["user_id"]
    
    # Get relevant documents
    docs = index_manager.search(user_id, query, k=10)
    
    # Format documents into a context string
    context = "\n".join([
        f"- {doc['text']}" for doc in docs
    ])
    
    return {
        **state,
        "retrieved_docs": docs,
        "context": context if context else "No inventory data found."
    }

# Function to generate LLM response
def generate_response(state: RAGState, llm_client: LLMClient) -> RAGState:
    """
    Generate LLM response based on the query and context
    """
    # Fill the prompt template with context and query
    user_prompt = state["prompt_template"].format(
        context=state["context"],
        query=state["query"]
    )
    
    # Get response from LLM
    response = llm_client.generate_response(
        system_prompt=state["system_prompt"],
        user_prompt=user_prompt
    )
    
    return {**state, "response": response}

# Function to format recipe list response
def format_recipe_list(state: RAGState, llm_client: LLMClient) -> RAGState:
    """
    Parse response into a list of recipe names
    """
    response = state["response"]
    recipe_list = llm_client.parse_recipe_list(response)
    
    return {**state, "recipe_list": recipe_list}

# Function to format structured recipe suggestions
def format_structured_suggestions(state: RAGState, llm_client: LLMClient) -> RAGState:
    """
    Parse response into structured recipe suggestions
    """
    response = state["response"]
    suggestions = llm_client.parse_structured_suggestions(response)
    
    return {**state, "structured_suggestions": suggestions}

# Define edge condition functions
def should_format_recipe_list(state: RAGState) -> bool:
    return state["output_type"] == "recipe_list"

def should_format_structured(state: RAGState) -> bool:
    return state["output_type"] == "structured"

def should_return_text(state: RAGState) -> bool:
    return state["output_type"] == "text"

# Get appropriate initial state based on query type
def get_initial_state(query: str, user_id: str, output_type: str = "text") -> RAGState:
    """
    Get initial state based on query type
    """
    if output_type == "recipe_list":
        system_prompt = SystemPrompts.RECIPE_LIST_SYSTEM_PROMPT
        prompt_template = PromptTemplates.RECIPE_QUERY_TEMPLATE
    elif output_type == "structured":
        system_prompt = SystemPrompts.STRUCTURED_RECIPE_SYSTEM_PROMPT
        prompt_template = PromptTemplates.STRUCTURED_RECIPE_TEMPLATE
    else:  # Default: text response
        system_prompt = SystemPrompts.GENERAL_SYSTEM_PROMPT
        prompt_template = PromptTemplates.GENERAL_QUERY_TEMPLATE
    
    return {
        "query": query,
        "user_id": user_id,
        "retrieved_docs": [],
        "context": "",
        "system_prompt": system_prompt,
        "prompt_template": prompt_template,
        "response": "",
        "recipe_list": [],
        "structured_suggestions": [],
        "output_type": output_type
    }

# Create RAG workflow
def create_rag_workflow(index_manager: IndexManager, llm_client: LLMClient):
    """
    Create a LangGraph workflow for the RAG system
    """
    # Define the workflow
    builder = graph.StateGraph(RAGState)
    
    # Add nodes
    builder.add_node("retrieve_documents", lambda state: retrieve_documents(state, index_manager))
    builder.add_node("generate_response", lambda state: generate_response(state, llm_client))
    builder.add_node("format_recipe_list", lambda state: format_recipe_list(state, llm_client))
    builder.add_node("format_structured_suggestions", lambda state: format_structured_suggestions(state, llm_client))
    
    # Set the entry point
    builder.set_entry_point("retrieve_documents")
    
    # Define edges
    builder.add_edge("retrieve_documents", "generate_response")
    
    # Add conditional edges from generate_response
    builder.add_conditional_edges(
        "generate_response",
        # If output_type is recipe_list, go to format_recipe_list
        # If output_type is structured, go to format_structured_suggestions
        # Otherwise, we're done (implicit END node)
        {should_format_recipe_list: "format_recipe_list",
         should_format_structured: "format_structured_suggestions",
         should_return_text: graph.END}
    )
    
    # Add end nodes
    builder.add_edge("format_recipe_list", graph.END)
    builder.add_edge("format_structured_suggestions", graph.END)
    
    # Compile the graph
    return builder.compile()

# Invoke RAG workflow
def invoke_rag(query: str, user_id: str, output_type: str, index_manager: IndexManager, llm_client: LLMClient) -> Dict[str, Any]:
    """
    Invoke the RAG workflow
    
    Args:
        query: User's question
        user_id: User ID for retrieving inventory data
        output_type: Type of output (text, recipe_list, or structured)
        index_manager: IndexManager instance
        llm_client: LLMClient instance
        
    Returns:
        Final state containing the response
    """
    # Get appropriate initial state
    initial_state = get_initial_state(query, user_id, output_type)
    
    # Create workflow
    rag_workflow = create_rag_workflow(index_manager, llm_client)
    
    # Invoke workflow
    final_state = rag_workflow.invoke(initial_state)
    
    return final_state