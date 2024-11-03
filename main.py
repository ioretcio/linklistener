from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from database import DatabaseManager
from google_sheets_exporter import GoogleSheetsExporter
import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

db_manager = DatabaseManager()
sheets_exporter = GoogleSheetsExporter()

@dp.chat_join_request_handler()
async def on_join_request(join_request: types.ChatJoinRequest):
    user = join_request.from_user
    invite_link = join_request.invite_link.invite_link
    channel = join_request.chat.title

    db_manager.save_invite(invite_link, user.id, user.username, user.full_name, channel)

    spreadsheet_id = db_manager.get_spreadsheet_id_for_channel(channel)
    if not spreadsheet_id:
        spreadsheet_id = sheets_exporter.create_spreadsheet(channel)
        db_manager.save_channel_link(channel, invite_link, spreadsheet_id)

    tab_name = invite_link.replace("https://", "")
    sheets_exporter.create_tab(spreadsheet_id, tab_name)
    sheets_exporter.append_data(
        spreadsheet_id, f'{tab_name}!A2', [[user.id, user.username, user.full_name]]
    )

    await bot.approve_chat_join_request(join_request.chat.id, user.id)

@dp.message_handler(commands=['tree'])
async def send_tree_links(message: types.Message):
    links = db_manager.get_channel_links()
    response = "\n".join([f"{channel}: https://docs.google.com/spreadsheets/d/{spreadsheet_id}" for channel, _, spreadsheet_id in links])
    await message.reply(f"Links to invite statistics:\n{response}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
