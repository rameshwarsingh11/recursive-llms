import openai
import os
import re
import io
import contextlib
import sys

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

def extract_code(response):
    """Extract REPL code from the LLM response (triple-backtick block with 'repl')."""
    match = re.search(r'```repl\n(.*?)\n```', response, re.DOTALL)
    return match.group(1) if match else None

def extract_final(response):
    """Extract the final answer from FINAL() or FINAL_VAR()."""
    match = re.search(r'FINAL\((.*?)\)', response, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r'FINAL_VAR\((.*?)\)', response, re.DOTALL)
    if match:
        var_name = match.group(1).strip()
        return repl_globals.get(var_name, "No variable found")
    return "No final answer found"

def rlm(query, context, model="gpt-4", sub_model="gpt-3.5-turbo", max_depth=5, depth=0):
    """
    Recursive Language Model implementation.
    
    Args:
        query (str): The user's query.
        context (str): The long context string.
        model (str): Root LLM model.
        sub_model (str): Sub-LLM model for recursion.
        max_depth (int): Max recursion depth to prevent stack overflow.
        depth (int): Current depth (internal).
    
    Returns:
        str: The final answer.
    """
    if depth > max_depth:
        return "Max recursion depth reached."
    
    # Simulate REPL environment
    repl_globals = {
        'context': context,
        'print': print,  # Allow printing for inspection
    }
    
    # Define llm_query for recursive sub-calls
    def llm_query(sub_prompt, sub_context=None):
        return rlm(sub_prompt, sub_context or context, model=sub_model, sub_model=sub_model, depth=depth+1)
    
    repl_globals['llm_query'] = llm_query
    
    # Metadata for prompt
    context_len = len(context)
    metadata = f"Context length: {context_len} characters. You can slice or search it programmatically."
    
    # System prompt (adapted from the paper)
    system_prompt = """
You are a Recursive Language Model tasked with answering a query using a long context stored in a REPL environment.
The full context is available as the variable 'context' (a string). Do NOT assume you can see the entire context at once—it's too long.
Instead, use Python code in ```repl blocks to inspect, slice, search (e.g., via regex), or process it.

Available tools:
- context: The full string variable.
- llm_query(prompt, sub_context): Call a sub-RLM with a custom prompt and optional sub_context string. Use sparingly as it's costly.
- Standard Python: str methods, re, lists, etc.
- print(): To inspect outputs.

Process:
1. Write REPL code to decompose the context (e.g., chunk = context[0:10000]; print(chunk)).
2. Use llm_query on chunks if needed for deeper analysis.
3. Aggregate results in variables (e.g., answers = []).
4. Once ready, output the final answer wrapped in FINAL(your_answer) or FINAL_VAR(variable_name) if stored in a var.

Be efficient: Batch chunks, minimize llm_query calls, use filtering.
"""
    
    # Initial user prompt
    user_prompt = f"{metadata}\nQuery: {query}"
    
    # History to accumulate interactions
    history = [{"role": "system", "content": system_prompt}]
    history.append({"role": "user", "content": user_prompt})
    
    max_iterations = 10  # Prevent infinite loops
    for _ in range(max_iterations):
        # Call LLM
        response = openai.ChatCompletion.create(
            model=model if depth == 0 else sub_model,
            messages=history
        ).choices[0].message.content
        
        history.append({"role": "assistant", "content": response})
        
        # Check for REPL code
        code = extract_code(response)
        if code:
            # Execute code in REPL namespace, capture output
            with contextlib.redirect_stdout(io.StringIO()) as f:
                try:
                    exec(code, repl_globals, repl_globals)
                except Exception as e:
                    output = f"REPL Error: {str(e)}"
                else:
                    output = f.getvalue()
            # Append output to history
            history.append({"role": "user", "content": f"REPL executed. Output:\n{output}"})
        
        # Check for final answer
        if 'FINAL' in response.upper():
            return extract_final(response)
    
    return "Max iterations reached without final answer."

# Example Usage: Needle-in-a-Haystack Test
if __name__ == "__main__":
    # Create a long context (simulate 10K+ tokens; in reality, make it millions)
    haystack = " " * 100000  # Filler
    needle = "The secret number is 42."
    context = haystack[:50000] + needle + haystack[50000:]
    
    query = "What is the secret number hidden in the context?"
    
    print("Running RLM...")
    answer = rlm(query, context)
    print(f"Final Answer: {answer}")