from telethon import events
from telethon.tl.types import InputMessagesFilterDocument

import messages
from file_manager import FileManager, Helper


class Handler:
    def __init__(self, bot, database):
        self.bot = bot
        self.db = database
        self.fm = FileManager(bot, database)
        self.bot.add_event_handler(self.files, events.NewMessage(pattern='^[^(/add)$]', forwards=False))
        self.bot.add_event_handler(self.add_files, events.NewMessage(pattern='/add', forwards=False))

    async def files(self, event):
        bot = self.bot
        db = self.db
        fm = self.fm
        # inline_buttons = self.inline_buttons
        user = db.check_user(str(event.sender_id))
        if user is False:
            await bot.send_message(event.sender_id, messages.first_time_user)
            db.create_table(event.sender_id)
        # resource = ['stupid', 'stupid']
        current_path, content_type = '/', 'folder'
        while content_type != 'file':
            content = await fm.directory(event.sender_id, current_path)
            if content is None:
                return
            current_path = content[4]
            content_type = content[1]
        if type != 'file':
            # throw error
            return
        await bot.send_message(event.sender_id, content[2], parse_mode='html', file=content[0])

    async def add_files(self, event):
        bot = self.bot
        db = self.db
        fm = self.fm
        user = db.check_user(str(event.sender_id))
        if user is False:
            await bot.send_message(event.sender_id, messages.first_time_user)
            db.create_table(event.sender_id)
        args = event.message.text.split(" ")
        if len(args) != 2 and event.message.is_reply is False:
            await bot.send_message(event.sender_id, messages.add_instructions_normal)
            return
        if args:
            offset_id = event.message.id
            limit = int(args)
            if 25 < limit < 0:
                await bot.send_message(event.sender_id, messages.add_instructions_invalid_bulk)
                return
            documents = []
            async for message in bot.iter_messages(event.sender_id, filter=InputMessagesFilterDocument, offset_id=offset_id,
                                                   limit=limit):

                # await self.add(event, message.document)
                documents.append(message.document)
                await self.add(documents)
                return
        elif event.message.is_reply is True:
            file_message = event.message.get_reply_message()
            if file_message.document:
                await self.add(event, [file_message.document])
                print("do something cool")
            else:
                await bot.send_message(event.sender_id, messages.add_instructions_no_proper_reply)
            return
        else:
            await bot.send_message(event.sender_id, messages.add_instructions_normal)

    async def add(self, event, documents):
        fm = self.fm
        bot = self.bot
        current_path, action = '/', 'folder'
        while action != 'add_file':
            action = await fm.directory(event.sender_id, current_path)
            current_path = action[4]
            if action == 'make_dir':
                new_dir_path = await fm.make_directory(event.sender_id, current_path)
                current_path = new_dir_path
            if action is None:
                await bot.send_message(event.sender_id, messages.operation_incomplete)
                return
        progress = bot.send_message(event.sender_id, 'Adding...')
        async for document in documents:
            status = await fm.add_file_to_directory(event.sender_id, document, current_path)
            status_message = '<code>{}</code> {}'.format(document.file_name, status)
            progress.edit(text=status_message)
        return
