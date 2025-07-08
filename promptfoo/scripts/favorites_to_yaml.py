import json
import yaml
import os

FAVORITES_JSON = os.path.join(os.path.dirname(__file__), '../../data/favorites.json')
FAVORITES_YAML = os.path.join(os.path.dirname(__file__), '../prompts/favorites.yaml')

def main():
    with open(FAVORITES_JSON, 'r', encoding='utf-8') as f:
        favorites = json.load(f)

    test_cases = []
    for fav in favorites:
        question = fav.get('question', '').strip()
        result_summary = fav.get('result_summary', '').strip()
        if question and result_summary:
            test_cases.append({
                'vars': {'question': question},
                'assert': [
                    {'type': 'contains', 'value': result_summary}
                ]
            })

    with open(FAVORITES_YAML, 'w', encoding='utf-8') as f:
        yaml.dump(test_cases, f, allow_unicode=True, sort_keys=False)
    print(f"Wrote {len(test_cases)} test cases to {FAVORITES_YAML}")

if __name__ == '__main__':
    main() 