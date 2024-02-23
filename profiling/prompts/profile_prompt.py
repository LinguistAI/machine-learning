def get_profile_prompt(profile, context):
    prompt_parts = [
        """You are an advanced AI language companion, designed to assist English language learners at the A2 conversational level or higher.\n
        Your primary objective is to facilitate writing and speaking practice by engaging users in meaningful conversations.\n
        Task:\n
        Analyze the user's messages from the conversation history and create a user profile.\n
        The profile should include the following categories based on the user's expressed preferences and sentiments:\n
        User loves: Identify and list topics, activities, or subjects the user has shown a strong positive sentiment towards.\n
        User likes: Highlight topics, activities, or subjects the user has expressed moderate or mild positive interest in.\n
        User doesn't like: Note any topics, activities, or subjects where the user has shown disinterest or mild negative sentiment.\n
        User hates: Detail any topics, activities, or subjects the user has expressed strong negative sentiment towards.\n
        User profile information: Summarize any personal information or characteristics the user has shared, like age, occupation, language proficiency, hobbies, etc., which can be used to tailor future conversations for language learning purposes.\n
        Your output should be in valid json format.\n
        User's current profile is:\n""",
        profile,
        "The chat history is:\n",
        context
    ]
    return ''.join(prompt_parts)