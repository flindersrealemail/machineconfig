"""
CC
"""

from crocodile.file_management import P
from crocodile.core import Struct
from crocodile.meta import RepeatUntilNoException
import getpass
from machineconfig.scripts.python.helpers.cloud_helpers import Args
import argparse
import os
# from dataclasses import dataclass
# from pydantic import BaseModel
from typing import Optional

from machineconfig.scripts.python.helpers.helpers2 import parse_cloud_source_target
from machineconfig.scripts.python.helpers.cloud_helpers import ArgsDefaults


def _get_padding(text: str, box_width: int = 150, padding_before: int = 2, padding_after: int = 1) -> str:
    """Calculate the padding needed to align the box correctly.
    
    Args:
        text: The text to pad
        box_width: The total width of the box
        padding_before: The space taken before the text (usually "║ ")
        padding_after: The space needed after the text (usually " ║")
    
    Returns:
        A string of spaces for padding
    """
    # Count visible characters (might not be perfect for all Unicode characters)
    text_length = len(text)
    padding_length = box_width - padding_before - text_length - padding_after
    return ' ' * max(0, padding_length)


@RepeatUntilNoException(retry=3, sleep=1)
def get_securely_shared_file(url: Optional[str] = None, folder: Optional[str] = None) -> None:
    print(f"""
╔{'═' * 150}╗
║ 🚀 Secure File Downloader{_get_padding("🚀 Secure File Downloader")}║
╚{'═' * 150}╝
""")
    
    folder_obj = P.cwd() if folder is None else P(folder)
    print(f"📂 Target folder: {folder_obj}")
    
    if os.environ.get("DECRYPTION_PASSWORD") is not None:
        print("🔑 Using password from environment variables")
        pwd: str=str(os.environ.get("DECRYPTION_PASSWORD"))
    else:
        pwd = getpass.getpass(prompt="🔑 Enter decryption password: ")
        
    if url is None:
        if os.environ.get("SHARE_URL") is not None:
            url = os.environ.get("SHARE_URL")
            assert url is not None
            print("🔗 Using URL from environment variables")
        else:
            url = input("🔗 Enter share URL: ")
    
    print(f"""
╭{'─' * 150}╮
│ 📡 Downloading from URL...{_get_padding("📡 Downloading from URL...")}│
╰{'─' * 150}╯
""")
    from rich.progress import Progress
    with Progress(transient=True) as progress:
        _task = progress.add_task("Downloading... ", total=None)
        url_obj = P(url).download(folder=folder_obj)
        
    print(f"""
╭{'─' * 150}╮
│ 📥 Downloaded file: {url_obj}{_get_padding(f"📥 Downloaded file: {url_obj}")}│
╰{'─' * 150}╯
""")
    
    print(f"""
╭{'─' * 150}╮
│ 🔐 Decrypting and extracting...{_get_padding("🔐 Decrypting and extracting...")}│
╰{'─' * 150}╯
""")
    with Progress(transient=True) as progress:
        _task = progress.add_task("Decrypting... ", total=None)
        tmp_folder = P.tmpdir(prefix="tmp_unzip")
        res = url_obj.decrypt(pwd=pwd, inplace=True).unzip(inplace=True, folder=tmp_folder)
        res.search("*").apply(lambda x: x.move(folder=folder_obj, overwrite=True))


