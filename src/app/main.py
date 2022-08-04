from dashapp import dashapp


def main():
    dashapp.run_server(host='0.0.0.0', port='8083', debug=True)


if __name__ == '__main__':
    main()
