import random

def mathematics(user_data, message_text, idio, idi):
    target_score = user_data['miniapps']['mathematics']['target_score']

    if user_data['miniapps']['mathematics']['current_score'] >= target_score:
        message = f"{idio['Finished'][idi]}! 🎉 🎉 🎉 🎉 🎉"

    else:
        if message_text == user_data['miniapps']['mathematics']['answer']:
            user_data['miniapps']['mathematics']['current_score'] += 1
            current_score = user_data['miniapps']['mathematics']['current_score']
            user_data['coins'] += 1/user_data['miniapps']['mathematics']['ex_rate']
            message = f"{idio['Well done'][idi]}! 😀\n{idio['Progress'][idi]}: {round(current_score/target_score*100, 1)}%\n\n"
        else:
            user_data['miniapps']['mathematics']['current_score'] += user_data['miniapps']['mathematics']['fault_penalty']
            current_score = user_data['miniapps']['mathematics']['current_score']
            user_data['coins'] += user_data['miniapps']['mathematics']['fault_penalty']/user_data['miniapps']['mathematics']['ex_rate']
            correct_ans = user_data['miniapps']['mathematics']['answer']
            message = f"{idio['That is not correct'][idi]} 😥 ➡️ {idio['Correct answer'][idi]}: {correct_ans}\nProgress: {round(current_score/target_score*100, 1)}%\n\n"
        user_data, question = random_question(user_data, idio, idi)
        message = message + question

    return user_data, message

def random_question(user_data, idio, idi):
    functions = {'multiplication': multiplications, 'division': divisions, 'sum': sums, 'rest': rests}
    function_list = user_data['miniapps']['mathematics']['operations']
    selected_function_name = random.choice(function_list)
    selected_function = functions[selected_function_name]
    user_data, question = selected_function(user_data, idio, idi)

    return user_data, question

def multiplications(user_data, idio, idi): # multiplication
    num1 = random.randint(user_data['miniapps']['mathematics']['homework']['multiplication']['lower_num'], user_data['miniapps']['mathematics']['homework']['multiplication']['upper_num'])
    num2 = random.randint(user_data['miniapps']['mathematics']['homework']['multiplication']['lower_num'], user_data['miniapps']['mathematics']['homework']['multiplication']['upper_num'])
    question = f"{idio['What is'][idi]} {num1} ✖️ {num2}?"
    user_data['miniapps']['mathematics']['answer'] = num1 * num2

    return user_data, question

def divisions(user_data, idio, idi): # division (int)
    num1 = random.randint(user_data['miniapps']['mathematics']['homework']['division']['lower_num'], user_data['miniapps']['mathematics']['homework']['division']['upper_num'])
    num2 = random.randint(user_data['miniapps']['mathematics']['homework']['division']['lower_num'], user_data['miniapps']['mathematics']['homework']['division']['upper_num'])
    question = f"{idio['What is'][idi]} {num1*num2} ➗ {num1}?"
    user_data['miniapps']['mathematics']['answer'] = num2

    return user_data, question

def sums(user_data, idio, idi):
    num1 = random.randint(user_data['miniapps']['mathematics']['homework']['sum']['lower_num'], user_data['miniapps']['mathematics']['homework']['sum']['upper_num'])
    num2 = random.randint(user_data['miniapps']['mathematics']['homework']['sum']['lower_num'], user_data['miniapps']['mathematics']['homework']['sum']['upper_num'])
    question = f"{idio['What is'][idi]} {num1} ➕ {num2}?"
    user_data['miniapps']['mathematics']['answer'] = num1 + num2

    return user_data, question

def rests(user_data, idio, idi):
    num1 = random.randint(user_data['miniapps']['mathematics']['homework']['rest']['lower_num'], user_data['miniapps']['mathematics']['homework']['rest']['upper_num'])
    num2 = random.randint(user_data['miniapps']['mathematics']['homework']['rest']['lower_num'], user_data['miniapps']['mathematics']['homework']['rest']['upper_num'])

    if num1 > num2:
        question = f"{idio['What is'][idi]} {num1} ➖ {num2}?"
        user_data['miniapps']['mathematics']['answer'] = num1 - num2
    else:
        question = f"{idio['What is'][idi]} {num2} ➖ {num1}?"
        user_data['miniapps']['mathematics']['answer'] = num2 - num1

    return user_data, question