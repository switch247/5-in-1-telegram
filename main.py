import csv, logging, requests,json,time
from aiogram import Bot, Dispatcher, types,executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext


# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token="5408721786:AAFDGzpBUgCZ3Wx6Ev61nS37N98OdwT-Yg4")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class SomeState(StatesGroup):
    waiting_for_question = State()
    waiting_for_translate = State()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [ "Quote of the Day" , "What is The Weather", "Joke", "News","Translate"]
    keyboard.add(*buttons)
    await message.answer("Welcome! Please select an option:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Quote of the Day")
async def ask_question(message: types.Message):
    quote = await get_quote()
    resp = f"Quote of the Day:\n {quote['text']}\n --{quote['author']} "
    print(resp)
    await message.answer( resp , reply_markup=None)

@dp.message_handler(lambda message: message.text == "What is The Weather")
async def ask_weather(message: types.Message):
    await message.answer(" Please enter your city:", reply_markup=None)
    await SomeState.waiting_for_question.set()
    

@dp.message_handler(state=SomeState.waiting_for_question)
async def process_question(message: types.Message , state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("End" )
    if message.text =="End":
        # Reset the state
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [ "Quote of the Day" , "What is The Weather", "Joke", "News","Translate"]
        keyboard.add(*buttons)
        await message.answer("Welcome! Please select an option:", reply_markup=keyboard)
    else:
        weather = await get_weather(message.text)
        if weather['cod'] == '404':
            a= weather['message']
            await message.answer(a, reply_markup=None)
            
        # a =res[] +"\nPlease enter your city:"
        # print(a)
        else:
            ph= f"https://openweathermap.org/img/wn/{weather['weather'][0]['icon']}.png"
            x=  f'''
            
            city: {weather['name']}
            Temprature: {weather['main']['temp']}° C
            description: {weather['weather'][0]['description']}
            humidity: {weather['main']['humidity']}%
            wind_speed: {weather['wind']['speed']}km/hr
            '''
            await message.answer(x, reply_markup=keyboard)
            await bot.send_photo(chat_id=message.from_id, photo=ph)

@dp.message_handler(lambda message: message.text == "Joke")
async def ask_joke(message: types.Message):
    joke = await get_joke_png()
    resp = f"{joke['body']['setup']}"
    resp2 = f"\n --{joke['body']['punchline']} "
    # ph = f"{joke['body']['image']}"
    # print(ph)
    # await bot.send_photo(chat_id=message.from_id, photo=ph)
    # print(resp,resp2)
    await message.answer( resp , reply_markup=None)
    time.sleep(5)
    await message.answer( resp2 , reply_markup=None)



@dp.message_handler(lambda message: message.text == "Translate")
async def ask_translation(message: types.Message):
    await message.answer(" Please enter text to translate to spanish:", reply_markup=None)
    await SomeState.waiting_for_translate.set()
    

@dp.message_handler(state=SomeState.waiting_for_translate)
async def process_translation(message: types.Message , state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("#" )
    if message.text =="#":
        # Reset the state
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [ "Quote of the Day" , "What is The Weather", "Joke", "News","Translate"]
        keyboard.add(*buttons)
        await message.answer("Welcome! Please select an option:", reply_markup=keyboard)
        
    else:
        res = await translate(message.text)
        new ="Welcome! Please select an option:"
        await message.reply(res, reply_markup=None)
        await message.answer(new, reply_markup=keyboard)



@dp.message_handler(lambda message: message.text == "News")
async def ask_news(message: types.Message):
    news = await get_news()
    # print(news)
    for index,item in enumerate( news ):
        #    print(item)
           news_text = f"---{item['articlesName']}---\n{item['articlesShortDescription']}"

           keyboard = types.InlineKeyboardMarkup()
           buttonm = types.InlineKeyboardButton(text="More", callback_data=f"display_c:{index}")
           keyboard.add(buttonm)
           await message.reply(news_text, reply_markup=keyboard)
    
@dp.callback_query_handler(lambda c: c.data.startswith('display_c:'))
async def display_c_callback(callback_query: types.CallbackQuery):
    target =  callback_query.data.split(':')[1] 
    # print(target)
    await callback_query.answer()
    # await callback_query.message.reply(f": {item['content']}")
    news =  await get_news()
    # print(news)
    
    for index,items in enumerate( news):
        if target == str(index):
            json_obj = json.loads(items["articlesDescription"])
            # print(json_obj)
            for item in json_obj:
                print(item)
                await callback_query.answer()
                await callback_query.message.reply(f"{item['content']}")




async def get_quote():
    # import requests
    url = "https://quotes-inspirational-quotes-motivational-quotes.p.rapidapi.com/quote"
    querystring = {"token":"ipworld.info"}
    headers = {
        "X-RapidAPI-Key": "5e5534d99cmshc500a57813ea737p1df09ejsndeaaeb550d43",
        "X-RapidAPI-Host": "quotes-inspirational-quotes-motivational-quotes.p.rapidapi.com"
    }
    response =requests.get(url, headers=headers, params=querystring)
    return(response.json())

async def get_weather(city):
    api_key ="8aa46341f09c625169029d3dd37c3220"
    response = requests.get(" https://api.openweathermap.org/data/2.5/weather?q="+city+"&units=metric&appid="+api_key)
    return(response.json())

async def get_joke_png():
    url = "https://dad-jokes.p.rapidapi.com/random/joke/png"
    headers = {
        "X-RapidAPI-Key": "5e5534d99cmshc500a57813ea737p1df09ejsndeaaeb550d43",
        "X-RapidAPI-Host": "dad-jokes.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    return(response.json())


def detect_lang(query):
    url = "https://google-translate1.p.rapidapi.com/language/translate/v2/detect"
    payload = { "q": f"{query}" }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "application/gzip",
        "X-RapidAPI-Key": "5e5534d99cmshc500a57813ea737p1df09ejsndeaaeb550d43",
        "X-RapidAPI-Host": "google-translate1.p.rapidapi.com"
    }
    response = requests.post(url, data=payload, headers=headers)
    # print((response.json())['data']["detections"][0][0]['language'])
    # working
    return(response.json())['data']["detections"][0][0]['language']

async def translate(query):
    url = "https://google-translate1.p.rapidapi.com/language/translate/v2"
    payload =  {
        "q": f"{query}",
        "target": "es",
        "source": f"{detect_lang(query)}"
        # es
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "application/gzip",
        "X-RapidAPI-Key": "5e5534d99cmshc500a57813ea737p1df09ejsndeaaeb550d43",
        "X-RapidAPI-Host": "google-translate1.p.rapidapi.com"
    }
    response = requests.post(url, data=payload, headers=headers)
    # print(response.json())
    # print((response.json())['data']["translations"][0]['translatedText'])
    return(response.json())['data']["translations"][0]['translatedText']


async def get_news():
    url = "https://reuters-business-and-financial-news.p.rapidapi.com/category-id/8/article-date/11-04-2021"
    querystring = {"category-id":"8","ArticleDate":"11-04-2021"}
    headers = {
        "X-RapidAPI-Key": "5e5534d99cmshc500a57813ea737p1df09ejsndeaaeb550d43",
        "X-RapidAPI-Host": "reuters-business-and-financial-news.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    return(response.json())



if __name__ == '__main__':
    # Start the bot
    try:
        
        executor.start_polling(dp)
    except Exception as e:
        logging.exception(e)
