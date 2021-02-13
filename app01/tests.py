# Create your tests here.
import os

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bbs.settings")
    from django import setup

    setup()
    from app01 import models
    from app01.myfunctions import comment_del
    comment_del.CommentRecover()(6)
