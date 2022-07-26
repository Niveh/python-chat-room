commands_list = ["!who"]


def commands_output(command, nicknames):
    if command == "!who":
        connected = nicknames.values()

        if len(connected) > 0:
            return f"\nConnected users: {', '.join(connected)}"
