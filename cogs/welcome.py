import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import json
import asyncio
from utils.guild_config import get_guild_value, set_guild_value, get_guild_config


def format_message(template: str, member: discord.Member) -> str:
    return (
        template
        .replace("{user}", member.mention)
        .replace("{username}", str(member))
        .replace("{displayname}", member.display_name)
        .replace("{server}", member.guild.name)
        .replace("{count}", str(member.guild.member_count))
        .replace("{id}", str(member.id))
    )


# ── Persistent Reaction Role View ─────────────────────────────────────────────

class ReactionRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


class RoleSelectView(discord.ui.View):
    def __init__(self, role_map: dict):
        super().__init__(timeout=None)
        options = [
            discord.SelectOption(label=name, value=str(role_id))
            for name, role_id in list(role_map.items())[:25]
        ]
        select = discord.ui.Select(
            placeholder="Pick your roles...",
            min_values=0,
            max_values=min(len(options), 10),
            options=options,
            custom_id="reaction_role_select"
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        selected_ids = [int(v) for v in interaction.data["values"]]
        guild = interaction.guild
        cfg = get_guild_config(guild.id)
        role_map = cfg.get("reaction_roles", {})
        all_role_ids = [int(rid) for rid in role_map.values()]

        to_add = []
        to_remove = []
        for role_id in all_role_ids:
            role = guild.get_role(role_id)
            if not role:
                continue
            if role_id in selected_ids and role not in interaction.user.roles:
                to_add.append(role)
            elif role_id not in selected_ids and role in interaction.user.roles:
                to_remove.append(role)

        try:
            if to_add:
                await interaction.user.add_roles(*to_add)
            if to_remove:
                await interaction.user.remove_roles(*to_remove)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to assign those roles.", ephemeral=True)
            return

        added = [r.name for r in to_add]
        removed = [r.name for r in to_remove]
        lines = []
        if added:
            lines.append(f"Added: {', '.join(added)}")
        if removed:
            lines.append(f"Removed: {', '.join(removed)}")
        msg = "\n".join(lines) if lines else "No changes made."
        await interaction.response.send_message(msg, ephemeral=True)


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── JOIN / LEAVE EVENTS ───────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = member.guild.id

        # Welcome message
        ch_id = get_guild_value(guild_id, "welcome_channel")
        msg_template = get_guild_value(guild_id, "welcome_message", "Welcome {user} to **{server}**! You are member #{count}.")
        if ch_id:
            ch = member.guild.get_channel(int(ch_id))
            if ch:
                embed = discord.Embed(
                    description=format_message(msg_template, member),
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                embed.set_author(name=str(member), icon_url=member.display_avatar.url)
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"Member #{member.guild.member_count}")
                await ch.send(embed=embed)

        # DM welcome
        dm_msg = get_guild_value(guild_id, "welcome_dm")
        if dm_msg:
            try:
                await member.send(format_message(dm_msg, member))
            except discord.Forbidden:
                pass

        # Auto-role
        auto_role_id = get_guild_value(guild_id, "auto_role")
        if auto_role_id:
            role = member.guild.get_role(int(auto_role_id))
            if role:
                try:
                    await member.add_roles(role, reason="Auto-role")
                except discord.Forbidden:
                    pass

        # Extra auto-roles (list)
        extra_roles = get_guild_value(guild_id, "extra_auto_roles", [])
        for role_id in extra_roles:
            role = member.guild.get_role(int(role_id))
            if role:
                try:
                    await member.add_roles(role, reason="Extra auto-role")
                except discord.Forbidden:
                    pass

        # Milestone announcements
        milestones = get_guild_value(guild_id, "milestones", [])
        count = member.guild.member_count
        if count in milestones:
            ch_id = get_guild_value(guild_id, "welcome_channel")
            if ch_id:
                ch = member.guild.get_channel(int(ch_id))
                if ch:
                    await ch.send(f"🎉 We've reached **{count} members**! Thanks to everyone who joined!")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_id = member.guild.id
        ch_id = get_guild_value(guild_id, "leave_channel")
        msg_template = get_guild_value(guild_id, "leave_message", "**{username}** has left the server. We now have {count} members.")
        if not ch_id:
            return
        ch = member.guild.get_channel(int(ch_id))
        if not ch:
            return
        embed = discord.Embed(
            description=format_message(msg_template, member),
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        embed.set_footer(text=f"Now at {member.guild.member_count} members")
        await ch.send(embed=embed)

    # ── WELCOME CONFIG ────────────────────────────────────────────────────────

    @app_commands.command(name="setwelcome", description="Set the welcome message channel.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setwelcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        set_guild_value(interaction.guild.id, "welcome_channel", str(channel.id))
        await interaction.response.send_message(f"Welcome channel set to {channel.mention}.", ephemeral=True)

    @app_commands.command(name="setwelcomemsg", description="Set the welcome message text.")
    @app_commands.describe(message="Use {user} {username} {displayname} {server} {count} {id}")
    @app_commands.checks.has_permissions(administrator=True)
    async def setwelcomemsg(self, interaction: discord.Interaction, message: str):
        set_guild_value(interaction.guild.id, "welcome_message", message)
        await interaction.response.send_message("Welcome message updated.", ephemeral=True)

    @app_commands.command(name="setwelcomedm", description="Set a DM message sent to new members.")
    @app_commands.describe(message="DM text. Leave blank to disable.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setwelcomedm(self, interaction: discord.Interaction, message: str = None):
        set_guild_value(interaction.guild.id, "welcome_dm", message)
        if message:
            await interaction.response.send_message("Welcome DM set.", ephemeral=True)
        else:
            await interaction.response.send_message("Welcome DM disabled.", ephemeral=True)

    @app_commands.command(name="setleave", description="Set the channel for leave messages.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setleave(self, interaction: discord.Interaction, channel: discord.TextChannel):
        set_guild_value(interaction.guild.id, "leave_channel", str(channel.id))
        await interaction.response.send_message(f"Leave channel set to {channel.mention}.", ephemeral=True)

    @app_commands.command(name="setleavemsg", description="Set the leave message text.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setleavemsg(self, interaction: discord.Interaction, message: str):
        set_guild_value(interaction.guild.id, "leave_message", message)
        await interaction.response.send_message("Leave message updated.", ephemeral=True)

    # ── AUTO-ROLE CONFIG ──────────────────────────────────────────────────────

    @app_commands.command(name="setautorole", description="Set the primary auto-role for new members.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setautorole(self, interaction: discord.Interaction, role: discord.Role):
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("That role is above my top role.", ephemeral=True)
            return
        set_guild_value(interaction.guild.id, "auto_role", str(role.id))
        await interaction.response.send_message(f"Auto-role set to {role.mention}.", ephemeral=True)

    @app_commands.command(name="clearautorole", description="Remove the primary auto-role.")
    @app_commands.checks.has_permissions(administrator=True)
    async def clearautorole(self, interaction: discord.Interaction):
        set_guild_value(interaction.guild.id, "auto_role", None)
        await interaction.response.send_message("Auto-role cleared.", ephemeral=True)

    @app_commands.command(name="addextrarole", description="Add an additional auto-role given to new members.")
    @app_commands.checks.has_permissions(administrator=True)
    async def addextrarole(self, interaction: discord.Interaction, role: discord.Role):
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("That role is above my top role.", ephemeral=True)
            return
        extras = get_guild_value(interaction.guild.id, "extra_auto_roles", [])
        if str(role.id) not in extras:
            extras.append(str(role.id))
            set_guild_value(interaction.guild.id, "extra_auto_roles", extras)
        await interaction.response.send_message(f"Added {role.mention} to extra auto-roles.", ephemeral=True)

    @app_commands.command(name="removeextrarole", description="Remove an extra auto-role.")
    @app_commands.checks.has_permissions(administrator=True)
    async def removeextrarole(self, interaction: discord.Interaction, role: discord.Role):
        extras = get_guild_value(interaction.guild.id, "extra_auto_roles", [])
        if str(role.id) in extras:
            extras.remove(str(role.id))
            set_guild_value(interaction.guild.id, "extra_auto_roles", extras)
        await interaction.response.send_message(f"Removed {role.mention} from extra auto-roles.", ephemeral=True)

    @app_commands.command(name="listautoroles", description="List all auto-roles configured.")
    @app_commands.checks.has_permissions(administrator=True)
    async def listautoroles(self, interaction: discord.Interaction):
        primary = get_guild_value(interaction.guild.id, "auto_role")
        extras = get_guild_value(interaction.guild.id, "extra_auto_roles", [])
        embed = discord.Embed(title="Auto-Roles", color=discord.Color.blurple())
        embed.add_field(name="Primary", value=f"<@&{primary}>" if primary else "None", inline=False)
        embed.add_field(name="Extra", value=", ".join(f"<@&{r}>" for r in extras) if extras else "None", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── REACTION ROLES ────────────────────────────────────────────────────────

    @app_commands.command(name="addreactionrole", description="Add a role to the reaction role list.")
    @app_commands.describe(role="The role", label="Label shown in the dropdown")
    @app_commands.checks.has_permissions(administrator=True)
    async def addreactionrole(self, interaction: discord.Interaction, role: discord.Role, label: str):
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("That role is above my top role.", ephemeral=True)
            return
        rr = get_guild_value(interaction.guild.id, "reaction_roles", {})
        rr[label] = str(role.id)
        set_guild_value(interaction.guild.id, "reaction_roles", rr)
        await interaction.response.send_message(f"Added **{label}** → {role.mention} to reaction roles.", ephemeral=True)

    @app_commands.command(name="removereactionrole", description="Remove a role from the reaction role list.")
    @app_commands.describe(label="The label to remove")
    @app_commands.checks.has_permissions(administrator=True)
    async def removereactionrole(self, interaction: discord.Interaction, label: str):
        rr = get_guild_value(interaction.guild.id, "reaction_roles", {})
        if label in rr:
            del rr[label]
            set_guild_value(interaction.guild.id, "reaction_roles", rr)
            await interaction.response.send_message(f"Removed **{label}** from reaction roles.", ephemeral=True)
        else:
            await interaction.response.send_message("Label not found.", ephemeral=True)

    @app_commands.command(name="sendreactionroles", description="Send a dropdown reaction role panel to this channel.")
    @app_commands.describe(title="Panel title", description="Panel description")
    @app_commands.checks.has_permissions(administrator=True)
    async def sendreactionroles(self, interaction: discord.Interaction, title: str = "Choose Your Roles", description: str = "Select roles from the dropdown below."):
        rr = get_guild_value(interaction.guild.id, "reaction_roles", {})
        if not rr:
            await interaction.response.send_message("No reaction roles configured. Use `/addreactionrole` first.", ephemeral=True)
            return
        embed = discord.Embed(title=title, description=description, color=discord.Color.blurple())
        for label, role_id in list(rr.items())[:25]:
            embed.add_field(name=label, value=f"<@&{role_id}>", inline=True)
        view = RoleSelectView(rr)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("Reaction role panel sent.", ephemeral=True)

    # ── VERIFICATION / JOIN GATE ──────────────────────────────────────────────

    @app_commands.command(name="setverification", description="Configure a verification role given after accepting rules.")
    @app_commands.describe(role="Role to give on verify", channel="Channel where the verify button appears")
    @app_commands.checks.has_permissions(administrator=True)
    async def setverification(self, interaction: discord.Interaction, role: discord.Role, channel: discord.TextChannel):
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("That role is above my top role.", ephemeral=True)
            return
        set_guild_value(interaction.guild.id, "verify_role", str(role.id))
        set_guild_value(interaction.guild.id, "verify_channel", str(channel.id))

        embed = discord.Embed(title="✅ Verification", description="Click the button below to verify and gain access to the server.", color=discord.Color.green())
        view = VerifyView(str(role.id))
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Verification set up in {channel.mention} with role {role.mention}.", ephemeral=True)

    # ── MILESTONE ─────────────────────────────────────────────────────────────

    @app_commands.command(name="addmilestone", description="Add a member count milestone to celebrate.")
    @app_commands.describe(count="Member count to celebrate (e.g. 100)")
    @app_commands.checks.has_permissions(administrator=True)
    async def addmilestone(self, interaction: discord.Interaction, count: int):
        milestones = get_guild_value(interaction.guild.id, "milestones", [])
        if count not in milestones:
            milestones.append(count)
            set_guild_value(interaction.guild.id, "milestones", milestones)
        await interaction.response.send_message(f"Added member milestone at **{count}** members.", ephemeral=True)

    @app_commands.command(name="removemilestone", description="Remove a milestone.")
    @app_commands.checks.has_permissions(administrator=True)
    async def removemilestone(self, interaction: discord.Interaction, count: int):
        milestones = get_guild_value(interaction.guild.id, "milestones", [])
        if count in milestones:
            milestones.remove(count)
            set_guild_value(interaction.guild.id, "milestones", milestones)
        await interaction.response.send_message(f"Removed milestone at **{count}**.", ephemeral=True)

    # ── SHOW CONFIG ───────────────────────────────────────────────────────────

    @app_commands.command(name="showconfig", description="View the full welcome/server configuration.")
    @app_commands.checks.has_permissions(administrator=True)
    async def showconfig(self, interaction: discord.Interaction):
        g = interaction.guild.id
        welcome_ch = get_guild_value(g, "welcome_channel")
        leave_ch = get_guild_value(g, "leave_channel")
        auto_role = get_guild_value(g, "auto_role")
        extras = get_guild_value(g, "extra_auto_roles", [])
        verify_role = get_guild_value(g, "verify_role")
        rr = get_guild_value(g, "reaction_roles", {})
        milestones = get_guild_value(g, "milestones", [])
        dm = get_guild_value(g, "welcome_dm")

        embed = discord.Embed(title="Server Configuration", color=discord.Color.blurple(), timestamp=datetime.utcnow())
        embed.add_field(name="Welcome Channel", value=f"<#{welcome_ch}>" if welcome_ch else "Not set", inline=True)
        embed.add_field(name="Leave Channel", value=f"<#{leave_ch}>" if leave_ch else "Not set", inline=True)
        embed.add_field(name="Auto-Role", value=f"<@&{auto_role}>" if auto_role else "Not set", inline=True)
        embed.add_field(name="Verify Role", value=f"<@&{verify_role}>" if verify_role else "Not set", inline=True)
        embed.add_field(name="Extra Auto-Roles", value=", ".join(f"<@&{r}>" for r in extras) if extras else "None", inline=False)
        embed.add_field(name="Reaction Roles", value=str(len(rr)), inline=True)
        embed.add_field(name="Milestones", value=", ".join(str(m) for m in milestones) if milestones else "None", inline=True)
        embed.add_field(name="Welcome DM", value="Enabled" if dm else "Disabled", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="testwelcome", description="Preview the welcome message for yourself.")
    @app_commands.checks.has_permissions(administrator=True)
    async def testwelcome(self, interaction: discord.Interaction):
        template = get_guild_value(interaction.guild.id, "welcome_message", "Welcome {user} to **{server}**! You are member #{count}.")
        embed = discord.Embed(description=format_message(template, interaction.user), color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="testleave", description="Preview the leave message for yourself.")
    @app_commands.checks.has_permissions(administrator=True)
    async def testleave(self, interaction: discord.Interaction):
        template = get_guild_value(interaction.guild.id, "leave_message", "**{username}** has left the server.")
        embed = discord.Embed(description=format_message(template, interaction.user), color=discord.Color.red(), timestamp=datetime.utcnow())
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="resetconfig", description="[Admin] Reset all welcome config for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def resetconfig(self, interaction: discord.Interaction):
        from utils.guild_config import load_configs, save_configs
        data = load_configs()
        if str(interaction.guild.id) in data:
            del data[str(interaction.guild.id)]
            save_configs(data)
        await interaction.response.send_message("Config reset.", ephemeral=True)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You need administrator permissions for this command.", ephemeral=True)
        elif not interaction.response.is_done():
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)


# ── Persistent Verify View ────────────────────────────────────────────────────

class VerifyView(discord.ui.View):
    def __init__(self, role_id: str = None):
        super().__init__(timeout=None)
        self._role_id = role_id

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success, emoji="✅", custom_id="verify_button")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        from utils.guild_config import get_guild_value
        role_id = get_guild_value(interaction.guild.id, "verify_role")
        if not role_id:
            await interaction.response.send_message("Verification role not configured.", ephemeral=True)
            return
        role = interaction.guild.get_role(int(role_id))
        if not role:
            await interaction.response.send_message("Verification role not found.", ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.response.send_message("You are already verified.", ephemeral=True)
            return
        try:
            await interaction.user.add_roles(role, reason="User verified")
            await interaction.response.send_message(f"✅ You have been verified and given the **{role.name}** role!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I couldn't assign that role. Please contact a moderator.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
