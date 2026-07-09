import getpass
from .auth.credentials import save_credentials


def main():
    print("=" * 50)
    print("  IIT KGP ERP MCP Server — Setup")
    print("=" * 50)
    print()
    print("Your credentials will be stored securely in your")
    print("OS keychain (never in plaintext files).")
    print()

    roll = input("Roll Number: ").strip()
    password = getpass.getpass("Password: ")

    if not roll or not password:
        print("Error: Both roll number and password are required.")
        return

    save_credentials(roll, password)
    print()
    print("Credentials saved to OS keychain.")
    print()
    print("Add this to your MCP client config:")
    print()
    print('  {')
    print('    "mcpServers": {')
    print('      "iitkgp-erp": {')
    print('        "command": "iitkgp-erp-mcp"')
    print('      }')
    print('    }')
    print('  }')
    print()
    print("Works with: Claude Code, Cursor, Cline, Continue, Zed,")
    print("or any MCP-compatible AI agent.")
    print()
    print("Done! Start asking your AI agent about your ERP data.")


if __name__ == "__main__":
    main()
