# Telegram Stats Generator

![Header Image](assets/dark_preview.png#gh-dark-mode-only)
![Header Image](assets/light_preview.png#gh-light-mode-only)

### For Android:
  * Download Latest [Termux](https://github.com/termux/termux-app/releases).
     ```bash
     # Change Default repository of termux.
     termux-change-repo
     # ( Select Single mirror then default )
     # Update local packages.
     yes|apt update && yes|apt upgrade
     ```

### Installation:
  ```bash
  # Install required packages.
  apt install -y python3 git python-pip

   # Clone Repo.
  git clone -q https://github.com/anonymousx97/telegram-stats-generator
  cd telegram-stats-generator 

  # Install Pypi packages
  pip install -U setuptools wheel && pip install -r req.txt

  # Starting Generator
  python stats.py
  ```
