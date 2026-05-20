from copy import deepcopy


AVATAR_OPTIONS = [
    {
        "id": "avatar_01",
        "label": "Blue Fox",
        "image_url": "/avatars/avatar_01.png",
    },
    {
        "id": "avatar_02",
        "label": "Green Owl",
        "image_url": "/avatars/avatar_02.png",
    },
    {
        "id": "avatar_03",
        "label": "Red Panda",
        "image_url": "/avatars/avatar_03.png",
    },
    {
        "id": "avatar_04",
        "label": "Purple Cat",
        "image_url": "/avatars/avatar_04.png",
    },
    {
        "id": "avatar_05",
        "label": "Orange Tiger",
        "image_url": "/avatars/avatar_05.png",
    },
    {
        "id": "avatar_06",
        "label": "Gray Wolf",
        "image_url": "/avatars/avatar_06.png",
    },
]

VALID_AVATAR_IDS = {avatar["id"] for avatar in AVATAR_OPTIONS}
DEFAULT_AVATAR_ID = AVATAR_OPTIONS[0]["id"]

DEFAULT_NOTIFICATION_SETTINGS = {
    "comment_replies": True,
    "comment_admin_actions": True,
    "forum_thread_replies": True,
    "forum_post_replies": True,
    "forum_admin_actions": True,
}


def get_default_notification_settings() -> dict:
    return deepcopy(DEFAULT_NOTIFICATION_SETTINGS)