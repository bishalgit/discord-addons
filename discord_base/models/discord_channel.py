# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

from hashlib import sha1

from odoo import api, fields, models, tools, http, _


class DiscordChannel(models.Model):
    _name = "discord.channel"
    _inherit = 'mail.thread'
    _description = "Discord Channel"
    _order = "name desc, id desc"

    name = fields.Char(string="Name", help="The channel name.", required=True, copy=False, readonly=True, index=True, track_visibility='onchange')
    guild_id = fields.Many2one('discord.guild', string="Guild", readonly=True, index=True, help="The guild the channel belongs to.")
    category_id = fields.Many2one('discord.channel.category', string="Category", readonly=True, index=True, help="The category this channel belongs to.")
    discord_id = fields.Char(string="Discord ID", readonly=True, index=True, help="The guild’s ID.", copy=False)
    position = fields.Integer(string="Position", readonly=True, help="The position in the channel list. This is a number that starts at 0. e.g. the top channel is position 0.")
    mention = fields.Char(string="Mention", readonly=True, index=True, help="The string that allows you to mention the channel.", track_visibility="onchange", copy=False)
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the channel without removing it.")

    _sql_constraints = [
        ('mention_unique',
        'UNIQUE(mention)',
        "The mention must be unique"),
    ]

    @api.multi
    def _sync_discord(self, vals):
        for record in self:
            record.write(vals[record.discord_id])


class DiscordChannelCategory(models.Model):
    _name = "discord.channel.category"
    _description = "Represents a Discord channel category."

    name = fields.Char(string="Name", help="The category name.", copy=False, readonly=True, index=True, track_visibility='onchange')
    guild_id = fields.Many2one('discord.guild', string="Guild", readonly=True, index=True, help="The guild the channel belongs to.")
    discord_id = fields.Char(string="Discord ID", readonly=True, help="The guild’s ID.", copy=False)
    position = fields.Integer(string="Position", readonly=True, help="The position in the channel list. This is a number that starts at 0. e.g. the top channel is position 0.", track_visibility="onchange")
    text_channels = fields.One2many('discord.channel', 'category_id', string='Channels', copy=False, readonly=True)
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the category without removing it.")

    @api.multi
    def _sync_discord(self, vals):
        for record in self:
            record.write(vals[record.discord_id])