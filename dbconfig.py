import configparser

#  simplistic and no error handling.
def get_mysql_param(filename='dbconfig.ini', section='mysql'):

    config = configparser.ConfigParser()
    config.read(filename)

    return config[section]
