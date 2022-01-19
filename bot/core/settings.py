# -*- coding: utf-8 -*-

from telethon.tl.types import KeyboardButtonCallback,KeyboardButton
from telethon import events
from bot import SessionVars
import asyncio as aio
from .getVars import get_val
from functools import partial
import time,os,configparser,logging,traceback

torlog = logging.getLogger(__name__)
#logging.getLogger("telethon").setLevel(logging.DEBUG)

TIMEOUT_SEC = 60

# this file will contian all the handlers and code for settings
# code can be more modular i think but not bothering now
# todo make the code more modular

no = "❌"
yes = "✅"
# Central object is not used its Acknowledged 
header =  '<u>SETTINGS MENU</u>'
async def handle_setting_callback(e):
    # db = tordb
    # session_id,_ = db.get_variable("SETTING_AUTH_CODE")


    session_id= SessionVars.get_var("SETTING_AUTH_CODE")

    data = e.data.decode()
    cmd = data.split(" ")
    val = ""
    
    if cmd[-1] != session_id:
        print("Session id",session_id," - - ",cmd[-1])
        await e.answer("This Setting menu is expired.",alert=True)
        await e.delete()
        return
    if cmd[1] == "fdocs":
        await e.answer("")
        if cmd[2] == "true":
            val = True
        else:
            val = False
        
        SessionVars.update_var("FORCE_DOCUMENTS",val)
        await handle_settings(await e.get_message(),True,f"<b><u>Changed the value to {val} of force documents.</b></u>",session_id=session_id)
    
    elif cmd[1] == "rclonemenu":
        # this is menu
        mmes = await e.get_message()
        await handle_settings(mmes,True,"\nWelcome to Rclone Config Menu. TD= Team Drive, ND= Normal Drive",submenu="rclonemenu",session_id=session_id)
    elif cmd[1] == "mainmenu":
        # this is menu
        mmes = await e.get_message()
        await handle_settings(mmes,True,session_id=session_id)
    elif cmd[1] == "rcloneconfig":
        await e.answer("Send the rclone config file which you have generated.",alert=True)
        mmes = await e.get_message()
        await mmes.edit(f"{mmes.raw_text}\n/ignore to go back",buttons=None)
        val = await get_value(e,True)
        
        await general_input_manager(e,mmes,"RCLONE_CONFIG","str",val,"rclonemenu")

    elif cmd[1] == "change_drive":
        #await e.answer(f"Changed default drive to {cmd[2]}.",alert=True)
        torlog.info(cmd[2])
        SessionVars.update_var("DEF_RCLONE_DRIVE", cmd[2])

        await handle_settings(await e.get_message(),True,f"<b><u>Changed the default drive to {cmd[2]}</b></u>","rclonemenu",session_id=session_id)

    elif cmd[1] == "ctrlacts":
        # this is menu
        mmes = await e.get_message()
        await handle_settings(mmes,True,"\nWelcome to Control Actions.",submenu="ctrlacts",session_id=session_id)
    
    elif cmd[1] == "rcloneenable":
        await e.answer("Note that this parameter will only work if rclone config is loaded.")
        if cmd[2] == "true":
            val = True
        else:
            val = False
        SessionVars.update_var("RCLONE_ENABLED",val)
        mmes = await e.get_message()
        await handle_settings(mmes,True,f"<b><u>Changed the value to {val} of Rclone Enabled.</b></u>","ctrlacts",session_id=session_id)
    
    elif cmd[1] == "leechenable":
        await e.answer("")
        if cmd[2] == "true":
            val = True
        else:
            val = False
        
        SessionVars.update_var("LEECH_ENABLED",val)
        mmes = await e.get_message()
        await handle_settings(mmes,True,f"<b><u>Changed the value to {val} of Leech Enabled.</b></u>","ctrlacts",session_id=session_id)
    
    elif cmd[1] == "editsleepsec":
        await e.answer("Type the new value for EDIT_SLEEP_SECS. Note that integer is expected.",alert=True)

        mmes = await e.get_message()
        await mmes.edit(f"{mmes.raw_text}\n/ignore to go back",buttons=None)
        val = await get_value(e)
        
        await general_input_manager(e,mmes,"EDIT_SLEEP_SECS","int",val,None)

    elif cmd[1] == "statusdeltime":
        await e.answer("Type the new value for STATUS_DEL_TOUT. Note that integer is expected.",alert=True)

        mmes = await e.get_message()
        await mmes.edit(f"{mmes.raw_text}\n/ignore to go back",buttons=None)
        val = await get_value(e)
        
        await general_input_manager(e,mmes,"STATUS_DEL_TOUT","int",val,None)
    elif cmd[1] == "fastupload":
        await e.answer("")

        if cmd[2] == "true":
            val = True
        else:
            val = False
        
        SessionVars.update_var("FAST_UPLOAD",val)
        mmes = await e.get_message()
        await handle_settings(mmes,True,f"<b><u>Changed the value to {val} of Fast Upload Enabled.</b></u>","ctrlacts",session_id=session_id)
    elif cmd[1] == "expressupload":
        await e.answer("")

        if cmd[2] == "true":
            val = True
        else:
            val = False
        
        SessionVars.update_var("EXPRESS_UPLOAD",val)
        mmes = await e.get_message()
        await handle_settings(mmes,True,f"<b><u>Changed the value to {val} of Express Upload Enabled.</b></u>","ctrlacts",session_id=session_id)
    elif cmd[1] == "allowuset":
        await e.answer("")

        if cmd[2] == "true":
            val = True
        else:
            val = False
        
        SessionVars.update_var("USETTINGS_IN_PRIVATE",val)
        mmes = await e.get_message()
        await handle_settings(mmes,True,f"<b><u>Changed the value to {val} of Allow USETTINGS IN PRIVATE.</b></u>","ctrlacts",session_id=session_id)
    
    elif cmd[1] == "remotelist":
        await e.answer("Done.")
        if cmd[2] == "true":
            val = True
        else:
            val = False
        SessionVars.update_var("SHOW_REMOTE_LIST",val)
        mmes = await e.get_message()
        await handle_settings(mmes,True,f"<b><u>Changed the value to {val} of Show rmeote list.</b></u>","rclonemenu",session_id=session_id)

    elif cmd[1] == "metainfo":
        await e.reply("Add @metainforobot to your group to get the metadata easily.")

    elif cmd[1] == "selfdest":
        await e.answer("Closed")
        await e.delete()
        


