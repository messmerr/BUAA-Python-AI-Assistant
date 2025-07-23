"""
Simple test for Gemini API - English only to avoid encoding issues
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_services import ask_gemini, gemini_service

def test_basic_functionality():
    """Test basic API functionality"""
    print("=== Testing Basic Gemini API ===")
    
    try:
        # Test 1: Basic text generation
        print("Test 1: Basic text generation")
        response = ask_gemini("What is Python programming language? Answer in English briefly.")
        print(f"Response: {response[:200]}...")
        print("[PASS] Basic text generation: PASSED\n")

        # Test 2: System prompt
        print("Test 2: System prompt")
        system_prompt = "You are a helpful programming tutor. Answer concisely."
        response = ask_gemini(
            "What is a list comprehension?",
            system_prompt=system_prompt
        )
        print(f"Response: {response[:200]}...")
        print("[PASS] System prompt: PASSED\n")

        # Test 3: Temperature parameter
        print("Test 3: Temperature parameter")
        response = ask_gemini(
            "Write a short poem about coding",
            temperature=0.9
        )
        print(f"Response: {response[:200]}...")
        print("[PASS] Temperature parameter: PASSED\n")

        # Test 4: Stream generation (just test first few chunks)
        print("Test 4: Stream generation")
        print("Streaming response: ", end="")
        chunk_count = 0
        for chunk in ask_gemini("Explain what is a function in programming", stream=True):
            print(chunk, end="", flush=True)
            chunk_count += 1
            if chunk_count > 10:  # Limit output for testing
                print("... (truncated)")
                break
        print("\n[PASS] Stream generation: PASSED\n")

        print("SUCCESS: All tests passed! Gemini API is working correctly.")
        return True
        
    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        return False

if __name__ == "__main__":
    if not gemini_service:
        print("[FAIL] Gemini service not initialized. Check API key configuration.")
    else:
        test_basic_functionality()
