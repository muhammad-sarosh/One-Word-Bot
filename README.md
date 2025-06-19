# One Word Bot

One Word Bot is a fun and interactive Discord bot that lets you and your friends write a story together — **one word at a time**. Collaborate, compete, and watch as your random words turn into hilarious, wild, or epic stories!

---

## 🎮 How to Play

1. **Start a game** with your friends.
2. **Take turns** adding one word each (unless it’s a name or place).
3. Try to build a story together, one word at a time.
4. The person who starts the game is called the **Host**.

> **Note:**  
> - Please use double quotes `"` for open and end quotes, instead of single quotes `'`.  
> - Incorrect grammar may cause the story not to appear correctly in the `-view` command, since spaces are inserted based on grammar rules.
> - Only the **Host** (or Admin, for ending the game) has access to some moderation commands.
 
---

## 📜 Commands

| Command     | Description |
|-------------|-------------|
| **-start**  | Starts a new game. After `-start`, mention (ping) 1 or more people you want to play with (excluding yourself). Make sure to leave spaces between pings — they’ll be added to the queue. |
| **-end**    | Ends the game and displays the final story. Can also be used by an Administrator if the Host leaves the game on. **[Host/Admin only]** |
| **-a**      | Adds a word to the story. |
| **-remove** | Removes a certain amount of words from the story. If no number is specified, removes the most recent word. **[Host only]** |
| **-push**   | Adds a person to the queue. After `-push`, mention the user you want to add. Only one person can be added at a time. **[Host only]** |
| **-pop**    | Removes a person from the queue. After `-pop`, mention the user you want to remove. Only one person can be removed at a time. **[Host only, unless removing yourself]** |
| **-host**   | Changes the host of the game. After `-host`, mention the new host. **[Host only]** |
| **-skip**   | Skips the current turn. Users can also skip their own turn. **[Host only]** |
| **-queue**  | Displays the current players in the queue. |
| **-view**   | Shows the story so far. |

---

## 🤖 Example

```plaintext
Host: -start @Bob

Bot: Game started!
Bot: @Alice's turn.

Alice: -a Once

Bot: @Bob's turn.

Bob: -a upon

Bot: @Alice's turn.

Alice: -a a

Bot: @Bob's turn.

Bob: -a time.
Bob: -end

Bot: The final story is: "Once upon a time."
