
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
