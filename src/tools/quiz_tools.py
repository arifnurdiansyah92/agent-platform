"""Quiz tools for interactive math learning."""

import asyncio
import json
import logging
import uuid
from typing import List

from livekit.agents import RunContext, function_tool

from src.config import RPC_METHOD_QUIZ, RPC_TIMEOUT
from src.models import Quiz, QuizQuestion, UserData

logger = logging.getLogger("agent.tools.quiz")


@function_tool
async def create_quiz(
    context: RunContext[UserData],
    topic: str,
    num_questions: int = 5,
    difficulty: str = "medium"
):
    """Create a math quiz on a specific topic.

    This will generate a quiz and display it to the student via the frontend.

    Args:
        topic: The math topic (e.g., "algebra", "geometry", "fractions")
        num_questions: Number of questions (1-10, default: 5)
        difficulty: Difficulty level ("easy", "medium", "hard")
    """
    userdata = context.userdata

    # Validate inputs
    num_questions = max(1, min(10, num_questions))
    difficulty = difficulty.lower() if difficulty.lower() in ["easy", "medium", "hard"] else "medium"

    # Generate quiz questions (you can integrate with OpenAI API to generate these dynamically)
    questions = _generate_quiz_questions(topic, num_questions, difficulty)

    # Create quiz object
    quiz = Quiz(
        id=str(uuid.uuid4()),
        topic=topic,
        difficulty=difficulty,
        questions=questions,
        current_question_index=0,
        score=0,
        completed=False
    )

    # Store quiz in userdata
    userdata.current_quiz = quiz
    userdata.quiz_history.append({
        "id": quiz.id,
        "topic": topic,
        "difficulty": difficulty,
        "status": "in_progress",
        "created_at": str(uuid.uuid4())  # timestamp
    })

    # Send quiz to frontend
    if not userdata.ctx or not userdata.ctx.room:
        return f"Created a {num_questions}-question quiz on {topic}, but couldn't display it"

    room = userdata.ctx.room
    participants = room.remote_participants
    if not participants:
        return "Quiz created, but no participants found to send it to"

    participant = next(iter(participants.values()), None)
    if not participant:
        return "Quiz created, but couldn't get the first participant"

    try:
        # Send quiz start event
        payload = json.dumps({
            "action": "start_quiz",
            "quiz_id": quiz.id,
            "topic": topic,
            "difficulty": difficulty,
            "total_questions": len(questions),
            "question": {
                "index": 0,
                "question_text": questions[0].question_text,
                "options": questions[0].options,
                "question_id": questions[0].id
            }
        })

        logger.info(f"Sending quiz start: {payload}")

        result = await asyncio.wait_for(
            room.local_participant.perform_rpc(
                destination_identity=participant.identity,
                method=RPC_METHOD_QUIZ,
                payload=payload,
            ),
            timeout=RPC_TIMEOUT,
        )

        response = json.loads(result)
        logger.info(f"[Quiz] Start result: {response}")

        if response.get("ok"):
            return f"I've created a {difficulty} {topic} quiz with {num_questions} questions. Let's start with question 1!"
        else:
            error = response.get("error", "Unknown error")
            return f"Created quiz but couldn't display it: {error}"

    except asyncio.TimeoutError:
        logger.error("Quiz start timed out")
        return "Quiz created but the display timed out. Please try again."
    except Exception as e:
        logger.error(f"Failed to start quiz: {e!s}")
        return f"Created quiz but encountered an error displaying it: {str(e)}"


@function_tool
async def submit_answer(
    context: RunContext[UserData],
    answer: str
):
    """Submit an answer to the current quiz question.

    Args:
        answer: The student's answer (A, B, C, or D for multiple choice)
    """
    userdata = context.userdata

    if not userdata.current_quiz:
        return "There's no active quiz. Create a quiz first using create_quiz."

    quiz = userdata.current_quiz

    if quiz.completed:
        return f"This quiz is already completed. Your score was {quiz.score}/{len(quiz.questions)}."

    # Get current question
    current_question = quiz.questions[quiz.current_question_index]

    # Check answer
    is_correct = answer.upper() == current_question.correct_answer.upper()

    if is_correct:
        quiz.score += 1

    # Store answer
    current_question.user_answer = answer.upper()
    current_question.is_correct = is_correct

    # Move to next question or complete quiz
    quiz.current_question_index += 1

    if quiz.current_question_index >= len(quiz.questions):
        # Quiz completed
        quiz.completed = True
        return await _complete_quiz(context, quiz)
    else:
        # Next question
        return await _show_next_question(context, quiz)


