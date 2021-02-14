import itertools
import re

from telethon import events, Button
# import config_vars
import messages


class Helper:
    @staticmethod
    async def make_inline_buttons(options: list):
        return [[Button.inline(option, data=option)] for option in options]


class FileManager:
    def __init__(self, bot, database):
        self.bot = bot
        self.db = database
        # self.event = event

    async def simple_select(self, user, options: list, message='Select'):
        bot = self.bot
        async with bot.conversation(user) as conv:
            await conv.send_message(message=message, buttons=options)
            query = await conv.wait_event(events.CallbackQuery(user))
            await query.delete()
            return query.data.decode('utf-8')

    async def directory(self, user_id, directory='/', act='SEND'):
        bot = self.bot
        db = self.db
        contents = db.open_directory(user_id, directory)
        if len(contents) == 0 and directory == '/':
            await bot.send_message(user_id, message="Add some files first using /add. Please see /help if you are new!")
            return
        parent_directory = db.get_parent_directory(user_id, directory)
        message = 'You are here -- > <code>{}</code>'.format(directory)
        keyboard = []
        for r in contents:
            if r[1] == 'file':
                if act == 'ADD':
                    # skip displaying files when action is adding a new file
                    continue
                emoji = '📄'
            elif r[1] == 'folder':
                emoji = '📁'
            button_name = emoji + ' ' + r[2]
            data = r[4]
            keyboard.append([Button.inline(button_name, data=data)])
        if act == 'ADD':
            keyboard.append([Button.inline('Add here', data='add_file')])
            keyboard.append([Button.inline('New Folder here', data='make_dir')])
        elif act == 'DELETE' and directory != '/':
            keyboard.append([Button.inline('Delete this folder', data='delete_dir')])
        if directory != '/':
            keyboard.append([Button.inline('<<Back<<', data=parent_directory)])
        next_path = await self.simple_select(user_id, keyboard, message)
        return next_path

    async def add_file_to_directory(self, user_id, document, path):
        bot = self.bot
        db = self.db
        status = db.touch(user_id=user_id, file_id=document.id, file_name=document.name, path=path)
        if status == 'OK':
            return "added!"
        elif status == 'EXISTS':
            return "already exists!"
        else:
            return "NOT added⚠️"

    async def make_directory(self, user_id, path):
        bot = self.bot
        db = self.db
        ins = '<code>{}</code>\nSend folder name'.format(path)
        err = 'Please do not use *, /, \\ or other special characters'
        folder_name = await self.communicate(user_id, ins, err, r'(^(\w+\s*)+$)')
        full_path = path + folder_name + '/'
        status = db.create_folder(user_id, folder_name, path)
        if status == 'OK':
            return full_path
        elif status == 'EXISTS':
            await bot.send_message(user_id, message=messages.dir_use_diff_name)
            return
        else:
            await bot.send_message(user_id, message=messages.dir_create_failed)
            return

    async def communicate(self, user, instruction, error, pattern=None):
        bot = self.bot
        cancel_key = [Button.inline('Cancel', data='CANCEL')]
        async with bot.conversation(user) as conv:
            await bot.send_message(user, instruction, parse_mode='html', buttons=cancel_key)
            response = (await conv.get_response(0)).message
            if pattern:
                while re.match(pattern, response) is None:
                    await bot.send_message(user, error, parse_mode='html', buttons=cancel_key)
                    response = (await conv.get_response(0)).message
            return response
