from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

def intent_prompt(user_query):
    return f"""
    Role: Intent Classifier for Search query given by the user.
    Task: Check if the query is a valid search query and categorize it into one of the following categories intents:

    Valid query: User's query is clear and valid.
    Output: "valid_query"

    Greeting: User greets the assistant or initiates a conversation.
    Output: "greeting"

    Query not clear: User's query is not clear or ambiguous.
    Output: "query_not_clear"

    Out of scope or context: Applies when the user's request doesn't fit any listed intents or falls beyond the assistant's scope, or the intent is ambiguous.
    Output: "out_of_scope"

    User Query: {user_query}
    Output:"""


def base_prompt(intent, query):
    prompt = f"""You are a WizSearch.AI an search expert that helps answering question. 
    Found that user query is either greetings, ambiguous, not clear or out of scope. Please provide appropriate response to the user.
    
    User query: {query}
    Intent: {intent}

    Response:
    """
    return prompt

def search_rag_prompt(search_results, history=None):
    system_prompt = f"""You are a WizSearch.AI an search expert that helps answering question, 
    utilize the search information to their fullest potential to provide additional information and assistance in your response.
    SEARCH INFORMATION is below:
    ---------------------
    {search_results}
    ---------------------
    RULES:
    1. Only Answer the USER QUESTION using the INFORMATION.
    2. Include source link and images in the answer.
    3. Respond in markdown format.
    """
    
    messages = [
        SystemMessage(content=system_prompt)
    ]
    if history is not None:
        for message in history:
            if message["role"] == "user":
                messages.append(HumanMessage(content=message["content"]))
            else:
                messages.append(AIMessage(content=message["content"]))

    return messages