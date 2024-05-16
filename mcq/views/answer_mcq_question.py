from rest_framework.decorators import api_view
from constants.header_constants import HEADER_USER_EMAIL
from mcq.models import MCTQuestion

from mcq.serializers import MCTQuestionSerializer, MCTQuestionHiddenAnswerSerializer
from utils.http_utils import generate_error_response, generate_success_response, validate_request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_description="Submit answer to a multiple choice question",
    operation_id="submit_answer",
    operation_summary="Submit answer to a multiple choice question",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'questionId': openapi.Schema(type=openapi.TYPE_STRING, description="Question ID"),
            'answer': openapi.Schema(type=openapi.TYPE_STRING, description="User's answer (case-insensitive)")
        }
    ),
    responses={
        
        "200": openapi.Response(
            description="Answer submitted successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Answer submitted successfully",
                    "data": {
                        "id": "Question ID",
                        "email": "User's email",
                        "word": "Word",
                        "answer": "Correct answer",
                        "options": [
                            {
                                "label": "Randomized Option 1",
                                "isEliminated": False
                            },
                            {
                                "label": "Randomized Option 2",
                                "isEliminated": False
                            },
                            {
                                "label": "Randomized Option 3",
                                "isEliminated": False
                            },
                            {
                                "label": "Randomized Option 4",
                                "isEliminated": False
                            }
                        ],
                        "createdAt": "2021-08-30 14:00:00",
                        "updatedAt": "2021-08-30 14:00:00",
                        "isUserCorrect": True,
                        "hasUserAnswered": True,
                        "userAnswer": [
                                    "User's first answer",
                                    "User's second answer (if Double Answer item was used)"
                                ],
                        "numTriesLeft": 0
                    }
                }
            }
        ),
        "400": openapi.Response(
            description="Bad request",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 400,
                    "msg": "Authentication is required"
                }
            }
        ),
        "404": openapi.Response(
            description="Not found",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 404,
                    "msg": "Question not found"
                }
            }
        )
    }
)            
@api_view(['POST'])
def answer_mcq_question(request):
    try:
        # Check the request header for email
        validation_error = validate_request(request, required_data=["questionId", "answer"])
        if validation_error:
            return validation_error

        email = request.headers.get(HEADER_USER_EMAIL)
        question_id = request.data.get("questionId")
        user_answer = request.data.get("answer")

        # Check if the question exists
        question = MCTQuestion.objects.filter(id=question_id).first()
        if not question:
            return generate_error_response(404, "Question not found")

        # Check if user has already answered this question
        if question.hasUserAnswered:
            return generate_error_response(400, "This question was already answered.")

        # Check if the user's answer is not an eliminated option
        if user_answer in question.get_eliminated_options():
            return generate_error_response(400, "Given answer is an eliminated option.")

        # Append user's answer to the answer array in the question
        if question.userAnswer is None:
            question.userAnswer = []
        question.userAnswer.append(user_answer)

        isUserCorrect = (str(user_answer).lower() == question.answer.lower())

        # Check if number of tries left is more than 1 and answer is incorrect
        if question.numTriesLeft > 1 and not isUserCorrect:
            question.hasUserAnswered = False
            question.numTriesLeft -= 1

            # Iterate over option fields and update isEliminated if necessary
            option_fields = ['option1', 'option2', 'option3', 'option4']
            for field_name in option_fields:
                options = getattr(question, field_name)
                for option in options:
                    if option['value'] == user_answer:
                        option['isEliminated'] = True
                        break

            question_serializer = MCTQuestionHiddenAnswerSerializer(question)
        else:
            question.hasUserAnswered = True
            question.isUserCorrect = isUserCorrect
            question.numTriesLeft = 0
            question_serializer = MCTQuestionSerializer(question)

        question.save()

        return generate_success_response("Answer submitted successfully", question_serializer.data)

    except Exception as e:
        return generate_error_response(500, f"An error occurred: {str(e)}")