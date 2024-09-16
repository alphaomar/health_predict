import logging
import ollama
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_response(prompt):
    """
    Generate a response from the selected Ollama model.
    """
    try:
        model_name = 'tinyllama'  # Change this to 'hi' or 'mensratal' as needed
        stream = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}],
            stream=True,
        )

        # Yield each chunk of the response
        response = ''
        for chunk in stream:
            content = chunk.get('message', {}).get('content', '')
            if content:  # Only yield non-empty content
                response += content  # Use Server-Sent Events format

        return response

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return "Sorry, I'm not able to understand your question. Please try again or rephrase it."

@csrf_exempt
def chat_view(request):
    """
    Handle the chat view for medical queries.
    """
    if request.method == "POST":
        logger.info("POST request received with user input.")
        try:
            user_input = request.POST.get("user_input", "")
            logger.info(f"User input: {user_input}")

            prompt = (
                "You are Dr. Buju, a seasoned medical professional with over 32 years of experience. "
                "Your expertise includes diagnosing and treating diseases in Sierra Leone and West Africa, "
                "with a focus on infectious diseases, chronic illnesses, and public health concerns. "
                "Provide clear, culturally sensitive, and evidence-based medical guidance tailored to this region. "
                "Respond with empathy and consider socio-economic factors that may affect patient outcomes. "
                "Answer comprehensively and in an easy-to-understand manner. "
                "Here is a user's medical query:\n\nUser: " + user_input + "\nAI:"
            )

            response = generate_response(prompt)
            return StreamingHttpResponse(response, content_type='text/plain')  # Use plain text for simplicity
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            return HttpResponse("Sorry, an error occurred while processing your request. Please try again.", status=500)
    else:
        logger.info("GET request received.")
        return render(request, "ai/chat.html")
