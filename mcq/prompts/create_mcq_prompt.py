


def create_mcq_prompt(word: str):
    prompt = [
        "Input Word: ",
        word + "\n",
              
    """
    Create a sentence where a single word is left blank.\n
    The blank word can be the input word or a B1 CEFR level word that is not very related.\n
    This sentence should be structured in such a way that it is clear and meaningful, with the blank word naturally fitting as the correct answer.\n
    The options should not fit the blank in any way.\n
    Input word must either be in the options or be the answer.\n
    There should be four options, and an answer.\n
    All option should be unique, and answer cannot be in the options.\n
    Format the Multiple Choice Question as json:\n
    Example:\n
    Input Word: Respiration\n
    Output:\n
    {
    "question": "Plants convert sunlight into energy through the process of _______.",
    "options": [
    "Respiration",
    "Fermentation",
    "Transpiration",
    "Expiration"
    ],
    "answer": "Photosynthesis"
    }
    """]
    return "".join(prompt)