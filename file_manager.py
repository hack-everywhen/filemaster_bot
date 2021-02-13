import itertools

from telethon import events, Button
# import config_vars


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
        if len(contents) == 0:
            await bot.send_message(user_id, message="Add some files first using /add. Please see /help if you are new!")
            return
        parent_directory = db.get_parent_directory(user_id, directory)
        print("parent dir:" + parent_directory)
        message = 'You are here -- > <code>{}</code>'.format(directory)
        keyboard = []
        for r in contents:
            print("for loop")
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
        print(keyboard)
        next_path = await self.simple_select(user_id, keyboard, message)
        return next_path