async def handle_settings(e,edit=False,msg="",submenu=None,session_id=None):
    # this function creates the menu
    # and now submenus too
    if session_id is None:
        session_id = time.time()
        SessionVars.update_var("SETTING_AUTH_CODE",str(session_id))
        
    
    menu = [
        #[KeyboardButtonCallback(yes+" Allow TG Files Leech123456789-","settings data".encode("UTF-8"))], # for ref
    ]
    
    if submenu is None:
        await get_sub_menu("☁️ Open Rclone Menu ☁️","rclonemenu",session_id,menu)
        await get_sub_menu("🕹️ Control Actions 🕹️","ctrlacts",session_id,menu)
        menu.append(
            [KeyboardButtonCallback("Close Menu",f"settings selfdest {session_id}".encode("UTF-8"))]
        )


        if edit:
            rmess = await e.edit(header+"\nIts recommended to lock the group before setting vars.\n"+msg,parse_mode="html",buttons=menu,link_preview=False)
        else:
            rmess = await e.reply(header+"\nIts recommended to lock the group before setting vars.\n",parse_mode="html",buttons=menu,link_preview=False)
    
    elif submenu == "rclonemenu":

        rcval = await get_string_variable("RCLONE_CONFIG",menu,"rcloneconfig",session_id)

        if rcval != "None":
            # create a all drives menu
            if "Custom file is loaded." in rcval:

                # db = tordb
                # _, fdata = db.get_variable("RCLONE_CONFIG")

                path = os.path.join(os.getcwd(),"rclone.conf")

                # find alternative to this
                #with open(path,"wb") as fi:
                    #fi.write(fdata)
                
                conf = configparser.ConfigParser()
                conf.read(path)
                
                #menu.append([KeyboardButton("Choose a default drive from below")])
                def_drive = get_val("DEF_RCLONE_DRIVE")

                for j in conf.sections():
                    torlog.info(j)
                    prev=""
                    if j == def_drive:
                        prev = yes

                    if "team_drive" in list(conf[j]):
                        menu.append(
                            [KeyboardButtonCallback(f"{prev}{j} - TD",f"settings change_drive {j} {session_id}")]
                        )
                    else:
                        menu.append(
                            [KeyboardButtonCallback(f"{prev}{j} - ND",f"settings change_drive {j} {session_id}")]
                        )
        await get_sub_menu("Go Back ⬅️","mainmenu",session_id,menu)

        menu.append(
            [KeyboardButtonCallback("Close Menu",f"settings selfdest {session_id}".encode("UTF-8"))]
        )

        if edit:
            rmess = await e.edit(header+"\nIts recommended to lock the group before setting vars.\n"+msg,parse_mode="html",buttons=menu,link_preview=False)

    elif submenu == "ctrlacts":
        await get_bool_variable("RCLONE_ENABLED","Enable Rclone.",menu,"rcloneenable",session_id)
        await get_bool_variable("LEECH_ENABLED","Enable Leech.",menu,"leechenable",session_id)

        await get_sub_menu("Go Back ⬅️","mainmenu",session_id,menu)
        menu.append(
            [KeyboardButtonCallback("Close Menu",f"settings selfdest {session_id}".encode("UTF-8"))]
        )
        if edit:
            rmess = await e.edit(header+"\nIts recommended to lock the group before setting vars.\n"+msg,parse_mode="html",buttons=menu,link_preview=False)
   

