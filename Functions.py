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


def update_user_progress(userdata, uid, wpm, accuracy, language):
    user_record = userdata.find_one({"_id": uid})
    if user_record is None:
        userdata.insert_one({"_id": uid, "progress": [], "record": {"wpm": 0, "accuracy": 0, "language": ""}})

    user_record = userdata.find_one({"_id": uid})
    user_record["progress"].append(
        {'userId': uid, 'wpm': wpm, 'accuracy': accuracy, 'date': datetime.now().isoformat(), 'language': language})
    userdata.update_one({"_id": uid}, {"$set": {"progress": user_record["progress"]}})