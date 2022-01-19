# -*- coding: utf-8 -*-
# (c) YashDK [yash-dk@github]

from asyncio.log import logger
from configparser import ConfigParser
from ..core.getVars import get_val
import os
import logging
import subprocess
import asyncio
import json
import time
import re
from ..utils.size import calculate_size
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .progress_for_rclone import status

torlog = logging.getLogger(__name__)


class RcloneUploader():
    
    def __init__(self, path, user_msg, dest_drive=None):
        super().__init__()
        self._path = path
        self._user_msg = user_msg
        self._rclone_pr = None
        self._current_update = None
        self._dest_drive = dest_drive

    async def execute(self):
        path = self._path
        if self._dest_drive is None:
            dest_drive = get_val("DEF_RCLONE_DRIVE")
        else:
            dest_drive = self._dest_drive

        conf_path = await self.get_config()
        torlog.info(conf_path)

        if conf_path is None:
            torlog.info("The rclone config file was not found.")
            await self._user_msg.reply("The rclone config file was not found.")

        conf = ConfigParser()
        conf.read(conf_path)
        is_gdrive = False
        is_general = False
        general_drive_name = ""

        for i in conf.sections():
            if dest_drive == str(i):
                if conf[i]["type"] == "drive":
                    is_gdrive = True
                    dest_base = get_val("GDRIVE_BASE_DIR")
                    torlog.info("Google Drive Upload Detected.")
                else:
                    is_general = True
                    general_drive_name = conf[i]["type"]
                    dest_base = get_val("RCLONE_BASE_DIR")
                    torlog.info(f"{general_drive_name} Upload Detected.")
                break

        ul_size = calculate_size(path)
        # this function will need a driver for him :o

        if not os.path.exists(path):
            torlog.info(f"Returning none cuz the path {path} not found")
            await self._user_msg.reply("Returning none cuz the path {path} not found")
            return False

        iterator = 0

        while True:
            iterator += 1
            if iterator > 100:
                # Fail safe condition
                self._is_errored = True
                self._error_reason = "Canceled Rclone Upload"
                return False

            if os.path.isdir(path):
                # handle dirs
                new_dest_base = os.path.join(dest_base, os.path.basename(path))
                # buffer size needs more testing though #todo
                if get_val("RSTUFF"):
                    rclone_copy_cmd = [get_val("RSTUFF"), 'copy', f'--config={conf_path}', str(path),
                                       f'{dest_drive}:{new_dest_base}', '-P']
                else:
                    rclone_copy_cmd = ['rclone', 'copy', f'--config={conf_path}', str(path),
                                       f'{dest_drive}:{new_dest_base}','-P']

                # spawn a process # attempt 1 # test 2
                rclone_pr = subprocess.Popen(
                    rclone_copy_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self._rclone_pr = rclone_pr
                await self.rclone_process_update()
                
                is_rate_limit = False
                blank = 0

                if is_gdrive:
                    while True:
                        data = rclone_pr.stderr.readline().decode()
                        data = data.strip()
                        if data == "":
                            blank += 1
                            if blank == 5:
                                break
                        else:
                            mat = re.findall(".*User.*Rate.*(Limit|Quota).*Exceeded.*", data, re.IGNORECASE)
                            if mat is not None:
                                if len(mat) > 0:
                                    is_rate_limit = True
                                    torlog.info("Current account limit reached...")
                                    break

                torlog.info("Upload complete")
                self._user_msg.edit("Upload complete") 

                if is_gdrive:
                    gid = await self.get_glink(dest_drive, dest_base, os.path.basename(path), conf_path)
                    torlog.info(f"Upload folder id :- {gid}")

                    folder_link = f"https://drive.google.com/folderview?id={gid[0]}"

                    # transfer[0] += ul_size
                    self._error_reason = "Uploaded Size:- {}\nUPLOADED FOLDER :-<code>{}</code>\nTo Google Drive.".format(
                        ul_size, os.path.basename(path))

                elif is_general:
                    folder_link = "http://localhost"
                    index_link = None

                    self._error_reason = "Uploaded Size:- {}\nUPLOADED FOLDER :-<code>{}</code>\nTo {}.".format(ul_size,
                                                                                                                os.path.basename(
                                                                                                                    path),
                                                                                                                general_drive_name)

                if not is_rate_limit:
                    return folder_link, index_link

            else:
                new_dest_base = dest_base
                # buffer size needs more testing though #todo
                if get_val("RSTUFF"):
                    rclone_copy_cmd = [get_val("RSTUFF"), 'copy', f'--config={conf_path}', str(path),
                                       f'{dest_drive}:{new_dest_base}', '-f', '- *.!qB', '--buffer-size=1M', '-P']
                else:
                    rclone_copy_cmd = ['rclone', 'copy', f'--config={conf_path}', str(path),
                                       f'{dest_drive}:{new_dest_base}', '-f', '- *.!qB', '--buffer-size=1M', '-P']

                # spawn a process # attempt 1 # test 2
                rclone_pr = subprocess.Popen(
                    rclone_copy_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self._rclone_pr = rclone_pr
                await self.rclone_process_update()

                # Check for errors
                is_rate_limit = False
                blank = 0
                if is_gdrive:
                    while True:
                        data = rclone_pr.stderr.readline().decode()
                        data = data.strip()
                        if data == "":
                            blank += 1
                            if blank == 5:
                                self._is_completed = True
                                self._is_done = True
                                break
                        else:
                            mat = re.findall(".*User.*Rate.*(Limit|Quota).*Exceeded.*", data, re.IGNORECASE)
                            if mat is not None:
                                if len(mat) > 0:
                                    is_rate_limit = True
                                    torlog.info("Current account limit reached now changing the SA account.")
                                    await self.gen_sa_rc_file(change=True)
                                    break

                torlog.info("Upload complete")
                if is_gdrive:
                    gid = await self.get_glink(dest_drive, dest_base, os.path.basename(path), conf_path, False)
                    torlog.info(f"Upload folder id :- {gid}")

                    file_link = f"https://drive.google.com/file/d/{gid[0]}/view"

                    # transfer[0] += ul_size
                    self._error_reason = "Uploaded Size:- {}\nUPLOADED FILE :-<code>{}</code>\nTo Google Drive.".format(
                        ul_size, os.path.basename(path))

                elif is_general:
                    file_link = "https://nube.uclv.cu/index.php/apps/files/"
                    index_link = None

                    self._error_reason = "Uploaded Size:- {}\nUPLOADED FILE :-<code>{}</code>\nTo {}.".format(ul_size,
                                                                                                              os.path.basename(
                                                                                                                  path),
                                                                                                              general_drive_name)

                if not is_rate_limit:
                    return file_link


    async def rclone_process_update(self):
        
        process = self._rclone_pr
        user_message= self._user_msg
        progress= ''
        percent= ''
        percent1= ''
        amount= ''
        speed=''
        eta=''

        while True:
                line = process.stdout.readline()
                if line:
                    dline= line.decode('UTF8')
                    
                    mat = re.findall("^ * ", dline)

                    if (mat):
                        val1= dline.split(",") 
                        val2= val1[2].replace("Transferred:","") 
                        amount= val2[5:].strip()
                        #torlog.info(amount)
                        percent = val1[3]
                        #torlog.info(percent)
                        speed= val1[4]
                        #torlog.info(speed)
                        eta= val1[5].replace("ETA","") 
                        #torlog.info(eta)
                        statu= percent.replace("%","")
                        #torlog.info(statu)
                        if statu != " -":
                            statu= int(statu)
                            progress = status(statu)

                    if percent1 != percent:
                        data = "upcancel {}".format(process.pid)
                        msg= "{} \n {} \n {} \n {} \n {}".format(
                            f'Subiendo: {statu}',
                            progress,
                            f'COMPLETADO:{ amount}',
                            f'VELOCIDAD: {speed}',
                            f'ETA: {eta}'
                            )
                        await user_message.edit(text= msg, reply_markup = InlineKeyboardMarkup([[
                         InlineKeyboardButton("Cancel", callback_data= data)]]))

                        percent1= percent
                else:
                    await user_message.edit("Upload Complete") 
                    break
      

    async def get_glink(self, drive_name, drive_base, ent_name, conf_path, isdir=True):
        print("Ent - ", ent_name)
        ent_name = re.escape(ent_name)
        filter_path = os.path.join(os.getcwd(), str(time.time()).replace(".", "") + ".txt")
        with open(filter_path, "w", encoding="UTF-8") as file:
            file.write(f"+ {ent_name}\n")
            file.write(f"- *")

        if isdir:
            if get_val("RSTUFF"):
                get_id_cmd = [get_val("RSTUFF"), "lsjson", f'--config={conf_path}', f"{drive_name}:{drive_base}",
                              "--dirs-only", "-f", f"+ {ent_name}/", "-f", "- *"]
            else:
                get_id_cmd = ["rclone", "lsjson", f'--config={conf_path}', f"{drive_name}:{drive_base}", "--dirs-only",
                              "-f", f"+ {ent_name}/", "-f", "- *"]
            # get_id_cmd = ["rclone", "lsjson", f'--config={conf_path}', f"{drive_name}:{drive_base}", "--dirs-only", f"--filter-from={filter_path}"]
        else:
            if get_val("RSTUFF"):
                get_id_cmd = [get_val("RSTUFF"), "lsjson", f'--config={conf_path}', f"{drive_name}:{drive_base}",
                              "--files-only", "-f", f"+ {ent_name}", "-f", "- *"]
            else:
                get_id_cmd = ["rclone", "lsjson", f'--config={conf_path}', f"{drive_name}:{drive_base}", "--files-only",
                              "-f", f"+ {ent_name}", "-f", "- *"]
            # get_id_cmd = ["rclone", "lsjson", f'--config={conf_path}', f"{drive_name}:{drive_base}", "--files-only", f"--filter-from={filter_path}"]

        # piping only stdout
        process = await asyncio.create_subprocess_exec(
            *get_id_cmd,
            stdout=asyncio.subprocess.PIPE
        )

        stdout, _ = await process.communicate()
        stdout = stdout.decode().strip()

        if os.path.exists(filter_path):
            os.remove(filter_path)

        try:
            data = json.loads(stdout)
            id = data[0]["ID"]
            name = data[0]["Name"]
            return (id, name)
        except Exception:
            torlog.exception("Error Occured while getting id ::- {}".format(stdout))

    async def get_config(self):
        config = get_val("RCLONE_CONFIG")
        if config is not None:
            if isinstance(config, str):
                if os.path.exists(config):
                    return config

        return None