# an attempt to manager all the input
async def general_input_manager(e, mmes, var_name, datatype, value, sub_menu):
    if value is not None and not "ignore" in value:
        await confirm_buttons(mmes,value)
        conf = await get_confirm(e)
        if conf is not None:
            if conf:
                try:
                    if datatype == "int":
                        value = int(value)
                    if datatype == "str":
                        value = str(value)
                    if datatype == "bool":
                        if value.lower() == "true":
                            value = True
                        elif value.lower() == "false":
                            value = False
                        else:
                            raise ValueError("Invalid value from bool")
                    
                    if var_name == "RCLONE_CONFIG":
                        #adjust the special case
                        try:

                            conf = configparser.ConfigParser()
                            conf.read(value)

                            for i in conf.sections():
                                SessionVars.update_var("DEF_RCLONE_DRIVE", str(i))
                                break
                                
                            #with open(value, "rb") as fi:
                                #data = fi.read()
                                # db.set_variable("RCLONE_CONFIG",0,True,data)
                            SessionVars.update_var("RCLONE_CONFIG", value)

                            #os.remove(value)
                            SessionVars.update_var("LEECH_ENABLED",True)

                        except Exception:
                            torlog.error(traceback.format_exc())
                            await handle_settings(mmes,True,f"<b><u>The conf file is invalid check logs.</b></u>",sub_menu)
                            return
                                      
                    else:
                        SessionVars.update_var(var_name, value)
                    
                    await handle_settings(mmes,True,f"<b><u>Received {var_name} value '{value}' with confirm.</b></u>",sub_menu)
                except ValueError:
                    await handle_settings(mmes,True,f"<b><u>Value [{value}] not valid try again and enter {datatype}.</b></u>",sub_menu)    
            else:
                await handle_settings(mmes,True,f"<b><u>Confirm differed by user.</b></u>",sub_menu)
        else:
            await handle_settings(mmes,True,f"<b><u>Confirm timed out [waited 60s for input].</b></u>",sub_menu)
    else:
        await handle_settings(mmes,True,f"<b><u>Entry Timed out [waited 60s for input]. OR else ignored.</b></u>",sub_menu)


