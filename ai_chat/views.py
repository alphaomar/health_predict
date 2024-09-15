

# import ollama
# from django.shortcuts import render
# from django.http import StreamingHttpResponse
# from django.views.decorators.csrf import csrf_exempt
#
# def generate_response(prompt):
#     try:
#         stream = ollama.chat(
#             model='llama3',
#             messages=[{'role': 'user', 'content': prompt}],
#             stream=True,
#         )
#         for chunk in stream:
#             yield chunk['message']['content']
#     except Exception as e:
#         yield str(e)
#
# @csrf_exempt
# def chat_view(request):
#     if request.method == "POST":
#         try:
#             user_input = request.POST["user_input"]
#             prompt = f"You are a highly experienced doctor with over 22 years of experience. Answer the following query as an expert:\n\nUser: {user_input}\nAI:"
#             response = generate_response(prompt)
#             return StreamingHttpResponse(response, content_type='text/plain')
#         except Exception as e:
#             return StreamingHttpResponse(str(e), content_type='text/plain')
#     return render(request, "ai/chat.html")
import logging
import ollama
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_response(prompt):
    """
    Generate a response from the ollama model.
    """
    try:
        # Use a specific model and adjust the streaming and logging as needed
        stream =ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': prompt}],
            stream=True,
        )

        # Yield each chunk of the response
        for chunk in stream:
            yield chunk['message']['content']
    except Exception as e:
        # Log the exception and yield a friendly error message
        logger.error(f"Error generating response: {str(e)}")
        yield "Sorry, I'm not able to understand your question. Please try again or rephrase it."


@csrf_exempt
def chat_view(request):
    """
    Handle the chat view for medical queries.
    """
    if request.method == "POST":
        try:
            # Get the user's input
            user_input = request.POST["user_input"]

            # Create a prompt that reflects the AI's medical expertise and experience
            prompt = (
                    "You are a highly experienced doctor with over 32 years of experience, "
                    "specializing in diseases common in Sierra Leone, West Africa, and the world. "
                    "You have worked with various hospitals and clinics in Sierra Leone, "
                    "including the Sierra Leone Teaching Hospital. You are well-versed in "
                    "treating diseases such as malaria, HIV/AIDS, tuberculosis, and other "
                    "common conditions. You are also knowledgeable about traditional "
                    "medicinal practices in Sierra Leone. Please answer the following query "
                    "as an expert:\n\nUser: "
                    + user_input +
                    "\nAI:"
            )

            # Generate a response to the user's query
            response = generate_response(prompt)
            return StreamingHttpResponse(response, content_type='text/plain')
        except Exception as e:
            # Log the exception and return a friendly error message
            logger.error(f"Error handling request: {str(e)}")
            return HttpResponse("Sorry, an error occurred while processing your request. Please try again.", status=500)
    else:
        return render(request, "ai/chat.html")