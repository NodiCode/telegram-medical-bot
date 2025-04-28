import os
import telebot
from google import genai
from flask import Flask, request, jsonify

# Инициализируем Flask приложение
app = Flask(__name__)

# Инициализируем бота
bot = telebot.TeleBot(os.environ.get("TELEGRAM_BOT_TOKEN"), parse_mode=None)

# Инициализируем Google Gen AI
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# Ваш текущий код бота
# ...

# Добавляем API эндпоинт для медицинской диагностики
@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    data = request.json
    symptoms = data.get('symptoms', [])
    
    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400
    
    # Создаем простой промпт с симптомами
    prompt = "Здравствуйте, я - чат-бот для медицинской диагностики.\n\n"
    prompt += f"Пользователь жалуется на следующие симптомы: {', '.join(symptoms)}\n\n"
    prompt += "Предварительный диагноз: "
    
    try:
        # Генерируем ответ с помощью Gemini
        config = genai.types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2048
        )
        
        response = client.models.generate_content(
            model="gemini-1.5-flash-latest",
            contents=prompt,
            config=config
        )
        
        # Формируем ответ
        diagnosis_response = {
            "diagnosis": response.text,
            "conditions": ["Предварительный диагноз на основе симптомов"],
            "tests": ["Общий анализ крови", "Консультация специалиста"],
            "recommendations": [
                "Обратитесь к врачу для точной диагностики",
                "Не занимайтесь самолечением"
            ],
            "severity": "moderate",
            "followUpRequired": True
        }
        
        return jsonify(diagnosis_response)
    except Exception as e:
        print(f"Error in diagnosis: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Если файл запускается напрямую
if __name__ == '__main__':
    # Получаем порт из переменных окружения (для Render)
    port = int(os.environ.get("PORT", 5000))
    
    # Запускаем бота в отдельном потоке
    import threading
    bot_thread = threading.Thread(target=bot.infinity_polling)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем веб-сервер
    app.run(host="0.0.0.0", port=port)