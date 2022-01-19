
class ExecVars:
        # Set true if its VPS
        IS_VPS = False
        
        API_HASH = "40bb66beb2823e70ae5fe53935418ea0"
        API_ID = 2573648
        BOT_TOKEN = "5070550670:AAEAEsKibr4W_INFZUchfZhQYf3EBoiNLWo"
        BASE_URL_OF_BOT = ""

        # Edit the server port if you want to keep it default though.
        
        SERVPORT = 80

        # ALLOWED USERS [ids of user or supergroup] seperate by commas
        ALD_USR = [1843193844]
        OWNER_ID = 1843193844
        
        # Time to wait before edit message
        EDIT_SLEEP_SECS = 16

        # Telegram Upload Limit (in bytes)
        TG_UP_LIMIT = 2000000000

        # Should force evething uploaded into Document
        FORCE_DOCUMENTS = False

        # Chracter to use as a completed progress 
        COMPLETED_STR = "▰"

        # Chracter to use as a incomplete progress
        REMAINING_STR = "▱"

        # UNCOMMENT THE BELOW LINE WHEN USING CONTAINER AND COMMENT THE UPPER LINE
        #DATABASE_URL = "dbname=tortk user=postgres password=your-pass host=db port=5432"

        # Gdrive Config
        GDRIVE_BASE_DIR = "/"

        # The base direcory to which the files will be upload if using RCLONE for other engine than GDRIVE/ONEDRIVE
        RCLONE_BASE_DIR = "/"
        
        # Set this value to show all the remotes while leeching
        SHOW_REMOTE_LIST = False
        
        # This value will be considered only if Rclone is True - this may be defied now ;)
        # Cuz at least one needs to be Ture at a time either RCLONE or Leech.
        LEECH_ENABLED = True

        # Will be enabled once its set
        # For vps change it to True if config loaded
        RCLONE_ENABLED = False

        # If the user fails to select whether to use rclone or telegram to upload this will be the deafult.
        DEFAULT_TIMEOUT = "leech"

        # For vps set path here or you can use runtime too
        RCLONE_CONFIG = "/home/cp9/Downloads/TorToolkitX/rclone.conf"
        
        # Max size direct link
        MAX_DL_LINK_SIZE = 10

        # Name of the RCLONE drive from the config
        DEF_RCLONE_DRIVE = ""

        # Set this to your bot username if you want to add the username of your bot at the end of the commands like
        # /leech@Bot so the value will be @Bot
        BOT_CMD_POSTFIX = "" 

        # Time out for the status Delete.
        STATUS_DEL_TOUT = 20

        # Allow the user settings to be accessed in private
        USETTINGS_IN_PRIVATE = False

        # Torrent max time to collect metadata in seconds
        TOR_MAX_TOUT = 180

        ENABLE_WEB_FILES_VIEW= "False"

        # No need to worry about these
        # CHANGE THESE AT YOUR RISK
        LOCKED_USERS = False
        RSTUFF = False
        FORCE_DOCS_USER = False
        FAST_UPLOAD = True
        METAINFO_BOT = False
        EXPRESS_UPLOAD = True
        





