# Patch Chromium 

## Create patch  

- Create a comparison file based on the current modification and the original chromium code
```sh
cd script
python update_patch.py
```

## Apply patch on chromium code
```sh
cd script/lib
python git_patch.py
```