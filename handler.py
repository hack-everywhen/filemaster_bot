from telethon import events
import messages
from file_manager import FileManager, Helper


class Handler:
    def __init__(self, bot, database):
        self.bot = bot
        self.db = database
        self.fm = FileManager(bot, database)
        self.bot.add_event_handler(self.files, events.NewMessage(forwards=False))

    async def files(self, event):
        bot = self.bot
        db = self.db
        fm = self.fm
        # inline_buttons = self.inline_buttons
        user = db.check_user(str(event.sender_id))
        if user is False:
            await bot.send_message(event.sender_id, messages.first_time_user)
            db.create_table(event.sender_id)
        resource = ['stupid', 'stupid']
        current_path = '/'
        while resource[1] != 'file':
            resource = await fm.directory(event.sender_id, current_path)
            if resource is None:
                return
        if resource[1] != 'file':
            # throw error
            return
        await bot.send_message(event.sender_id, resource[2], parse_mode='html', file=resource[0])
