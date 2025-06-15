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
      user_input = input("\n Bạn: ").strip()

      if user_input.lower() in ['quit', 'exit', 'bye']:
        print("Tạm biệt!")
        break

      if not user_input:
        continue

      # Process query
      result = bot.process_vietnamese_query(user_input)

      if result['success']:
        function_call = result['function_call']
        function_name = function_call['name']
        params = function_call['parameters']

        param_str = ', '.join([f"{k}={v}" for k, v in params.items()])
        display_msg = f"{function_name}({param_str})"

        print(f"Bot: {display_msg}")

        if config.DEBUG:
          print(f"Vietnamese Query: {result['vietnamese_query']}")
          print(f"English Query: {result['english_query']}")
          print(f"Function Call: {json.dumps(result['function_call'], indent=2)}")
      else:
        print(f"Error: {result['error']}")

    except KeyboardInterrupt:
      print("\nTạm biệt!")
      break
    except Exception as e:
      print(f"Unexpected error: {e}")

if __name__ == "__main__":
  main()