from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import json, time
from src.utils import image_data

 
def intent_prompt(user_query):
    return (
        SystemMessage(
            content=f"Role: Intent Classifier for Search query given by the user.\n"
            f"Task: Check if the query is a valid search query and categorize it into one of the following categories intents:\n"
            f"Search: Query needs to be search factual information in internet or documents.\n"
            f"Query examples: [ What is the capital of France, What was result of last night's cricket game, Who is the president of USA, What are the symptoms of COVID-19, Who won the 2022 FIFA World Cup, What is the stock price of Tesla today, How do I renew my passport online, What is the population of India, What are the latest trends in AI development, What is the weather forecast for tomorrow in London ]\n"
            f"Output: 'search'\n"
            f"Generate: Query is simple and doesn't need factual information or internet search.\n"
            f"Query examples: [ Write a short story about a dog, What is the meaning of life, Create a motivational speech for a team of engineers, Describe a futuristic city in 2050, What is your opinion on AI and ethics, Suggest some creative ideas for a birthday party, What is a unique gift idea for a friend, Draft an email apologizing for a late response, Imagine an alternative ending for Romeo and Juliet ]\n"
            f"Output: 'generate'\n"
            f"NOTE: When you are not sure about generate or search, choose search.\n"
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
    current_date = time.strftime("%Y-%m-%d")
    return (
        SystemMessage(
            content=f"Role: Query Formatter for Search query given by the user.\n"
            f"Task: Format the user query to make it more suitable for search internet or document.\n"
            f"Include key information/words in the query.\n"
            f"Only return the formatted query."
            f"Do not answer the question, only format the query.\n"
        ),
        HumanMessage(
            content=f"Todays Date: {current_date}\n"
            f"User Query: {user_query}\n"
            f"Formatted Query:"
        )
    )


def key_points_prompt(text):
    return (
        SystemMessage(
            content=f"""Role: You are a extractive summarization expert.\n
            Goal: Identifies key sentences within the document using technique TF-IDF.
            Do not mention about the technique used.\n
            Instructions: 
            1. Make sure you include most important points only.
            2. Must Only include max 5 points. Keep it short and concise.
            3. Do not include any examples, links, repeated content. 
            4. Use the exact same words/sentences.
            5. Only return the key points. No explanation needed.\n"""
        ),
        HumanMessage(
            content=f"""Given document content: 
            ---------------------
            {text}
            ---------------------
            Only Key Points:"""
        )
    )

def summary_prompt(query, text):
    return (
        SystemMessage(
            content=f"""Role: You are a extractive summarization expert.\n
            Goal: Only use the documents content below to answer the user question.\n
            Instructions: 
            1. Make sure you include most important points.
            2. Use the exact same words/sentences. Do not hallucinate.
            3. Keep it short and concise.
            Documents content:
            ---------------------
            {text}
            ---------------------
            """
        ),
        HumanMessage(
            content=f"""User query: {query}\n 
            Answer:"""
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


def followup_query_prompt(history=None):
    query = history[-1]["content"]
    chat_history = None
    if len(history) > 2:
        chat_history = "Previous user questions: "
        chat_history += "\n".join([
            f"{message['content']}" if message["role"] == "user" else ""
            for message in history[:-1]
        ])

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
            Rules:
            If not sure or no need for follow-up question then Response: []
            Do not answer the question, only create follow-up questions.\n"""
        ),
        HumanMessage(
            content=f"{chat_history if chat_history else ''}\n"
            f"Current User query: {query}\n"
            f"Response in ARRAY format:"
        ) 
    ) 


def standalone_query_prompt(query=None, history=None):
    chat_history = "\n".join([
        f"User question: {message['content']}" if message["role"] == "user" else 
        f"Assistant: {message['content'][:100]}..." if len(message["content"]) > 100 else 
        f"Assistant: {message['content']}"
        for message in history[1:]
    ])

    return ( 
        SystemMessage(content=f"""Role: Standalone Question Creator.
            TASK: Create a standalone question based on the conversation that can be used to search.
            If the new question itself is a standalone question, then return the same question.                        
            Conversation History:
            ---------------------
            {chat_history}
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


def generate_prompt(query, history=None, image_data=None):
    if image_data:
        image_prompt = []
        for image in image_data:
            image_prompt.append({"type": "image_url", "image_url": {"url": image}})

    system_prompt = SystemMessage(content=f"""You are a WizSearch.AI an search expert that helps answering question, 
    utilize your fullest potential to provide information and assistance in your response.

    RULES:
    1. Only Answer the USER QUESTION.
    2. Do not hallucinate or provide false information.
    3. Respond in markdown format.""")
    
    prompt = [system_prompt]
    for dict_message in history:
        if dict_message["role"] == "user":
            if dict_message == history[-1]:
                if image_data:
                    prompt.append(HumanMessage(content=[{"type": "text", "text": f"User query: {query}"}] + image_prompt))
                else:
                    prompt.append(HumanMessage(content=f"User query: {query}"))
                break
            prompt.append(HumanMessage(content=dict_message["content"]))
        else:
            prompt.append(AIMessage(content=dict_message["content"]))
    return prompt


def search_rag_prompt(search_results,  history=None, image_urls=[]):
    image_prompt = []
    image_instructions = None
    images = []
    if image_urls and len(image_urls):
        for image in image_urls:
            base64_image = image_data(image)
            if base64_image:
                images.append(image)
                image_prompt.append({"type": "image_url", "image_url": {"url": base64_image}})
            if len(image_prompt) == 2:
                break

    if len(images):    
        image_instructions = f"{'Images:'+json.dumps(images)}\n Add only necessary images in the response only if needed.\n Focus on the user query and search information."

    system_base_prompt = f"""You are a WizSearch.AI an search expert that helps answering question, 
    utilize the search information to their fullest potential to provide additional information and assistance in your response.

    RULES:
    1. Only Answer the USER QUESTION using the INFORMATION.
    2. If answer is not in the search information, then respond politely as could not find answer.
    3. Include source link as reference in answer.
    4. Respond in markdown format."""

    user_prompt = f"""SEARCH INFORMATION is below:
    ---------------------
    {search_results}
    ---------------------
    {image_instructions if image_instructions else ""}
    User query: {history[-1]["content"]}"""

    system_prompt = SystemMessage(content=system_base_prompt)
    
    prompt = [system_prompt]
    for dict_message in history:
        if dict_message["role"] == "user":
            if dict_message == history[-1]:
                if len(image_prompt) > 0:
                    prompt.append(HumanMessage(content=[{"type": "text", "text": user_prompt}] + image_prompt))
                else:
                    prompt.append(HumanMessage(content=user_prompt))
                break
            prompt.append(HumanMessage(content=dict_message["content"]))
        else:
            prompt.append(AIMessage(content=dict_message["content"]))

    
    return prompt