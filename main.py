from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from src.database import DatabaseManager
from src.google_sheets_exporter import GoogleSheetsExporter
import os
from dotenv import load_dotenv
import sys

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
GOOGLE_CREDS = os.getenv('GOOGLE_CREDS')
SPREADSHEET_ID=os.getenv('SPREADSHEET_ID')


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

db_manager = DatabaseManager()
sheets_exporter = GoogleSheetsExporter(GOOGLE_CREDS)


if len(sys.argv) > 1:
    if sys.argv[1] == "create":
        spreadsheet_id = sheets_exporter.create_spreadsheet("база заявок")
        sheets_exporter.create_tab(spreadsheet_id, "юзеры")
        print(spreadsheet_id)

@dp.chat_join_request_handler()
async def on_join_request(join_request: types.ChatJoinRequest):
    user = join_request.from_user
    invite_link = join_request.invite_link.invite_link
    link_createt =  join_request.invite_link.creator.id
    channel = join_request.chat.title
    db_manager.save_invite(invite_link, user.id, user.username, user.full_name, channel, link_createt)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sheets_exporter.append_data(
        SPREADSHEET_ID, f'юзеры!A2', [[user.id, user.username, user.full_name, current_time, invite_link, channel]]
    )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
