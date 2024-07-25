# i-LLAMA Client

This is a Python package to extract issues from user reviews using an API.

## Installation

You can install the package using pip:

```bash
pip install git+https://github.com/vitormesaque/illama_client.git
```


## Usage


### 1. Define the review text

Create a string variable to hold the review text.

```python
review = """It's slow to load and crashes often. The GPS is also inaccurate, showing the driver at the wrong location."""
```

### 2. Import necessary modules

Import the required functions and libraries.

```python
from illama_client.issue_extractor import extract_issues
import json
import pandas as pd
```

### 3. Extract issues from the review

Use the `extract_issues` function to extract issues from the review. Replace `'api'` and `'model'` with your appropriate values.

```python
# Replace 'api' and 'model' with your actual values
issues = extract_issues(review, api, model)
```

### 4. Convert the extracted issues to a DataFrame

Parse the JSON response and normalize it into a pandas DataFrame.

```python
# Convert the JSON response to a pandas DataFrame
json_data = json.loads(issues)
df = pd.json_normalize(json_data, 'issues')
```

### 5. Display the DataFrame

Print the DataFrame to see the extracted issues in a tabular format.

```python
# Display the DataFrame
print(df)
```

### Example Output

The above code will extract the mentioned issues in the review and format them into a pandas DataFrame. Here's an example of the JSON output and the resulting DataFrame:

#### JSON Output

```json
{
  "review": "It's slow to load and crashes often. The GPS is also inaccurate, showing the driver at the wrong location.",
  "issues": [
    {
      "label": "Slow Loading",
      "functionality": "App Speed",
      "severity": 3,
      "likelihood": 5,
      "category": "Performance",
      "sentence": "It's slow to load."
    },
    {
      "label": "Crashes",
      "functionality": "App Stability",
      "severity": 4,
      "likelihood": 5,
      "category": "Bug",
      "sentence": "The app crashes often."
    },
    {
      "label": "GPS Inaccuracy",
      "functionality": "Navigation Accuracy",
      "severity": 3,
      "likelihood": 4,
      "category": "Functionality",
      "sentence": "The GPS is also inaccurate."
    }
  ]
}
```

#### DataFrame Output

```plaintext
           label       functionality  severity  likelihood     category                sentence
0   Slow Loading           App Speed         3           5  Performance         It's slow to load.
1        Crashes        App Stability         4           5          Bug       The app crashes often.
2  GPS Inaccuracy  Navigation Accuracy         3           4  Functionality  The GPS is also inaccurate.
```

