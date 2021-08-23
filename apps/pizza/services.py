import os


def upload_to(instance, file):
    return os.path.join(instance.pizza.title, 'image', file)
