import sys, subprocess, os

def fail(msg):
    print "failed: ", msg
    raise Exception(msg)

def parse_command(command_key, commands = []):
    command_args = command_key.split()

    try:
        command = commands[command_args[0]]
    except:
        fail("Command `{0}` not found".format(command_args[0]))
        return

    return (command_args[0], command, command_args[1:])

def merge(res, *dicts):
    for source in dicts:
        for key, value in source.iteritems():
            if isinstance(value, dict):
                value = merge(res.setdefault(key, {}), value)
            res[key] = value

    return res

def parse_command_tree(command_config=None, commands_to_run=[], default_command_config={}):
    if isinstance(command_config, basestring):
        command = command_config
        commands_to_run.append((command, default_command_config))
    elif isinstance(command_config, list):
        command = " ".join(command_config)
        commands_to_run.append((command, default_command_config))
    elif isinstance(command_config, dict):
        try:
            if "commands" in command_config:
                default_command_config = merge({}, default_command_config, command_config)
                for command in command_config["commands"]:
                    parse_command_tree(command, commands_to_run, default_command_config)
            elif "command" in command_config:
                command = command_config["command"]
                default_command_config = merge({}, default_command_config, default_command_config)
                commands_to_run.append((command, default_command_config))
            else:
                fail("Invalid command config of type "+str(type(command_config)))
        except Exception as e:
            fail(e)
    else:
        fail("Invalid command config of type "+str(type(command_config)))


def run_command(command_key, commands = [], default_command_config={}):
    commandName, command_config, command_args = parse_command(command_key, commands)

    commands_to_run = []

    if isinstance(command_config, dict):
        merge(default_command_config, command_config)

    parse_command_tree(command_config, commands_to_run, default_command_config)

    count = len(commands_to_run)
    if not count > 0:
        fail("No commands to run")

    output = ""

    if default_command_config["minimizeBeforeCommands"]:
        wid = os.popen("xdotool getactivewindow").read()
        os.popen("xdotool getactivewindow windowminimize").read()
        commands_to_run.append(("xdotool windowactivate \"{0}\"".format(wid), {"formatArgs": False, "terminal": False}))

        count = len(commands_to_run)
        

    print "commands_to_run: ", commands_to_run

    ind = 0
    for command, command_config in commands_to_run:
        try:
            if command_config["formatArgs"]:
                if isinstance(command_args, basestring):
                    command_args = command_args.split()
                if isinstance(command_args, list):
                    command = command.format(" ".join(command_args), *command_args)
            # else:
            #     if ind == count - 1:
            #         if isinstance(command_args, basestring):
            #             command += command_args
            #         elif isinstance(command_args, list):
            #             command += " ".join(command_args)
            if command_config["terminal"]:
                command = 'gnome-terminal --working-directory=/home/daniel --window-with-profile=commandit -e "'+command+'"'
            if len(output):
                output += " "
            print "Executing: `{0}`".format(command)
            res = os.popen(command).read()
            print "Output: `{0}`".format(res)
            output += res
            if ind == count - 1:
                print "returing {0} {1}".format(ind, count)
                return (output, default_command_config)
        except Exception as e:
            fail(output+"\nError while running command `{0}`\n{1}".format(" ".join(command), str(e)))
            break
        finally:
            ind += 1
