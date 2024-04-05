import json

from loguru import logger
from telethon.sync import TelegramClient
from telethon.tl.custom.dialog import Dialog
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.patched import Message
from analyser import analys
from sortjson import sortdict
def save_to_json(file_to_save: list[dict[str, str]], file_name: str) -> None:
    with open(file_name, "w+", encoding="utf-8") as f:
        json.dump(file_to_save, f, ensure_ascii=False)


# Укажите свои учетные данные API Telegram
TELEGRAM_APP_ID  = 'ВВЕСТИ'
TELEGRAM_APP_HASH  = 'ВВЕСТИ'
PHONE_NUMBER ='session'
# Создайте клиента Telegram
client = TelegramClient(PHONE_NUMBER, TELEGRAM_APP_ID, TELEGRAM_APP_HASH,device_model = "iPhone 13 Pro Max",
        system_version = "14.8.1",
        app_version = "8.4",
        lang_code = "ru",)
client.start()


def get_dialogs(limit: int | None = 100) -> list[Dialog]:
    """Get all dialogs from the Telegram."""
    dialogs: list[Dialog] = client.get_dialogs(limit=limit)
    dialogs = [
        dialog for dialog in dialogs if dialog.is_user
    ]  # remove groups or channels
    logger.info(f"Found {len(dialogs)} dialogs")
    return dialogs


def parse_messages(dialog: Dialog, limit: int = 1000) -> list[dict]:
    """Get all messages from the dialog."""
    all_messages_list = []
    offset_id = 0

    while True:
        messages: list[Message] = client(
            GetHistoryRequest(
                peer=dialog,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0,
            )
        ).messages
        if not messages:
            break

        all_messages_list.extend(
            {
                "date": message.date.isoformat(),
                "message": message.message,
                "out": message.out,
            }
            for message in messages
            # Filter audio or video content
            if message.message and not message.via_bot
        )
        offset_id = offset_id = messages[-1].id
    return all_messages_list


def main():
    """Parse and save private chat messages."""
    dialogs = get_dialogs(limit=None)
    for dialog in dialogs:
        user = client.get_entity(dialog.id)

        user_name = user.first_name  # Записанное имя пользователя

        all_messages_list = parse_messages(dialog)
        if user_name!=None:

            user_name = user_name.replace('/','')
            user_name = user_name.replace('|', '')
            save_to_json(all_messages_list, f"data/{user_name}.json")
            logger.success(f"Saved {len(all_messages_list)} messages for {dialog.name}")


if __name__ == "__main__":
    main()
    analys()
    sortdict('out.json')
    sortdict('in.json')
