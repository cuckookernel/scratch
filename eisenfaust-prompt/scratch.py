from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.completion import WordCompleter

# from prompt_toolkit.lexers import PygmentsLexer


CONFIG = {
    "cmd-groups": [
        {
            "name": "fs-manip",
            "cmds": [
                {
                    "cmd": "ls",
                },
                {
                    "cmd": "cd ..",
                },
            ],
        },
        {
            "name": "git",
            "cmds": [
                {
                    "cmd": "git status",
                },
            ],
        },
    ],
}
# %%


def main():
    # %%
    session = PromptSession()

    cmd_group_names = [grp["name"] for grp in CONFIG['cmd-groups']]
    cmds_by_group = {grp["name"]: [ cmd["cmd"] for cmd in grp["cmds"] ]
                     for grp in CONFIG['cmd-groups'] }

    def command_groups_bottom_toolbar():
        return HTML(" | ".join([f'<green>{cmd}</green>' for cmd in cmd_group_names]))

    # %%
    while True:
        cmd_grp_completer = WordCompleter(cmd_group_names)
        # lexer = PygmentsLexer(BashLexer)
        cmd_grp_choice = session.prompt(HTML('<green>Select a command group: </green>'),
                                        # lexer=lexer,
                                        completer=cmd_grp_completer,
                                        bottom_toolbar=command_groups_bottom_toolbar)

        def cmd_strs_bottom_toolbar():
            return HTML(" | ".join([f'<orange>{cmd}</orange>'
                                    for cmd in cmds_by_group[cmd_grp_choice]]))

        cmd_completer = WordCompleter(cmds_by_group[cmd_grp_choice])
        cmd = session.prompt(HTML('<orange>Pick a command: </orange>'),
                             completer=cmd_completer,
                             bottom_toolbar=cmd_strs_bottom_toolbar,
                             )
        print(cmd)

    #


if __name__ == '__main__':
    main()
