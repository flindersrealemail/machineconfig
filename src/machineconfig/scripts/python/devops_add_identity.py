"""ID
"""


# from platform import system
from crocodile.file_management import P
from machineconfig.utils.options import display_options


def main():
    print(f"""
╔{'═' * 150}╗
║ 🔑 SSH IDENTITY MANAGEMENT                                               ║
╚{'═' * 150}╝
""")
    
    print(f"""
╭{'─' * 150}╮
│ 🔍 Searching for existing SSH keys...                                    │
╰{'─' * 150}╯
""")
    
    private_keys = P.home().joinpath(".ssh").search("*.pub").apply(lambda x: x.with_name(x.stem)).filter(lambda x: x.exists())
    
    if private_keys:
        print(f"""
╭{'─' * 150}╮
│ ✅ Found {len(private_keys)} SSH private key(s)                                    │
╰{'─' * 150}╯
""")
    else:
        print(f"""
╭{'─' * 150}╮
│ ⚠️  No SSH private keys found                                             │
╰{'─' * 150}╯
""")
        
    choice = display_options(msg="Path to private key to be used when ssh'ing: ", options=private_keys.apply(str).list + ["I have the path to the key file", "I want to paste the key itself"])
    
    if choice == "I have the path to the key file":
        print(f"""
╭{'─' * 150}╮
│ 📄 Please enter the path to your private key file                         │
╰{'─' * 150}╯
""")
        path_to_key = P(input("📋 Input path here: ")).expanduser().absolute()
        print(f"""
╭{'─' * 150}╮
│ 📂 Using key from custom path: {path_to_key}              │
╰{'─' * 150}╯
""")
        
    elif choice == "I want to paste the key itself":
        print(f"""
╭{'─' * 150}╮
│ 📋 Please provide a filename and paste the private key content            │
╰{'─' * 150}╯
""")
        key_filename = input("📝 File name (default: my_pasted_key): ") or "my_pasted_key"
        path_to_key = P.home().joinpath(f".ssh/{key_filename}").write_text(input("🔑 Paste the private key here: "))
        print(f"""
╭{'─' * 150}╮
│ 💾 Key saved to: {path_to_key}                           │
╰{'─' * 150}╯
""")
        
    elif isinstance(choice, str): 
        path_to_key = P(choice)
        print(f"""
╭{'─' * 150}╮
│ 🔑 Using selected key: {path_to_key.name}                                 │
╰{'─' * 150}╯
""")
        
    else: 
        print(f"""
╔{'═' * 150}╗
║ ❌ ERROR: Invalid choice                                                 ║
║ The selected option is not supported: {choice}                           ║
╚{'═' * 150}╝
""")
        raise NotImplementedError(f"Choice {choice} not supported")
    
    txt = f"IdentityFile {path_to_key.collapseuser().as_posix()}"  # adds this id for all connections, no host specified.
    config_path = P.home().joinpath(".ssh/config")
    
    print(f"""
╭{'─' * 150}╮
│ 📝 Updating SSH configuration...                                          │
╰{'─' * 150}╯
""")
    
    if config_path.exists(): 
        config_path.modify_text(txt_search=txt, txt_alt=txt, replace_line=True, notfound_append=True, prepend=True)  # note that Identity line must come on top of config file otherwise it won't work, hence `prepend=True`
        print(f"""
╭{'─' * 150}╮
│ ✏️  Updated existing SSH config file                                       │
╰{'─' * 150}╯
""")
    else: 
        config_path.write_text(txt)
        print(f"""
╭{'─' * 150}╮
│ 📄 Created new SSH config file                                            │
╰{'─' * 150}╯
""")
    
    program = f"""echo '
╔{'═' * 150}╗
║ ✅ SSH IDENTITY CONFIGURATION COMPLETE                                   ║
╠{'═' * 150}╣
║ Identity added to SSH config file                                        ║
║ Consider reloading the SSH config to apply changes                       ║
╚{'═' * 150}╝
'"""
    
    print(f"""
╔{'═' * 150}╗
║ 🎉 CONFIGURATION SUCCESSFUL                                              ║
╠{'═' * 150}╣
║ Identity added: {path_to_key.name}                                       
║ Config file: {config_path}                                
╚{'═' * 150}╝
""")
    
    return program


if __name__ == '__main__':
    pass
