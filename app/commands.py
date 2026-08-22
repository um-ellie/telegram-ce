"""Command registry shared by the help screen and the autocompleter."""

COMMANDS: dict[str, dict] = {
    "/menu":     {"args": "-",              "desc": "Open the interactive main menu"},
    "/chats":    {"args": "-",              "desc": "List all channels, groups and DMs"},
    "/view":     {"args": "<target> [n]",   "desc": "Read recent messages (target: @name | #index | id)"},
    "/info":     {"args": "<target>",       "desc": "Show full profile / channel card"},
    "/send":     {"args": "<target> <msg>", "desc": "Send a message"},
    "/reply":    {"args": "<target> <msg>", "desc": "Alias of /send"},
    "/join":     {"args": "<@channel>",     "desc": "Join a public channel or group"},
    "/leave":    {"args": "<@channel>",     "desc": "Leave a channel or group"},
    "/read":     {"args": "<target>",       "desc": "Mark a chat as read"},
    "/search":   {"args": "<query>",        "desc": "Search your chats by name or username"},
    "/stats":    {"args": "-",              "desc": "Account overview dashboard"},
    "/me":       {"args": "-",              "desc": "Show your account card"},
    "/help":     {"args": "-",              "desc": "Show this command guide"},
    "/clear":    {"args": "-",              "desc": "Clear the screen"},
    "/quit":     {"args": "-",              "desc": "Exit safely"},
}

ALIASES = {
    "/dialogs": "/chats",
    "/channels": "/chats",
    "/exit": "/quit",
}
