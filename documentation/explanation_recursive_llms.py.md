# **`recursive_llms.py`**

## **Overview**
This script defines a Recursive Language Model (RLM) that processes long contexts by breaking them into manageable chunks and recursively querying sub-models. It uses OpenAI's GPT models to answer user queries efficiently, even when the context exceeds the model's token limit.

---

## **Modules and Dependencies**
- **`openai`**: Interacts with OpenAI's GPT models.
- **`os`**: Accesses environment variables for API keys.
- **`re`**: Performs regular expression operations for extracting specific patterns from responses.
- **`io`**: Captures and redirects standard output during REPL code execution.
- **`contextlib`**: Provides utilities for managing contexts, such as redirecting output.
- **`sys`**: Handles system-level operations.

---

## **Environment Setup**
- The OpenAI API key must be set as an environment variable (`OPENAI_API_KEY`).
- If the API key is not found, the script raises a `ValueError`.

---

## **Functions**

### **`extract_code(response)`**
Extracts Python REPL code blocks from the LLM response.

- **Parameters**:
  - `response` (str): The response from the LLM.
- **Returns**:
  - Extracted code (str) if found, otherwise `None`.
- **Example**:
  ```python
  response = "```repl\nprint('Hello')\n```"
  extract_code(response)  # Returns "print('Hello')"
  ```

---

### **`extract_final(response)`**
Extracts the final answer from the LLM response, specifically from `FINAL()` or `FINAL_VAR()` blocks.

- **Parameters**:
  - `response` (str): The response from the LLM.
- **Returns**:
  - The extracted final answer (str) or a default message if no answer is found.
- **Example**:
  ```python
  response = "FINAL(The answer is 42)"
  extract_final(response)  # Returns "The answer is 42"
  ```

---

### **`rlm(query, context, model="gpt-4", sub_model="gpt-3.5-turbo", max_depth=5, depth=0)`**
Implements the Recursive Language Model.

- **Parameters**:
  - `query` (str): The user's query.
  - `context` (str): The long context string.
  - `model` (str): The root LLM model (default: `"gpt-4"`).
  - `sub_model` (str): The sub-LLM model for recursion (default: `"gpt-3.5-turbo"`).
  - `max_depth` (int): Maximum recursion depth to prevent stack overflow (default: `5`).
  - `depth` (int): Current recursion depth (default: `0`).
- **Returns**:
  - The final answer (str) or an error message if the recursion depth or iterations are exceeded.
- **Process**:
  1. Initializes a REPL environment with the context and helper functions.
  2. Defines a `llm_query` function for recursive sub-calls.
  3. Constructs a system prompt to guide the LLM.
  4. Iteratively queries the LLM, executes REPL code, and checks for final answers.
  5. Returns the extracted final answer or an error message.
- **Example**:
  ```python
  context = "The secret number is 42."
  query = "What is the secret number?"
  rlm(query, context)  # Returns "42"
  ```

---

## **Key Components**

### **REPL Environment**
The REPL environment simulates a Python runtime for the LLM to execute code. It includes:
- `context`: The full context string.
- `llm_query`: A function for recursive sub-queries.
- `print`: Standard Python `print` function for debugging.

---

### **System Prompt**
The system prompt instructs the LLM to:
1. Use REPL code to process the context.
2. Minimize recursive calls to sub-models.
3. Aggregate results and return the final answer using `FINAL()` or `FINAL_VAR()`.

---

### **Error Handling**
- If the recursion depth exceeds `max_depth`, the function returns `"Max recursion depth reached."`
- If the maximum iterations are reached without a final answer, the function returns `"Max iterations reached without final answer."`

---

## **Example Usage**
The script includes an example that simulates a "needle-in-a-haystack" test:
1. Creates a long context with a hidden "needle" string.
2. Queries the RLM to find the hidden string.
3. Prints the final answer.

```python
if __name__ == "__main__":
    haystack = " " * 100000
    needle = "The secret number is 42."
    context = haystack[:50000] + needle + haystack[50000:]
    query = "What is the secret number hidden in the context?"
    print("Running RLM...")
    answer = rlm(query, context)
    print(f"Final Answer: {answer}")
```

---

## **Notes**
- The script is designed for large-scale text processing tasks.
- It demonstrates efficient use of GPT models for recursive querying and context decomposition.
- The REPL environment allows dynamic code execution, making it highly flexible for complex queries.