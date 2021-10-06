import os


def upload_to(instance, file):
    return os.path.join(f'{instance.title}.jpg')

