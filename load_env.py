from environs import Env

env = Env()
env.read_env()

TOKEN = env.str("TOKEN")
SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG")
# PAYME_ID = env.str("PAYME_ID")
# PAYME_KEY = env.str("PAYME_KEY")
# TOTAL_AMOUNT = env.int("TOTAL_AMOUNT")
# ADMIN_LINK = env.str("ADMIN_LINK")
