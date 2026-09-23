# Potstein

A simple music player.

## Testing it 

```
nix run github:Rotsteiner/potstein -- <directory path with media files inside that directory  (either .ogg or file types mentioned in src/config.py)>
```

## Example 
Let's say `/home/user/music` contains `1.ogg`, `2.ogg` and `3.ogg` and you run 
```
nix run github:Rotsteiner/potstein -- /home/user/music
```
than they will be played in alphabetical order unitl the program terminates.
For keybinds look at `src/config.py`.
