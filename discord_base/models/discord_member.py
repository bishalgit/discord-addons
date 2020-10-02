# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, http, _



class DiscordUser(models.Model):
    _name = "discord.user"
    _inherit = 'mail.thread'
    _description = "Discord User"
    _order = "display_name desc, id desc"

    name = fields.Char(string="Username", help="The user’s username.", required=True, copy=False, readonly=True, index=True, track_visibility='onchange')
    display_name = fields.Char(string="Display Name", help="For regular users this is just their username, but if they have a guild specific nickname then that is returned instead.", required=True, copy=False, readonly=True, index=True, track_visibility='onchange')
    discord_id = fields.Char(string="Discord ID", readonly=True, help="The user’s unique ID.", track_visibility="onchange", copy=False)
    bot = fields.Boolean(string="Bot", readonly=True, help="Specifies if the user is a bot account.", default=False, copy=False)
    discriminator = fields.Char(string="Discriminator", readonly=True, help="The user’s discriminator. This is given when the username has conflicts.", track_visibility="onchange", copy=False)
    mention = fields.Char(string="Mention", readonly=True, index=True, help="The string that allows you to mention the user.", track_visibility="onchange", copy=False)
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the channel without removing it.")

    _sql_constraints = [
        ('discord_id_unique',
         'UNIQUE(discord_id)',
         "Discord id must be unique"),

        ('mention_unique',
         'UNIQUE(mention)',
         "The mention of a user must be unique"),
        
        ('name_unique',
         'UNIQUE(name)',
         "The username of a user must be unique"),
    ]


class DiscordMember(models.Model):
    _name = "discord.member"
    _inherit = 'discord.user'
    _description = "Discord Member"
    _order = "display_name desc, id desc"

    guild_id = fields.Many2one('discord.guild', string="Guild", readonly=True, index=True, help="The guild the member belongs to.")

    @api.multi
    def _sync_discord(self, vals):
        for record in self:
            record.write(vals[record.discord_id])