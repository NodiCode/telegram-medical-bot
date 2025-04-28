import os
import telebot
from google import genai
from google.genai import types

# Initialize Telegram bot
bot = telebot.TeleBot("6996025306:AAFrVMSC-o6rA-CWof4u3roA3pDr6t1H4p4", parse_mode=None)

# Configure Gemini API with the new SDK
# You can set the API key as an environment variable: export GOOGLE_API_KEY="YOUR_API_KEY"
# Or configure it directly:
client = genai.Client(api_key="AIzaSyAHhpJldughwEcIY5w0evRgRIz-unZ7-wE")

# System instruction in Russian for medical diagnosis
system_instruction = """
Здравствуйте, Я - чат-бот для медицинской диагностики. 
Расскажите мне о ваших симптомах, и я постараюсь предложить предварительный диагноз.
"""

# Dictionary to store conversations for each user
user_conversations = {}

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id
    
    # Initialize conversation for new users
    if user_id not in user_conversations:
        user_conversations[user_id] = []
        
        # Send a welcome message to new users
        bot.send_message(message.chat.id, 
                         "Здравствуйте! Я - чат-бот для медицинской диагностики. Расскажите мне о ваших симптомах.")
    
    try:
        user_text = message.text
        
        # Create a simple prompt that includes conversation history
        prompt = system_instruction + "\n\nИстория диалога:\n"
        
        # Add conversation history
        for past_msg in user_conversations[user_id]:
            if past_msg['role'] == 'user':
                prompt += f"Пользователь: {past_msg['text']}\n"
            else:
                prompt += f"Ассистент: {past_msg['text']}\n"
        
        # Add current message
        prompt += f"Пользователь: {user_text}\n"
        prompt += "Ассистент: "
        
        # Create proper configuration object
        config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2048
        )
        
        # Generate response using proper config object
        response = client.models.generate_content(
            model="gemini-1.5-flash-latest",
            contents=prompt,
            config=config
        )
        
        # Extract text from response
        if hasattr(response, 'text'):
            response_text = response.text
        else:
            response_text = "Извините, я не смог обработать ваш запрос."
        
        # Update conversation history
        user_conversations[user_id].append({'role': 'user', 'text': user_text})
        user_conversations[user_id].append({'role': 'assistant', 'text': response_text})
        
        # Limit history length to prevent tokens from growing too large
        if len(user_conversations[user_id]) > 10:
            user_conversations[user_id] = user_conversations[user_id][-10:]
        
        # Reply to the user
        bot.reply_to(message, response_text)
        
    except Exception as e:
        error_msg = str(e)
        # Truncate error message to prevent "message too long" errors
        if len(error_msg) > 100:
            error_msg = error_msg[:97] + "..."
        bot.reply_to(message, f"Произошла ошибка: {error_msg}")
        print(f"Error details: {str(e)}")
        import traceback
        print(traceback.format_exc())

# Start the bot
print("Bot is running...")
bot.infinity_polling()