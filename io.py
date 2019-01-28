import json


def export_as_json(path, content):
    """
    Export data as JSON format.

    Args:
            path: the location of output file.
            content: a dict type variable

    Returns:
            The result of saving.
    """
    with open(path, 'w+', encoding='utf8') as outfile:
        file_accessed = True
        json.dump(content, outfile, ensure_ascii=False, indent=4)

    if file_accessed:
        return True
    else:
        print("Error: [Export as JSON] Cannot access the file.")
        return False