@function_tool
async def get_quiz_status(context: RunContext[UserData]):
    """Get the status of the current quiz.

    Returns information about current progress, score, and which question the student is on.
    """
    userdata = context.userdata

    if not userdata.current_quiz:
        if userdata.quiz_history:
            last_quiz = userdata.quiz_history[-1]
            return f"No active quiz. Last quiz was on {last_quiz['topic']} ({last_quiz['status']})."
        return "No quiz has been created yet. Use create_quiz to start one."

    quiz = userdata.current_quiz

    if quiz.completed:
        return f"Quiz completed! Final score: {quiz.score}/{len(quiz.questions)} ({int(quiz.score/len(quiz.questions)*100)}%)"

    current = quiz.current_question_index + 1
    total = len(quiz.questions)
    return f"Currently on question {current} of {total}. Score so far: {quiz.score}/{quiz.current_question_index} answered correctly."


@function_tool
async def skip_question(context: RunContext[UserData]):
    """Skip the current quiz question and move to the next one.

    The skipped question will be marked as incorrect.
    """
    userdata = context.userdata

    if not userdata.current_quiz:
        return "There's no active quiz."

    quiz = userdata.current_quiz

    if quiz.completed:
        return "Quiz is already completed."

    # Mark current as skipped
    current_question = quiz.questions[quiz.current_question_index]
    current_question.user_answer = "SKIPPED"
    current_question.is_correct = False

    # Move to next
    quiz.current_question_index += 1

    if quiz.current_question_index >= len(quiz.questions):
        quiz.completed = True
        return await _complete_quiz(context, quiz)
    else:
        return await _show_next_question(context, quiz)


@function_tool
async def show_quiz_results(context: RunContext[UserData]):
    """Show detailed results of the completed quiz.

    Shows which questions were answered correctly and incorrectly.
    """
    userdata = context.userdata

    if not userdata.current_quiz:
        return "No quiz to show results for."

    quiz = userdata.current_quiz

    if not quiz.completed:
        return "Quiz is not completed yet. Finish the quiz first."

    # Send detailed results to frontend
    if not userdata.ctx or not userdata.ctx.room:
        return "Quiz completed but couldn't display results"

    room = userdata.ctx.room
    participants = room.remote_participants
    if not participants:
        return "No participants to send results to"

    participant = next(iter(participants.values()), None)
    if not participant:
        return "Couldn't get participant"

    try:
        results = []
        for i, q in enumerate(quiz.questions):
            results.append({
                "question_number": i + 1,
                "question": q.question_text,
                "correct_answer": q.correct_answer,
                "user_answer": q.user_answer or "Not answered",
                "is_correct": q.is_correct
            })

        payload = json.dumps({
            "action": "show_results",
            "quiz_id": quiz.id,
            "score": quiz.score,
            "total": len(quiz.questions),
            "percentage": int(quiz.score / len(quiz.questions) * 100),
            "results": results
        })

        logger.info(f"Sending quiz results")

        result = await asyncio.wait_for(
            room.local_participant.perform_rpc(
                destination_identity=participant.identity,
                method=RPC_METHOD_QUIZ,
                payload=payload,
            ),
            timeout=RPC_TIMEOUT,
        )

        response = json.loads(result)

        if response.get("ok"):
            return f"Here are your detailed results: {quiz.score}/{len(quiz.questions)} correct ({int(quiz.score/len(quiz.questions)*100)}%)"
        else:
            return f"Results: {quiz.score}/{len(quiz.questions)}"

    except Exception as e:
        logger.error(f"Failed to show results: {e!s}")
        return f"Quiz completed with score {quiz.score}/{len(quiz.questions)}"


# Helper functions

