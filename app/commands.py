"""Command registry shared by the help screen and the autocompleter."""

COMMANDS: dict[str, dict[str, str]] = {
    "/menu":     {"args": "-",                          "desc": "Open the interactive main menu"},
    "/chats":    {"args": "-",                          "desc": "List all channels, groups and DMs"},
    "/view":     {"args": "<@username | #index | id> [count]", "desc": "Read recent messages"},
    "/info":     {"args": "<@username | #index | id>",  "desc": "Show full profile / channel card"},
    "/send":     {"args": "<@target | #index> <message>", "desc": "Send a message"},
    "/reply":    {"args": "<@target | #index> <message>", "desc": "Alias of /send"},
    "/join":     {"args": "<@channel>",                 "desc": "Join a public channel or group"},
    "/leave":    {"args": "<@channel>",                 "desc": "Leave a channel or group"},
    "/read":     {"args": "<@target | #index>",         "desc": "Mark a chat as read"},
    "/search":   {"args": "<query>",                    "desc": "Search your chats by name or username"},
    "/stats":    {"args": "-",                          "desc": "Account overview dashboard"},
    "/me":       {"args": "-",                          "desc": "Show your account card"},
    "/help":     {"args": "-",                          "desc": "Show this command guide"},
    "/clear":    {"args": "-",                          "desc": "Clear the screen"},
    "/quit":     {"args": "-",                          "desc": "Exit safely"},
}

ALIASES = {
    "/dialogs": "/chats",
    "/channels": "/chats",
    "/exit": "/quit",
}

# commands whose last argument is a chat target (used by the autocompleter)
TARGET_COMMANDS = frozenset({
    "/view", "/info", "/send", "/reply", "/join", "/leave", "/read",
})
