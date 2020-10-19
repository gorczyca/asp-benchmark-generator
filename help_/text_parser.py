import re
import os
from typing import Tuple, List, Dict

HELP_INPUT_FILE_PATH = '../misc/help_text'

STRING_IN_TAGS_RE = r'<[a-zA-Z]\w*>(.*?)</[a-zA-Z]\w*>'
TAG_RE = r'</?[a-zA-Z]\w*>'


def parse_text(text: str) -> Tuple[str, Dict[str, List[Tuple[int, int]]]]:
    """Simple parser for text containing tags.
    Nested tags are not allowed nor is breaking line within a tag.

    :param text: Text to parse.
    :return: Tuple of the form (extracted text, dict) where:
        extracted text is the text without tags in it.
        dict is a dictionary of type tag: list of tuples (start, len_) where
            start is the index of the character where tag starts
            len_ is the length of the tagged string (counted from start)
    """
    extracted_text = '' # Text without any tags
    tags_dict = {}  # Dictionary of tags and their (start, length) positions.
    text_to_extract = text  # Text still to extract.

    for match in re.finditer(f'{STRING_IN_TAGS_RE}', text):
        tagged_string = match.group()
        string = match.groups()[0]
        # Append the text before this tag to extracted_text
        start_index = text_to_extract.index(tagged_string)
        extracted_text += text_to_extract[:start_index]
        # Extract tag type
        [opening_tag, _] = re.findall(TAG_RE, tagged_string)
        tag_type = opening_tag[1:-1]
        if tag_type not in tags_dict:
            tags_dict[tag_type] = []
        tags_dict[tag_type].append((len(extracted_text), len(string)))
        # Add string without tags to extracted_text
        extracted_text += string
        # Remove from text_to_extract the extracted part
        text_to_extract = text_to_extract[start_index + len(tagged_string):]

    # Append the rest.
    extracted_text += text_to_extract

    return extracted_text, tags_dict


def get_tutorial_data() -> Tuple[str, Dict[str, List[Tuple[int, int]]]]:
    """Extracts the tutorial data from the "help_text" file.

    :return: Tuple of the form (extracted text, dict) where:
        extracted text is the text without tags in it.
        dict is a dictionary of type tag: list of tuples (start, end) where
            start is the index of the character where tag starts
            end is the index of the character where tag ends
    """
    if os.path.exists(HELP_INPUT_FILE_PATH):
        with open(HELP_INPUT_FILE_PATH, 'r') as file:
            help_text = file.read()
            return parse_text(help_text)


def check_correct():
    extracted_text, tags_dict = get_tutorial_data()
    for key, list_ in tags_dict.items():
        print(f'key {key}:')
        for (start, len_) in list_:
            print(extracted_text[start:start+len_])
        print('')


if __name__ == '__main__':
    check_correct()