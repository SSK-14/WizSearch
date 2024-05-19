def intent_prompt(user_query):
    return f"""<|im_start|>system\nRole: Intent Classifier for Search query given by the user.
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
    Output:<|im_end|>\n
    <|im_start|>assistant\n"""

def query_formatting_prompt(user_query):
    return f"""<|im_start|>system\nRole: Query Formatter for Search query given by the user.
    Task: Format the user query to make it more suitable for search.
    User Query: {user_query}
    Only return the formatted query.<|im_end|>\n
    <|im_start|>assistant\n Formatted Query:"""

def base_prompt(intent, query):
    prompt = f"""<|im_start|>system\nYou are a SearchWiz.AI an search expert that helps answering question. 
    Found that user query is either greetings, ambiguous, not clear or out of scope. Please provide appropriate response to the user.
    User query: {query}
    Intent: {intent}
    Must only give the appropriate response.
    <|im_end|>\n
    <|im_start|>assistant\n
    """
    return prompt

def followup_query_prompt(query):
    prompt = f"""<|im_start|>system\nYou are a SearchWiz.AI an search expert that helps answering question. 
    Role: Follow-up Question Creator.
    TASK: Create two follow-up question's user can potentially ask based on the previous query.
    Give the response in ARRAY format:
    EXAMPLE:
    User Query: "What is the capital of France?"
    Response: ["What is the population of Paris?", "Place to visit in Paris?"]
    <|im_end|>\n
    <|im_start|>assistant\n
    User query: {query}
    Response:
    <|im_end|>\n
    """
    return prompt

def standalone_query_prompt(history=None):
    system_prompt = f"""<|im_start|>system\nRole: Standalone Question Creator.
    TASK: Create a standalone question based on the conversation that can be used to search.
    If the new question itself is a standalone question, then return the same question.

    RULES:
    1. Do not answer the question, only create a standalone question.
    2. Include key information/words in the question.
    <|im_end|>\n
    """
    
    prompt = [system_prompt]
    for dict_message in history:
        if dict_message["role"] == "user":
            prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
        else:
            prompt.append("<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>")
    
    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    return prompt_str

def search_rag_prompt(search_results, history=None):
    system_prompt = f"""<|im_start|>system\nYou are a SearchWiz.AI an search expert that helps answering question, 
    utilize the search information to their fullest potential to provide additional information and assistance in your response.
    SEARCH INFORMATION is below:
    ---------------------
    {search_results}
    ---------------------
    RULES:
    1. Only Answer the USER QUESTION using the INFORMATION.
    2. Include source link and images in the answer.
    3. Respond in markdown format.
    <|im_end|>\n
    """
    
    prompt = [system_prompt]
    for dict_message in history:
        if dict_message["role"] == "user":
            prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
        else:
            prompt.append("<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>")
    
    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    return prompt_str