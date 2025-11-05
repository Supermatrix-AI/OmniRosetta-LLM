import argparse

def link_module(module, repo, branch, path, desc, license, ethics, contact):
    print(f"🔗 Linking module: {module}")
    print(f"📂 Repo: {repo} ({branch})")
    print(f"📁 Path: {path}")
    print(f"📝 Description: {desc}")
    print(f"📜 License: {license} | 🌐 Ethics: {ethics}")
    print(f"✉️ Contact: {contact}")
    # Add GitHub API integration, pull check, or automation logic here


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--module")
    parser.add_argument("--repo")
    parser.add_argument("--branch")
    parser.add_argument("--path")
    parser.add_argument("--desc")
    parser.add_argument("--license")
    parser.add_argument("--ethics")
    parser.add_argument("--contact")
    args = parser.parse_args()

    link_module(**vars(args))
