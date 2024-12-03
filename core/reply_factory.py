from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(
        message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if current_question_id is None:
        return True, ""

    try:
        question = PYTHON_QUESTION_LIST[current_question_id]
    except IndexError:
        return False, "Invalid question ID."

    if answer.lower() not in map(str.lower, question['options']):
        return False, "Invalid answer. Please choose from the provided options."

    session.setdefault('user_answers', {})[
        current_question_id] = answer
    session.save()
    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id is None:
        next_question_index = 0
    else:
        next_question_index = current_question_id + 1

    if next_question_index >= len(PYTHON_QUESTION_LIST):
        return None, None

    question = PYTHON_QUESTION_LIST[next_question_index]
    question_text = f"{question['question']}\n"
    question_text += "\n".join(f"{i}. {option}" for i,
                               option in enumerate(question['options'], 1))

    return question_text.strip(), next_question_index


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    user_answers = session.get('user_answers', {})
    if not user_answers:
        return "You haven't answered any questions yet."

    correct_count = sum(
        PYTHON_QUESTION_LIST[q_id]['answer'].lower() == user_response.lower()
        for q_id, user_response in user_answers.items()
    )
    total_questions = len(PYTHON_QUESTION_LIST)
    score_percentage = (correct_count / total_questions) * 100

    result_message = (
        f"Quiz completed!\n"
        f"You answered {correct_count} out of {
            total_questions} questions correctly.\n"
        f"Your score: {score_percentage:.2f}%\n\n"
    )

    if score_percentage == 100:
        result_message += "Excellent job! You've mastered Python!"
    elif score_percentage >= 80:
        result_message += "Great work! You have a strong understanding of Python."
    elif score_percentage >= 60:
        result_message += "Good effort! Keep practicing to improve your Python skills."
    else:
        result_message += "You might want to review Python concepts and try again."

    return result_message
