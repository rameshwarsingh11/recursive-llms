# -----------------------------
#   Recursive LLMs Test Cases
# -----------------------------

from recursive_llms import rlm

def run_tests():
    print("\n" + "="*60)
    print("RUNNING RLM DEMO TEST SUITE")
    print("="*60 + "\n")

    test_cases = [
        {
            "name": "Basic Needle-in-a-Haystack (should succeed)",
            "context": " " * 80000 + "SECRET: The password is dragon42." + " " * 120000,
            "query": "What is the secret password mentioned in the text?",
            "expected": lambda x: "dragon42" in x.lower()
        },
        {
            "name": "Multiple needles - should find the last one",
            "context": (
                " " * 50000 + "SECRET: apple" +
                " " * 100000 + "SECRET: banana" +
                " " * 150000 + "SECRET: The real one is cherry99."
            ),
            "query": "What is the real secret mentioned at the end?",
            "expected": lambda x: "cherry99" in x
        },
        {
            "name": "Very short context - no recursion needed",
            "context": "The capital of France is Paris.",
            "query": "What is the capital of France?",
            "expected": lambda x: "paris" in x.lower()
        },
        {
            "name": "No needle present (should not hallucinate)",
            "context": "This is a very boring text with no secrets at all. " * 500,
            "query": "What is the secret number in the document?",
            "expected": lambda x: "no" in x.lower() or "not" in x.lower() or "none" in x.lower()
        },
        {
            "name": "Complex query requiring chunking & aggregation",
            "context": (
                "Report 1: Revenue Q1 = $1.2M\n" +
                " " * 90000 +
                "Report 2: Revenue Q2 = $1.5M\n" +
                " " * 120000 +
                "Report 3: Revenue Q3 = $1.8M\n" +
                " " * 80000 +
                "Report 4: Revenue Q4 = $2.1M"
            ),
            "query": "Calculate the total annual revenue from all quarterly reports and give the final number.",
            "expected": lambda x: "6.6" in x or "6,600,000" in x or "6600000" in x
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}/{len(test_cases)}: {test['name']}")
        print("-" * 50)
        print(f"Query: {test['query']}")
        print(f"Context length: {len(test['context']):,} chars (~{len(test['context'])//4:,} tokens)")

        try:
            answer = rlm(
                query=test["query"],
                context=test["context"],
                model="gpt-4o-mini",         # cheaper & faster for testing
                sub_model="gpt-4o-mini",
                max_depth=4,
                depth=0
            )

            print(f"Answer: {answer}")
            passed = test["expected"](answer)
            status = "PASSED ✓" if passed else "FAILED ✗"
            print(f"Status: {status}\n")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            print("Status: FAILED ✗\n")

    print("="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_tests()
    else:
        # Original demo
        haystack = " " * 100000
        needle = "The secret number is 42."
        context = haystack[:50000] + needle + haystack[50000:]

        query = "What is the secret number hidden in the context?"

        print("Running original demo...")
        answer = rlm(query, context)
        print(f"Final Answer: {answer}")