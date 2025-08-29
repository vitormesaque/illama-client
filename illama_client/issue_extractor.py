import requests
import json

class IssueExtractor:
    def __init__(self, api_url, model):
        self.api_url = api_url
        self.model = model

    def extract_issues(self, review):
        illama_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

        instruction = ("Extract issues from the user review in strict JSON format. At the top level, provide: severity (1–5), likelihood (1–5), risk_level (low|medium|high), and category (one of: Bug, User Experience, Performance, Security, Compatibility, Functionality, UI, Connectivity, Localization, Accessibility, Data Handling, Privacy, Notifications, Account Management, Payment, Content Quality, Support, Updates, Syncing, Customization). Also include an array [issues], where each issue has: title, category, severity (1–5), likelihood (1–5), and risk_level (low|medium|high).")

        text = illama_prompt.format(instruction, review, "")

        data = {
            "model": self.model,
            "prompt": text,
            "stream": False,
            "format": "json"
        }

        try:
            response = requests.post(self.api_url, json=data)
            response.raise_for_status()
            json_response = response.json()

            cleaned_response = json_response.get('response', '').replace('\n', '').replace('\t', '').replace('\\', '')
            return cleaned_response
        
        except requests.exceptions.RequestException as e:
            return f"Error during API request: {e}"
        
        except ValueError:
            return "Error decoding the response as JSON."
        
        except Exception as e:
            return f"An error occurred: {e}"

def extract_issues(review, api_url, model):
    extractor = IssueExtractor(api_url, model)
    return extractor.extract_issues(review)

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract issues from a user review.")
    parser.add_argument("review", type=str, help="The user review text.")
    parser.add_argument("api_url", type=str, help="The API URL.")
    parser.add_argument("model", type=str, help="The model name.")

    args = parser.parse_args()

    issues = extract_issues(args.review, args.api_url, args.model)
    print(issues)

if __name__ == "__main__":
    main()
