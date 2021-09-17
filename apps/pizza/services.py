import os


def upload_to(instance, file):
    return os.path.join(instance.title, 'image', file)
