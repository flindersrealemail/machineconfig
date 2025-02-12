#!/usr/bin/bash
# 📦 Repository Setup and Package Installation

# 📂 Create and enter code directory
cd $HOME
mkdir -p code
cd $HOME/code

# 🐊 Clone project repositories
git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig --depth 4  # Choose browser-based authentication.

# 🔄 Activate virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
  source $HOME/venvs/$ve_name/bin/activate || exit
fi

# ⚡ Install packages in development mode
cd $HOME/code/crocodile
if [ -n "$CROCODILE_EXRA" ]; then
  $HOME/.local/bin/uv pip install -e .[$CROCODILE_EXRA]
else
  $HOME/.local/bin/uv pip install -e .
fi

cd $HOME/code/machineconfig
$HOME/.local/bin/uv pip install -e .
cd $HOME