async def get_value(e,file=False):
    # todo replace with conver. - or maybe not Fix Dont switch to conversion
    # this function gets the new value to be set from the user in current context
    lis = [False,None]

    #func tools works as expected ;);)    
    cbak = partial(val_input_callback,o_sender=e.sender_id,lis=lis,file=file)
    
    e.client.add_event_handler(
        #lambda e: test_callback(e,lis),
        cbak,
        events.NewMessage()
    )

    start = time.time()

    while not lis[0]:
        if (time.time() - start) >= TIMEOUT_SEC:
            break

        await aio.sleep(1)
    
    val = lis[1]
    
    e.client.remove_event_handler(cbak)

    return val

async def get_confirm(e):
    # abstract for getting the confirm in a context

    lis = [False,None]
    cbak = partial(get_confirm_callback,o_sender=e.sender_id,lis=lis)
    
    e.client.add_event_handler(
        #lambda e: test_callback(e,lis),
        cbak,
        events.CallbackQuery(pattern="confirmsetting")
    )

    start = time.time()

    while not lis[0]:
        if (time.time() - start) >= TIMEOUT_SEC:
            break
        await aio.sleep(1)

    val = lis[1]
    
    e.client.remove_event_handler(cbak)

    return val

async def val_input_callback(e,o_sender,lis,file):
    # get the input value
    if o_sender != e.sender_id:
        return
    if not file:
        lis[0] = True
        lis[1] = e.text
        await e.delete()
    else:
        if e.document is not None:
            path = await e.download_media()
            lis[0]  = True
            lis[1] = path 
            await e.delete()
        else:
            if "ignore" in e.text:
                lis[0]  = True
                lis[1] = "ignore"
                await e.delete()
            else:
                await e.delete()
        
    raise events.StopPropagation

async def get_confirm_callback(e,o_sender,lis):
    # handle the confirm callback

    if o_sender != e.sender_id:
        return
    lis[0] = True
    
    data = e.data.decode().split(" ")
    if data[1] == "true":
        lis[1] = True
    else:
        lis[1] = False

async def confirm_buttons(e,val):
    # add the confirm buttons at the bottom of the message
    await e.edit(f"Confirm the input :- <u>{val}</u>",buttons=[KeyboardButtonCallback("Yes","confirmsetting true"),KeyboardButtonCallback("No","confirmsetting false")],parse_mode="html")

async def get_bool_variable(var_name,msg,menu,callback_name,session_id):
    # handle the vars having bool values
     
    val = get_val(var_name)
    
    if val:
        #setting the value in callback so calls will be reduced ;)
        menu.append(
            [KeyboardButtonCallback(yes+msg,f"settings {callback_name} false {session_id}".encode("UTF-8"))]
        ) 
    else:
        menu.append(
            [KeyboardButtonCallback(no+msg,f"settings {callback_name} true {session_id}".encode("UTF-8"))]
        ) 

async def get_sub_menu(msg,sub_name,session_id,menu):
    menu.append(
        [KeyboardButtonCallback(msg,f"settings {sub_name} {session_id}".encode("UTF-8"))]
    )

async def get_string_variable(var_name, menu, callback_name, session_id):
    # handle the vars having string value
    # condition for rclone config

    val = SessionVars.get_var(var_name)

    if var_name == "RCLONE_CONFIG":
        if val is not None:
            val = "Custom file is loaded. (Click to load another)"
        else:
            val = "Click here to load RCLONE config."

        
    msg = var_name + " " + str(val)
    menu.append(
        [KeyboardButtonCallback(msg,f"settings {callback_name} {session_id}".encode("UTF-8"))]
    )

    # Just in case
    return val

async def get_int_variable(var_name,menu,callback_name,session_id):
    # handle the vars having string value

    val = get_val(var_name)
    msg = var_name + " " + str(val)
    menu.append(
        [KeyboardButtonCallback(msg,f"settings {callback_name} {session_id}".encode("UTF-8"))]
    ) 

# todo handle the list value 