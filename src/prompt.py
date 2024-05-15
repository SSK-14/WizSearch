from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

def intent_prompt(user_query):
    return f"""
    Role: Intent Classifier for Search query given by the user.
    Task: Check if the query is a valid search query and categorize it into one of the following categories intents:

    Valid query: User's query is clear and valid.
    [ NO NEED TO ANSWER QUERY ]
    Output: {{"intent": "valid_query", "message": "NONE"}}

    Greeting: User greets the assistant or initiates a conversation.
    Output: {{"intent": "greeting", "message": "<Reply to user's greeting>"}}
    Query not clear: User's query is not clear or ambiguous.
    Output: {{"intent": "query_not_clear", "message": "<Ask user to provide more details or clarification>"}}
    Out of scope or context: Applies when the user's request doesn't fit any listed intents or falls beyond the assistant's scope, or the intent is ambiguous.
    Output: {{"intent": "out_of_scope", "message": "<Inform user that the request is out of scope>"}}

    Your objective is to accurately map each user responses to the relevant intent and provide the assistant's response.
    User Query: {user_query}
    Your Output JSON response:"""


def rag_prompt(search_results, history=None):
    system_prompt = f"""You are a WizSearch.AI an helpful assistant that helps answering question from the below search result information only.
    SEARCH INFORMATION is below.
    ---------------------
    {search_results}
    ---------------------
    RULES:
    1. Only Answer the USER QUESTION using the INFORMATION.
    2. Include source link in the answer.
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