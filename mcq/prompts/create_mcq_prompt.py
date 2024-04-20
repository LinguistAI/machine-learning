


def create_mcq_prompt(word: str):
    prompt = [
        "Input Word: ",
        word + "\n",
              
    """
    Generate a Sentence: Create a sentence relevant to the input word where a single word is left blank.\n
    This sentence should be structured in such a way that it is clear and meaningful, with the blank naturally fitting the input word as the correct answer.\n
    Create three distinctive and incorrect options: Generate three words that are related to the input word in some way (e.g., by topic, word structure, or general association) but do not correctly fill in the blank in the sentence and is not close to the answer.\n
    These options should make the question a bit hard but not so similar that they could be considered correct.\n
    Do not ever give duplicate options or the answer as an incorrect option.\n
    Format the Multiple Choice Question as json:\n
    {
    "question": "Write the sentence with the blank, indicating where the input word should fit."
    "options": [
    "Incorrect Option 1",
    "Incorrect Option 2",
    "Incorrect Option 3"
    ],
    "answer": "Correct Answer (Input Word)"
    }\n
    Example:\n
    Input Word: Photosynthesis\n
    Output:\n
    {
    "question": "Plants convert sunlight into energy through the process of _______.",
    "options": [
    "Respiration",
    "Fermentation",
    "Transpiration"
    ],
    "answer": "Photosynthesis"
    }"""]
    return "".join(prompt)