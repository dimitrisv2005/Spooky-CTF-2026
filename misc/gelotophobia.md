# Gelotophobia

A goofy "jokes" website at `http://18.217.64.238`, with a big epilepsy / flashing-strobe warning slapped across it.

## Initial Attempts

The page is pure meme — a "Generate Joke" button, a doge image, and phrases like "so funny / much joke / wow" flashing around at random positions. That flashing is what the epilepsy warning is about, and it's a complete red herring; there's nothing hidden in it.

Looking at the source, `testindex2.js` holds an array of ~46 Base64 strings, and the button does this:

```js
const joke = textData[Math.floor(Math.random()*textData.length)];
window.location.href = new URL(joke, window.location.origin).toString();
```

So clicking just navigates to `origin/<base64>`. Decoding one of those Base64 strings doesn't give a word though — it gives a long string of only `E` and `e`. That's a second layer: treat `e`=1 / `E`=0, read the bits as **UTF-16**, and you get a word — `pirate`, `oven`, `doctor`, `coffee`... 46 joke keywords. The server returns the matching dad joke for each.

## Finding the solution

The key realization: the server is **decoding the word server-side** and looking up a joke for it. So I could ask it for words that aren't in the list.

I rebuilt the exact double-encoder (word → UTF-16BE → bits as `e`/`E` → Base64) and verified it reproduced a known entry byte-for-byte:

```js
const encode = (w) => {
  let bits = "";
  for (const ch of w) {
    const c = ch.charCodeAt(0);
    for (const byte of [(c>>8)&255, c&255])
      for (let b=7; b>=0; b--) bits += ((byte>>b)&1) ? 'e' : 'E';
  }
  return btoa(bits);
};
encode("pirate") === textData[0];   // true
```

Then I just fetched crafted words and watched for any response that wasn't the default homepage. Two stood out:

- `password` → a decoy: *"What's Forrest Gump's password? 1forrest1"*
- `flag` → the actual flag, served as its "joke"

The flag's punchline is a pun on the whole gag — *"that wasn't funny."*

```flag
spooky{th4t_w4snt_funn3h}
```
