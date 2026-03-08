[![Python Quality Check](https://github.com/Koala-Devs/Discord-Welcomer/actions/workflows/python-test.yml/badge.svg)](https://github.com/Koala-Devs/Discord-Welcomer/actions)

# Koala Welcome Bot 🐨

<div align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/discord.py-2.0+-green.svg" alt="discord.py">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/status-active-brightgreen.svg" alt="Status">
</div>

<p align="center">
  A powerful, feature-rich Discord bot for managing server welcomes, auto-roles, verification, and reaction roles. Built by <a href="https://github.com/Koala-Devs">Koala Devs</a> ❤️
</p>

---

## 📋 Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Commands](#-commands)
- [Usage Examples](#-usage-examples)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

---

## 🚀 Features

### 👋 Welcome & Leave Management
- **Customizable welcome messages** in designated channels
- **Private welcome DMs** to new members
- **Leave messages** with member count updates
- Rich embed support with member avatars

### 🎭 Role Management
- **Auto-role assignment** (single primary role)
- **Multiple extra auto-roles** support
- **Reaction role panels** with dropdown menus
- **Verification system** with button-based role assignment

### 🎯 Member Milestones
- **Custom milestone celebrations** (e.g., 100, 500, 1000 members)
- Automatic announcements when reaching target member counts

### 🛠️ Configuration
- **Per-server configuration** stored in JSON
- **Easy setup commands** with Discord's slash commands
- **Configuration viewer** to see all settings at once
- **Test commands** to preview messages

---

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- A Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))
- Required intents enabled: `Members Intent`, `Message Content Intent`

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/Koala-Devs/Discord-Welcomer
cd welcome-bot
```

1. Install dependencies

```bash
pip install -r requirements.txt
```

1. Configure the bot

```bash
# Create a .env file with:
DISCORD_TOKEN=your_bot_token_here
```

1. Run the bot

```bash
python main.py
```

---

#### ⚙️ Configuration

The bot uses a JSON-based configuration system (guild_config.json). Each server's settings are stored separately with the following structure:

```json
{
  "guild_id": {
    "welcome_channel": "channel_id",
    "welcome_message": "Welcome {user} to {server}!",
    "welcome_dm": "Thank you for joining!",
    "leave_channel": "channel_id",
    "leave_message": "Goodbye {username}!",
    "auto_role": "role_id",
    "extra_auto_roles": ["role_id1", "role_id2"],
    "verify_role": "role_id",
    "verify_channel": "channel_id",
    "reaction_roles": {
      "Label 1": "role_id1",
      "Label 2": "role_id2"
    },
    "milestones": [100, 500, 1000]
  }
}
```

---

#### 📝 Commands

All commands are slash commands (/) and require administrator permissions unless noted.

**Welcome Configuration**

Command Description Parameters  
/setwelcome Set welcome channel channel
/setwelcomemsg Set welcome message message
/setwelcomedm Set DM welcome message (optional)
/setleave Set leave channel channel
/setleavemsg Set leave message message

**Auto-Role Management**

Command Description Parameters  
/setautorole Set primary auto-role role
/clearautorole Remove primary auto-role None
/addextrarole Add extra auto-role role
/removeextrarole Remove extra auto-role role
/listautoroles List all auto-roles None

**Reaction Roles**

Command Description Parameters  
/addreactionrole Add role to dropdown role, label
/removereactionrole Remove role label
/sendreactionroles Send panel title, description

**Verification**

Command Description Parameters  
/setverification Setup verification role, channel

**Milestones**

Command Description Parameters  
/addmilestone Add milestone count
/removemilestone Remove milestone count

**Utilities**

Command Description  
/showconfig View current configuration
/testwelcome Preview welcome message
/testleave Preview leave message
/resetconfig Reset all settings

---

#### 💡 Usage Examples

**Setting up Welcome Messages**

```
/setwelcome channel:#general
/setwelcomemsg message:Welcome {user} to **{server}**! You're member #{count}!
/setwelcomedm message:Thanks for joining our community! Check out #rules
```

**Configuring Auto-Roles**

```
/setautorole role:@Member
/addextrarole role:@Announcements
/addextrarole role:@Events
```

**Creating Reaction Roles**

```
/addreactionrole role:@Gamer label:🎮 Gaming
/addreactionrole role:@Artist label:🎨 Art
/sendreactionroles title:"Choose Your Roles" description:"Select your interest roles below"
```

**Setting Up Verification**

```
/setverification role:@Verified channel:#welcome
```

---

**📦 Message Variables**

Use these placeholders in your welcome/leave messages:

Variable Description
{user} User mention
{username} Username#discriminator
{displayname} Server nickname
{server} Server name
{count} Member count
{id} User ID

---

**🤝 Contributing**

We love contributions from the community! Here's how you can help:

**Getting Started**

1. Fork the repository
2. Create a feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

**Development Guidelines**

· Follow PEP 8 style guidelines  
· Add docstrings for new functions  
· Test your changes thoroughly  
· Update README if adding new features  
· Keep slash command structure consistent

**Ideas for Contributions**

· Add more message formatting options  
· Implement logging system  
· Add database support (PostgreSQL/MySQL)  
· Create web dashboard  
· Add more interactive components  
· Translation support  
· Custom embed color configuration  

---

**📄 License**

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 🐨 About Koala Devs

Koala Devs is a team of passionate developers creating open-source tools for the Discord community. We believe in:

· Quality code that's well-documented and tested  
· Community-driven development with user feedback  
· Open collaboration welcoming contributions from everyone

Check out our other projects on GitHub!

---

**💬 Support**

· GitHub Issues: For bugs and feature requests  
· Discord Server: Join our community  
· Documentation: Read the docs

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/Koala-Devs">Koala Devs</a>
  <br>
  ⭐ Star us on GitHub — it motivates us!
</div>