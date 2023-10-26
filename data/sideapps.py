from subprocess import check_output, CalledProcessError, run


# Проверка наличия стороннего ПО
def is_application_installed(application_name):
    try:
        check_output(["which", application_name])
        return True
    except CalledProcessError:
        return False


# Подкачка стороннего ПО
def install_application(*args):
    terminal_command = ['sudo','pacman','-S']
    terminal_command.extend(args)
    run(terminal_command)


if __name__ == "__main__":
    exit()
