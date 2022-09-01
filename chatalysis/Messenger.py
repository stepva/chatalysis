import os
from pathlib import Path
from message_source import MessageSource


class FacebookMessenger(MessageSource):
    def __init__(self, path: str):
        MessageSource.__init__(self, path)
        self.folders = self.get_message_folders()
        self.chats = self.get_all_chats()
        self._check_media()

    def get_all_chats(self) -> list:
        """Gets list of all conversations and their ID"""
        chats = {}

        for folder in self.folders:
            for chat_id in os.listdir(Path(folder) / "inbox"):
                name = chat_id.split("_")[0].lower()

                if name not in chats:
                    chats[name] = [chat_id.lower()]
                else:
                    previous_id = chats[name][0]
                    if chat_id != previous_id:
                        chats[name].append(chat_id.lower())
        return chats

    def get_chat(self, chat_name: str):
        return self.chats.get(chat_name)

    def get_message_folders(self) -> "list[str]":
        """Get folders containing the messages"""
        folders = []

        for d in os.listdir(self.data_dir_path):
            if d.startswith("messages") and os.path.isdir(f"{self.data_dir_path}/{d}"):
                folders.append(f"{self.data_dir_path}/{d}")

        if not folders:
            raise Exception(
                """Looks like there is no "messages" folder here. Make sure to add the "messages" folder downloaded 
                from Facebook as desribed in the README :)"""
            )

        return folders

    def _check_media(self):
        """Checks if all media types are included, as for some users Facebook doesn’t include files or videos"""
        media = {"photos": 0, "videos": 0, "files": 0, "gifs": 0, "audio": 0}

        for folder in self.folders:
            everything = []
            for _, dirs, _ in os.walk(folder):
                everything.extend(dirs)
            for i in media.keys():
                if i in everything:
                    media[i] = 1

        no_media = [m for m in media.keys() if media[m] == 0]

        no_media_str = ", ".join(no_media)
        if no_media:
            raise Exception(
                f"""These media types are not included in your messages for some reason: {no_media_str}. 
                I can’t do anything about it.\n"""
            )