from Worker import Worker


def main():
    w3 = Worker("localhost", 62000, "./server3")
    w3.start()


if __name__ == '__main__':
    main()
