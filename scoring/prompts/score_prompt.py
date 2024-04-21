def get_score_prompt(sentence: str, words: list[str]):
    score_template = ["""
        You will be given an English sentence and you will need to score given words in the sentence.\n 
        Only score the words based on the following properties.\n
        You should score each property from 1 to 5, where 1 is the lowest and 5 is the highest.\n
        You should return a JSON object.\n
        Only lower score from word choice if the word is not appropriate for the sentence.\n
        1- Gramatical correctness\n
        2- Spelling\n
        3- Punctuation\n
        4- Capitalization\n
        5- Word choice\n
        6- Sentence structure\n
        7- If rest of the sentence is gramatically correct.\n
        Example 1:\n
        [
            {
            "word": "hello",
            "properties": {
                "gramatical_correctness": 5,
                "spelling": 5,
                "punctuation": 5,
                "capitalization": 5,
                "word_choice": 5,
                "sentence_structure": 5,
                "rest_of_sentence": 5
            },
            "reasoning": "The word is a common greeting and is used correctly in the sentence."
            },
            {
            "word": "world",
            "properties": {
                "gramatical_correctness": 5,
                "spelling": 5,
                "punctuation": 5,
                "capitalization": 5,
                "word_choice": 5,
                "sentence_structure": 5,
                "rest_of_sentence": 5
            },
            "reasoning": "The word is a common noun and is used correctly in the sentence."
            }
        ]\n""",
        f"The sentence is:\n{sentence}\n",
        f"The words are:\n{','.join(words)}\n"]
    return "'".join(score_template)