def _generate_quiz_questions(topic: str, num_questions: int, difficulty: str) -> List[QuizQuestion]:
    """Generate quiz questions based on topic and difficulty.

    In production, integrate with OpenAI API to dynamically generate questions.
    For now, returns sample questions.
    """
    # Sample question bank (in production, use LLM to generate these dynamically)
    sample_questions = {
        "algebra": [
            QuizQuestion(
                id=str(uuid.uuid4()),
                question_text="What is 2x + 5 = 15? Solve for x.",
                options=["A) x = 5", "B) x = 10", "C) x = 7", "D) x = 3"],
                correct_answer="A",
                explanation="Subtract 5 from both sides: 2x = 10, then divide by 2: x = 5"
            ),
            QuizQuestion(
                id=str(uuid.uuid4()),
                question_text="Simplify: 3(x + 2) - 2x",
                options=["A) x + 6", "B) 5x + 6", "C) x + 2", "D) 3x + 6"],
                correct_answer="A",
                explanation="3(x + 2) - 2x = 3x + 6 - 2x = x + 6"
            ),
        ],
        "geometry": [
            QuizQuestion(
                id=str(uuid.uuid4()),
                question_text="What is the area of a rectangle with length 8 and width 5?",
                options=["A) 13", "B) 40", "C) 26", "D) 32"],
                correct_answer="B",
                explanation="Area = length × width = 8 × 5 = 40"
            ),
        ],
        "fractions": [
            QuizQuestion(
                id=str(uuid.uuid4()),
                question_text="What is 1/2 + 1/4?",
                options=["A) 2/6", "B) 3/4", "C) 1/6", "D) 2/4"],
                correct_answer="B",
                explanation="1/2 + 1/4 = 2/4 + 1/4 = 3/4"
            ),
        ]
    }

    # Get questions for topic (or use default)
    questions = sample_questions.get(topic.lower(), sample_questions["algebra"])

    # Return requested number
    return questions[:num_questions]


async def _show_next_question(context: RunContext[UserData], quiz: Quiz) -> str:
    """Show the next question to the student."""
    userdata = context.userdata

    if not userdata.ctx or not userdata.ctx.room:
        return "Moving to next question, but couldn't display it"

    room = userdata.ctx.room
    participants = room.remote_participants
    if not participants:
        return "No participants"

    participant = next(iter(participants.values()), None)
    if not participant:
        return "Couldn't get participant"

    try:
        next_question = quiz.questions[quiz.current_question_index]

        payload = json.dumps({
            "action": "next_question",
            "quiz_id": quiz.id,
            "question": {
                "index": quiz.current_question_index,
                "question_text": next_question.question_text,
                "options": next_question.options,
                "question_id": next_question.id
            },
            "progress": {
                "current": quiz.current_question_index + 1,
                "total": len(quiz.questions),
                "score": quiz.score
            }
        })

        logger.info(f"Sending next question")

        result = await asyncio.wait_for(
            room.local_participant.perform_rpc(
                destination_identity=participant.identity,
                method=RPC_METHOD_QUIZ,
                payload=payload,
            ),
            timeout=RPC_TIMEOUT,
        )

        response = json.loads(result)

        if response.get("ok"):
            return f"Moving to question {quiz.current_question_index + 1}."
        else:
            return f"Next question ready (Question {quiz.current_question_index + 1})"

    except Exception as e:
        logger.error(f"Failed to show next question: {e!s}")
        return "Moving to next question"


async def _complete_quiz(context: RunContext[UserData], quiz: Quiz) -> str:
    """Complete the quiz and show final score."""
    userdata = context.userdata

    percentage = int(quiz.score / len(quiz.questions) * 100)

    # Update quiz history
    for q in userdata.quiz_history:
        if q["id"] == quiz.id:
            q["status"] = "completed"
            q["score"] = f"{quiz.score}/{len(quiz.questions)}"
            q["percentage"] = percentage

    if not userdata.ctx or not userdata.ctx.room:
        return f"Quiz completed! Final score: {quiz.score}/{len(quiz.questions)} ({percentage}%)"

    room = userdata.ctx.room
    participants = room.remote_participants
    if not participants:
        return f"Quiz completed! Score: {quiz.score}/{len(quiz.questions)}"

    participant = next(iter(participants.values()), None)
    if not participant:
        return f"Quiz completed! Score: {quiz.score}/{len(quiz.questions)}"

    try:
        payload = json.dumps({
            "action": "complete_quiz",
            "quiz_id": quiz.id,
            "score": quiz.score,
            "total": len(quiz.questions),
            "percentage": percentage
        })

        logger.info(f"Completing quiz")

        result = await asyncio.wait_for(
            room.local_participant.perform_rpc(
                destination_identity=participant.identity,
                method=RPC_METHOD_QUIZ,
                payload=payload,
            ),
            timeout=RPC_TIMEOUT,
        )

        response = json.loads(result)

        if response.get("ok"):
            return f"Quiz completed! You scored {quiz.score}/{len(quiz.questions)} ({percentage}%). Great job!"
        else:
            return f"Quiz completed! Score: {quiz.score}/{len(quiz.questions)} ({percentage}%)"

    except Exception as e:
        logger.error(f"Failed to complete quiz: {e!s}")
        return f"Quiz completed! Final score: {quiz.score}/{len(quiz.questions)} ({percentage}%)"
