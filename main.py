from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from src.database import DatabaseManager
from src.google_sheets_exporter import GoogleSheetsExporter
import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
GOOGLE_CREDS = os.getenv('GOOGLE_CREDS')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

db_manager = DatabaseManager()
sheets_exporter = GoogleSheetsExporter(GOOGLE_CREDS)

@dp.chat_join_request_handler()
async def on_join_request(join_request: types.ChatJoinRequest):
    user = join_request.from_user
    invite_link = join_request.invite_link.invite_link
    channel = join_request.chat.title
    phone_number = user.phone_number if hasattr(user, 'phone_number') else None

    # Save invite with the current timestamp in the database
    db_manager.save_invite(invite_link, user.id, user.username, user.full_name, phone_number, channel)

    # Get spreadsheet and tab information
    spreadsheet_id = db_manager.get_spreadsheet_id_for_channel(channel)
    if not spreadsheet_id:
        spreadsheet_id = sheets_exporter.create_spreadsheet(channel)
        db_manager.save_channel_link(channel, invite_link, spreadsheet_id)

    tab_name = invite_link.replace("https://", "")
    sheets_exporter.create_tab(spreadsheet_id, tab_name)
    
    # Format current time for Google Sheets
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sheets_exporter.append_data(
        spreadsheet_id, f'{tab_name}!A2', [[user.id, user.username, user.full_name, phone_number, current_time]]
    )

@dp.message_handler(commands=['tree'])
async def send_tree_links(message: types.Message):
    links = db_manager.get_channel_links()
    response = "\n".join([f"{channel}: https://docs.google.com/spreadsheets/d/{spreadsheet_id}" for channel, _, spreadsheet_id in links])
    await message.reply(f"Links to invite statistics:\n{response}")

if __name__ == "__main__":
    spreadsheet_ids = [row[2] for row in db_manager.get_channel_links()]
    sheets_exporter.update_permissions_on_startup(spreadsheet_ids)
    executor.start_polling(dp, skip_updates=True)
