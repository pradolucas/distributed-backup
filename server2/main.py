from Worker import Worker


def main():
    w2 = Worker("localhost", 61000, "./server2")
    w2.start()


if __name__ == '__main__':
    main()
