import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.chatbot import BusinessAnalystChatbot
from config.settings import config

def main():
  """Main application entry point"""
  print("Vietnamese Business Analytics Chatbot")
  print("=" * 50)

  # Initialize chatbot
  try:
    bot = BusinessAnalystChatbot()
    print("Chatbot initialized successfully!")
  except Exception as e:
    print(f"Failed to initialize chatbot: {e}")
    return
  
  # Interact loop
  while True:
    try:
      user_input = input("\n BanjL ").strip()

      if user_input.lower() in ['quit', 'exit', 'bye']:
        print("Tạm biệt!")
        break

      if not user_input:
        continue

      # Process query
      print("Processing...")
      result = bot.process_vietnamese_query(user_input)

      if result['success']:
        print(f"Bot: {result['result']}")
        if config.DEBUG:
          print(f"Function Calls: {result['function_call']}")
        else:
          print(f"Error: {result['error']}")

    except KeyboardInterrupt:
      print("\nTạm biệt!")
      break
    except Exception as e:
      print(f"Unexpected error: {e}")

if __name__ == "__main__":
  main()