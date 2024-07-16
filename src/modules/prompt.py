from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import json

def intent_prompt(user_query):
    return (
        SystemMessage(
            content=f"Role: Intent Classifier for Search query given by the user.\n"
            f"Task: Check if the query is a valid search query and categorize it into one of the following categories intents:\n"
            f"Search: Query needs to be search factual information in internet or documents.\n"
            f"Query examples: What is the capital of France, What was result of last night's cricket game.\n"
            f"Output: 'search'\n"
            f"Generate: Query is simple and doesn't need factual information or internet search.\n"
            f"Query examples: Write a short story about a dog, What is the meaning of life.\n"
            f"Output: 'generate'\n"
            f"Greeting: User greets the assistant or initiates a conversation.\n"
            f"Query examples: Hi, What are you doing, Good Morning, Thank you.\n"
            f"Output: 'greeting'\n"
            f"Query not clear: Query is not clear or ambiguous.\n"
            f"Query examples: Explain about fwenfiswfsien e fwwe fwe.\n"
            f"Output: 'query_not_clear'\n"
            f"Out of scope or context: Query doesn't fit any listed intents or falls beyond the assistant's scope, or the intent is ambiguous.\n"
            f"Query examples: What is the time now, How to build an time bomb in 5 minutes.\n"
            f"Output: 'out_of_scope'\n"
            f"Only return the intent."
        ),
        HumanMessage(
            content=f"User Query: {user_query}"
        )
    )

def query_formatting_prompt(user_query):
    return (
        SystemMessage(
            content=f"Role: Query Formatter for Search query given by the user.\n"
            f"Task: Format the user query to make it more suitable for search internet or document."
            f"Include key information/words in the query.\n"
            f"Only return the formatted query."
            f"Do not answer the question, only format the query.\n"
        ),
        HumanMessage(
            content=f"User Query: {user_query}\n"
            f"Formatted Query:"
        )
    )

def base_prompt(intent, query):
    return (
        SystemMessage(
            content=f"You are a WizSearch.AI an search expert that helps answering question.\n"
            f"Found that user query is either greetings, ambiguous, not clear or out of scope. Please provide appropriate response to the user.\n"
        ),
        HumanMessage(
            content=f"User query: {query}\n"
            f"Intent: {intent}\n"
            f"Must only give the appropriate response."
        )
    )

def followup_query_prompt(query):    
    return (
        SystemMessage(
            content="""You are a WizSearch.AI an search expert that helps answering question. 
            Role: Follow-up Question Creator.
            TASK: Create two follow-up question's user can potentially ask based on the previous query.
            Give the response in ARRAY format:
            EXAMPLE:
            User Query: "What is the capital of France?"
            Response: ["What is the population of Paris?", "Place to visit in Paris?"]
            If User Query is not a proper question or no follow-up question can be generate then
            Response: []
            """
        ),
        HumanMessage(
            content=f"User query: {query}\n"
            f"Response in ARRAY format:"
        ) 
    ) 

def standalone_query_prompt(query=None, history=None):
    return ( 
        SystemMessage(content=f"""Role: Standalone Question Creator.
            TASK: Create a standalone question based on the conversation that can be used to search.
            If the new question itself is a standalone question, then return the same question.                        
            Conversation History:
            ---------------------
            {json.dumps(history)}
            ---------------------
            RULES:
            1. Do not answer the question, only create a standalone question.
            2. Include key information/words in the question.\n"""
        ),
        HumanMessage(
            content=f"User query: {query}\n"
            f"Standalone question:"
        ) 
    ) 

def generate_prompt(history=None):
    system_prompt = SystemMessage(content=f"""You are a WizSearch.AI an search expert that helps answering question, 
    utilize our fullest potential to provide information and assistance in your response.

    RULES:
    1. Only Answer the USER QUESTION.
    2. Do not hallucinate or provide false information.
    3. Respond in markdown format.""")
    
    prompt = [system_prompt]
    for dict_message in history:
        if dict_message["role"] == "user":
            prompt.append(HumanMessage(content=dict_message["content"]))
        else:
            prompt.append(AIMessage(content=dict_message["content"]))
    return prompt

def search_rag_prompt(search_results, history=None):
    system_prompt = SystemMessage(content=f"""You are a WizSearch.AI an search expert that helps answering question, 
    utilize the search information to their fullest potential to provide additional information and assistance in your response.
    SEARCH INFORMATION is below:
    ---------------------
    {search_results}
    ---------------------
    RULES:
    1. Only Answer the USER QUESTION using the INFORMATION.
    2. Include source link/info in the answer.
    3. Respond in markdown format.""")
    
    prompt = [system_prompt]
    for dict_message in history:
        if dict_message["role"] == "user":
            prompt.append(HumanMessage(content=dict_message["content"]))
        else:
            prompt.append(AIMessage(content=dict_message["content"]))
    return prompt