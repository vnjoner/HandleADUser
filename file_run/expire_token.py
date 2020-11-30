from ad_lib.handle_ad_user import HandleActiveDirectoryUser
from ad_lib.ad_action_const import *
from ad_lib.handle_token import HandleExpireToken


if __name__ == '__main__':
        handle_token = HandleExpireToken(FILE_TOKEN)
        handle_token.delete_expire_token()

