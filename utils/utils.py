import json


def parse_gemini_json(data: str):
    # Find the index of the first opening brace
    start_index = data.find('{')
    # Find the index of the last closing brace
    end_index = data.rfind('}')
    
    # Extract and return the substring between the first { and the last }
    # Includes the braces themselves in the extracted substring
    if start_index != -1 and end_index != -1 and end_index > start_index:
        json_data = data[start_index:end_index+1]
        return json.loads(json_data)
    else:
        # Return an error message or None if the required characters are not found
        # return empty json
        return json.loads("{}")