# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import logging
import threading
import requests

from odoo import api, fields, models, tools, http, _

_logger = logging.getLogger(__name__)


class DiscordGuild(models.Model):
    _name = "discord.guild"
    _inherit = 'mail.thread'
    _description = "This is referred to as a server in the official Discord UI."
    _order = "display_name, id desc"

    display_name = fields.Char(string="Name", help="Display name.", copy=False, index=True, track_visibility='onchange')
    name = fields.Char(string="Discord Name", help="The guild name.", copy=False, readonly=True, index=True, track_visibility='onchange')
    description = fields.Text(string="Description", help="The guild’s description.", copy=False, readonly=True)
    discord_id = fields.Char(string="Server ID", required=True, help="The guild’s ID.", copy=False)
    category_ids = fields.One2many('discord.channel.category', 'guild_id', string='Categories', copy=False, readonly=True)
    text_channels = fields.One2many('discord.channel', 'guild_id', string='Channels', copy=False, readonly=True)
    member_ids = fields.One2many('discord.member', 'guild_id', string='Members', copy=False, readonly=True)
    token = fields.Char(string="Token", copy=False)
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the guild without removing it.")

    @api.model
    def sync_guilds(self):
        filters = [('active', '=', 'True')]
        if 'filters' in self._context:
            filters.extend(self._context['filters'])
        filtered_guilds = self.search(filters, limit=10)
        try:
            # auto-commit except in testing mode
            auto_commit = not getattr(threading.currentThread(), 'testing', False)
            res = filtered_guilds.sync(auto_commit=auto_commit)
        except Exception:
            _logger.exception("Failed syncing discord guilds")
        return res

    def request_discord(self, url, parameters=None):
        headers = {'user-agent': 'odoo/11.0', 'Authorization': 'Bot %s' % self.token}
        try:
            result = requests.get(url, headers=headers, params=parameters)
            if result.status_code == 200:
                return result.json()
            result.close()
        except Exception as e:
            _logger.warning(e)
        return False

    @api.multi
    def sync(self, auto_commit=False):
        for guild in self:
            if guild.token:
                url = self.env['ir.config_parameter'].sudo().get_param('discord_api_url') or 'https://discord.com/api'
                url = url if url.endswith('/') else url + '/'
                # sync guild information
                base_url = url + 'guilds/%s' % guild.discord_id
                guild_remote = guild.request_discord(base_url)
                if guild_remote:
                    guild._sync_guild(guild_remote)

                # sync channels
                channel_url = base_url + '/channels'
                channels_remote = guild.request_discord(channel_url)
                if channels_remote:
                    guild._sync_channels(channels_remote)
                
                # sync channels
                members_url = base_url + '/members'
                members_remote = guild.request_discord(members_url, {'limit': 80})
                if members_remote:
                    guild._sync_members(members_remote)
            else:
                continue
            if auto_commit is True:
                self._cr.commit()
        return True

    @api.multi
    def _sync_guild(self, guild_remote):
        self.ensure_one()
        vals = {
            'name': guild_remote['name'],
            'description': guild_remote['description']
        }
        self.write(vals)
    
    @api.multi
    def _sync_channels(self, channels_remote):
        self.ensure_one()
        channel_ids = []
        category_ids = []
        vals = {}
        categ_vals = {}
        for channel in channels_remote:
            if channel['parent_id']:
                channel_ids.append(channel['id'])
                vals[channel['id']] = {
                    'name': channel['name'],
                    'position': channel['position'],
                    'guild_id': self.id,
                    'discord_id': channel['id'],
                    'category_id': channel['parent_id']
                }
            else:
                category_ids.append(channel['id'])
                categ_vals[channel['id']] = {
                    'name': channel['name'],
                    'position': channel['position'],
                    'guild_id': self.id,
                    'discord_id': channel['id']
                }

        # Sync Category
        existing_categ_ids = []
        if self.category_ids:
            existing_categ_ids = self.category_ids.mapped("discord_id")
            self.category_ids._sync_discord(categ_vals)
        new_categ_ids = list(set(category_ids) - set(existing_categ_ids))
        Category = self.env['discord.channel.category']
        for new in new_categ_ids:
            Category.create(categ_vals[new])

        # Create dict of discord_id:id of categories
        categories = {}
        for categ in self.category_ids:
            categories[categ.discord_id] = categ.id
        
        # Update category_id with real id
        for v in vals:
            vals[v]['category_id'] = categories.get(vals[v]['category_id']) or None 
        
        # Sync channels
        existing_ids = []
        if self.text_channels:
            existing_ids = self.text_channels.mapped("discord_id")
            self.text_channels._sync_discord(vals)
        new_ids = list(set(channel_ids) - set(existing_ids))
        Channel = self.env['discord.channel']
        for new_id in new_ids:
            Channel.create(vals[new_id])
        
    @api.multi
    def _sync_members(self, members_remote):
        self.ensure_one()
        member_ids = []
        vals = {}
        for member in members_remote:
            if not member['user'].get('bot'):
                member_ids.append(member['user']['id'])
                vals[member['user']['id']] = {
                    'name': member['user']['username'],
                    'discriminator': member['user']['discriminator'],
                    'guild_id': self.id,
                    'discord_id': member['user']['id']
                }
        
        # Sync Members
        existing_ids = []
        if self.member_ids:
            existing_ids = self.member_ids.mapped("discord_id")
            self.member_ids._sync_discord(vals)
        new_ids = list(set(member_ids) - set(existing_ids))
        Member = self.env['discord.member']
        for new in new_ids:
            Member.create(vals[new])