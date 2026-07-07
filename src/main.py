from gevent import monkey
monkey.patch_all()

from Server import Server

if __name__ == "__main__":
    Server().run()
