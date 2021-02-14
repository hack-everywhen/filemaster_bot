import copy

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
        self.bot.add_event_handler(self.delete_files, events.NewMessage(pattern='/delete', forwards=False))
        self.bot.add_event_handler(self.help, events.NewMessage(pattern='/help', forwards=False))

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
            file = db.get(event.sender_id, content)
            current_path = content
            content_type = file[1]
        if content_type != 'file':
            # throw error
            return
        await bot.send_message(event.sender_id, file[2], parse_mode='html', file=file[0])

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
        if len(args) == 2:
            offset_id = event.message.id
            limit = int(args[1])
            if 25 < limit < 0:
                await bot.send_message(event.sender_id, messages.add_instructions_invalid_bulk)
                return
            documents = []
            async for message in bot.iter_messages(event.sender_id, filter=InputMessagesFilterDocument,
                                                   offset_id=offset_id, limit=limit):

                # await self.add(event, message.document)
                documents.append(message.file)
                await self.add(documents)
                return
        elif event.message.is_reply is True:
            file_message = await event.message.get_reply_message()
            if file_message.file:
                await self.add(event, [file_message.file])
            else:
                await bot.send_message(event.sender_id, messages.add_instructions_no_proper_reply)
            return
        else:
            await bot.send_message(event.sender_id, messages.add_instructions_normal)

    async def add(self, event, files):
        fm = self.fm
        bot = self.bot
        current_path = '/'
        next_path = '/'
        while next_path != 'add_file':
            # action = current_path
            prev_path = copy.deepcopy(next_path)
            next_path = await fm.directory(event.sender_id, next_path, act='ADD')
            if next_path is None:
                await bot.send_message(event.sender_id, messages.operation_incomplete)
                return
            if next_path == 'make_dir':
                new_dir_path = await fm.make_directory(event.sender_id, prev_path)
                if new_dir_path == 'EXISTS':
                    return
                next_path = new_dir_path
                print("created p: "+next_path)
            # print(next_path)
        progress = await bot.send_message(event.sender_id, 'Adding...')
        for file in files:
            status = await fm.add_file_to_directory(event.sender_id, file, prev_path)
            status_message = '<code>{}</code> {}'.format(file.name, status)
            await progress.edit(text=status_message)
        return

    async def delete_files(self, event):
        fm = self.fm
        db = self.db
        bot = self.bot
        path = '/'
        while isinstance(path, str):
            # action = current_path
            prev_path = copy.deepcopy(path)
            path = await fm.directory(event.sender_id, path, act='DELETE')
            file = db.get(event.sender_id, path)
            if file[1] == 'file':
                db.delete_file(event.sender_id, path)
            if path is None:
                await bot.send_message(event.sender_id, messages.operation_incomplete)
                return
            if path == 'delete_dir':
                caution = 'Are you sure you want to delete <code>{}</code> and everything inside it?'.format(prev_path)
                confirm = await fm.simple_select(event.sender_id, ["Yes", "No"], caution)
                if confirm == 'Yes':
                    db.delete_folder(event.sender_id, prev_path)
                    await bot.send_message(event.sender_id, 'Folder and it\'s contents deleted!')
                    return
                else:
                    path = prev_path