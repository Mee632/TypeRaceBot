from datetime import datetime
import json

def calculate_wpm(start_time, end_time, num_words):
    elapsed_time = end_time - start_time
    minutes = elapsed_time / 60
    wpm = num_words / minutes
    return round(wpm, 2)


def calculate_correctness(user_input, correct_sentence):
    user_words = user_input.split()
    correct_words = correct_sentence.split()
    correct_count = sum(u == c for u, c in zip(user_words, correct_words))
    return correct_count / len(correct_words) * 100


def underline_errors(user_input, correct_sentence):
    user_words = user_input.split()
    correct_words = correct_sentence.split()
    underlined_sentence = []
    for u, c in zip(user_words, correct_words):
        if u == c:
            underlined_sentence.append(u)
        else:
            underlined_sentence.append(f"__{u}__")
    return ' '.join(underlined_sentence)


def update_user_progress(username, wpm, accuracy):
    with open('UserData/userprogress.json', 'r') as f:
        user_progress = json.load(f)

    user_record = user_progress.get(username, [])
    user_record.append({'date': datetime.now().isoformat(), 'wpm': wpm, 'accuracy': accuracy})
    user_progress[username] = user_record

    with open('UserData/userprogress.json', 'w') as f:
        json.dump(user_progress, f)
