# Promptfoo Evaluation Setup

This folder contains configuration and test cases for evaluating SQL generation using [promptfoo](https://www.promptfoo.dev/).

## What is promptfoo?

**promptfoo** is an open-source LLM (Large Language Model) testing framework. It allows you to define prompts, test cases, and assertions to systematically evaluate and compare LLM outputs. This helps ensure reliability and consistency as prompts, models, or logic evolve.

## Usage in This Project

In this project, promptfoo is used for **regression testing**. The goal is to ensure that user favorites—queries saved as important or useful by users—continue to produce valid and expected results, even if the underlying prompt or model changes. If you update the prompt template or switch models, you can quickly check that all favorite queries still work as intended.

## Structure

- `config.yaml`: Main configuration file for promptfoo. Specifies provider, prompt, and test cases.
- `prompts/sql_gen.prompt.txt`: Prompt template for instructing the LLM to generate SQL queries.
- `prompts/favorites.yaml`: Test cases generated from `data/favorites.json`. Each test case uses a question and expected result.

## How to Add New Test Cases

1. Add new entries to `data/favorites.json` (with `question` and `result_summary`).
2. Update `prompts/favorites.yaml` to include new test cases (or automate this step with a script).

## How to Update Test Cases from favorites.json

If you add or change entries in `data/favorites.json`, you can automatically regenerate the promptfoo test cases by running:

```sh
python promptfoo/scripts/favorites_to_yaml.py
```

This script will read all favorites and create or update `promptfoo/prompts/favorites.yaml` with the correct format for promptfoo regression testing. Run this script any time you want to sync your favorites with the test suite.

## How to Run promptfoo

1. Install promptfoo:
   ```sh
   npm install -g promptfoo
   ```
2. Set your OpenAI API key:
   ```sh
   export OPENAI_API_KEY=your-key-here
   ```
3. Run the evaluation:
   ```sh
   promptfoo eval -c promptfoo/config.yaml
   ```

See [promptfoo documentation](https://www.promptfoo.dev/docs/) for more options. 