def arg_parser() -> None:
    print(f"""
╔{'═' * 150}╗
║ ☁️  Cloud Copy Utility{_get_padding("☁️  Cloud Copy Utility")}║
╚{'═' * 150}╝
""")
    
    parser = argparse.ArgumentParser(description='🚀 Cloud CLI. It wraps rclone with sane defaults for optimum type time.')

    # positional argument
    parser.add_argument("source", help="📂 file/folder path to be taken from here.")
    parser.add_argument("target", help="🎯 file/folder path to be be sent to here.")

    parser.add_argument("--overwrite", "-w", help="✍️ Overwrite existing file.", action="store_true", default=ArgsDefaults.overwrite)
    parser.add_argument("--share", "-s", help="🔗 Share file / directory", action="store_true", default=ArgsDefaults.share)
    parser.add_argument("--rel2home", "-r", help="🏠 Relative to `myhome` folder", action="store_true", default=ArgsDefaults.rel2home)
    parser.add_argument("--root", "-R", help="🌳 Remote root. None is the default, unless rel2home is raied, making the default `myhome`.", default=ArgsDefaults.root)

    parser.add_argument("--key", "-k", help="🔑 Key for encryption", type=str, default=ArgsDefaults.key)
    parser.add_argument("--pwd", "-p", help="🔒 Password for encryption", type=str, default=ArgsDefaults.pwd)
    parser.add_argument("--encrypt", "-e", help="🔐 Decrypt after receiving.", action="store_true", default=ArgsDefaults.encrypt)
    parser.add_argument("--zip", "-z", help="📦 unzip after receiving.", action="store_true", default=ArgsDefaults.zip_)
    parser.add_argument("--os_specific", "-o", help="💻 choose path specific for this OS.", action="store_true", default=ArgsDefaults.os_specific)

    parser.add_argument("--config", "-c",  help="⚙️ path to cloud.json file.", default=None)

    args = parser.parse_args()
    args_dict = vars(args)
    source: str = args_dict.pop("source")
    target: str = args_dict.pop("target")
    args_obj = Args(**args_dict)

    if args_obj.config == "ss" and (source.startswith("http") or source.startswith("bit.ly")):
        print(f"""
╭{'─' * 150}╮
│ 🔒 Detected secure share link{_get_padding("🔒 Detected secure share link")}│
╰{'─' * 150}╯
""")
        if source.startswith("https://drive.google.com/open?id="):
            source = "https://drive.google.com/uc?export=download&id=" + source.split("https://drive.google.com/open?id=")[1]
            print("🔄 Converting Google Drive link to direct download URL")
        return get_securely_shared_file(url=source, folder=target)

    if args_obj.rel2home is True and args_obj.root is None:
        args_obj.root = "myhome"
        print("🏠 Using 'myhome' as root directory")

    print(f"""
╭{'─' * 150}╮
│ 🔍 Parsing source and target paths...{_get_padding("🔍 Parsing source and target paths...")}│
╰{'─' * 150}╯
""")
    cloud, source, target = parse_cloud_source_target(args=args_obj, source=source, target=target)
    
    print(f"""
╭{'─' * 150}╮
│ ⚙️  Configuration:{_get_padding("⚙️  Configuration:")}│
╰{'─' * 150}╯
""")
    Struct(args_obj.__dict__).print(as_config=True, title="CLI config")

    assert args_obj.key is None, "Key is not supported yet."
    
    if cloud in source:
        print(f"""
╔{'═' * 150}╗
║ 📥 DOWNLOADING FROM CLOUD{_get_padding("📥 DOWNLOADING FROM CLOUD")}║
╠{'═' * 150}╣
║ ☁️  Cloud: {cloud}{_get_padding(f"☁️  Cloud: {cloud}")}
║ 📂 Source: {source.replace(cloud + ":", "")}{_get_padding(f"📂 Source: {source.replace(cloud + ':', '')}")}
║ 🎯 Target: {target}{_get_padding(f"🎯 Target: {target}")}
╚{'═' * 150}╝
""")
        
        P(target).from_cloud(cloud=cloud, remotepath=source.replace(cloud + ":", ""),
                            unzip=args_obj.zip, decrypt=args_obj.encrypt, pwd=args_obj.pwd,
                            overwrite=args_obj.overwrite,
                            rel2home=args_obj.rel2home, os_specific=args_obj.os_specific, root=args_obj.root, strict=False,
                            )
        print(f"""
╔{'═' * 150}╗
║ ✅ Download completed successfully{_get_padding("✅ Download completed successfully")}║
╚{'═' * 150}╝
""")
        
    elif cloud in target:
        print(f"""
╔{'═' * 150}╗
║ 📤 UPLOADING TO CLOUD{_get_padding("📤 UPLOADING TO CLOUD")}║
╠{'═' * 150}╣
║ ☁️  Cloud: {cloud}{_get_padding(f"☁️  Cloud: {cloud}")}
║ 📂 Source: {source}{_get_padding(f"📂 Source: {source}")}
║ 🎯 Target: {target.replace(cloud + ":", "")}{_get_padding(f"🎯 Target: {target.replace(cloud + ':', '')}")}
╚{'═' * 150}╝
""")
        
        res = P(source).to_cloud(cloud=cloud, remotepath=target.replace(cloud + ":", ""),
                                    zip=args_obj.zip, encrypt=args_obj.encrypt, pwd=args_obj.pwd,
                                    rel2home=args_obj.rel2home, root=args_obj.root, os_specific=args_obj.os_specific, strict=False,
                                    share=args_obj.share)
        print(f"""
╔{'═' * 150}╗
║ ✅ Upload completed successfully{_get_padding("✅ Upload completed successfully")}║
╚{'═' * 150}╝
""")
        
        if args_obj.share:
            fname = f".share_url_{cloud}"
            if P(source).is_dir(): share_url_path = P(source).joinpath(fname)
            else: share_url_path = P(source).with_suffix(fname)
            share_url_path.write_text(res.as_url_str())
            print(f"""
╔{'═' * 150}╗
║ 🔗 SHARE URL GENERATED{_get_padding("🔗 SHARE URL GENERATED")}║
╠{'═' * 150}╣
║ 📝 URL file: {share_url_path}{_get_padding(f"📝 URL file: {share_url_path}")}
║ 🌍 {res.as_url_str()}{_get_padding(f"🌍 {res.as_url_str()}")}
╚{'═' * 150}╝
""")
    else: 
        print(f"""
╔{'═' * 150}╗
║ ❌ ERROR: Cloud '{cloud}' not found in source or target{_get_padding(f"❌ ERROR: Cloud '{cloud}' not found in source or target")}║
╚{'═' * 150}╝
""")
        raise ValueError(f"Cloud `{cloud}` not found in source or target.")


if __name__ == "__main__":
    arg_parser()
