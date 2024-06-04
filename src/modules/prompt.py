from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

def intent_prompt(user_query):
    return (
        SystemMessage(
            content=f"Role: Intent Classifier for Search query given by the user.\n"
            f"Task: Check if the query is a valid search query and categorize it into one of the following categories intents:\n"
            f"Valid query: User's query is clear and valid.\n"
            f"Output: 'valid_query'\n"
            f"Greeting: User greets the assistant or initiates a conversation.\n"
            f"Output: 'greeting'\n"
            f"Query not clear: User's query is not clear or ambiguous.\n"
            f"Output: 'query_not_clear'\n"
            f"Out of scope or context: Applies when the user's request doesn't fit any listed intents or falls beyond the assistant's scope, or the intent is ambiguous.\n"
            f"Output: 'out_of_scope'\n"
        ),
        HumanMessage(
            content=f"User Query: {user_query}"
        )
    )

def query_formatting_prompt(user_query):
    return (
        SystemMessage(
            content=f"Role: Query Formatter for Search query given by the user.\n"
            f"Task: Format the user query to make it more suitable for search.\n"
            f"Only return the formatted query."
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
            Response: ["What is the population of Paris?", "Place to visit in Paris?"]"""
        ),
        HumanMessage(
            content=f"User query: {query}\n"
            f"Response in ARRAY format:"
        ) 
    ) 

def standalone_query_prompt(history=None):
    system_prompt = SystemMessage(content=f"""Role: Standalone Question Creator.
    TASK: Create a standalone question based on the conversation that can be used to search.
    If the new question itself is a standalone question, then return the same question.

    RULES:
    1. Do not answer the question, only create a standalone question.
    2. Include key information/words in the question.\n""")
    
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