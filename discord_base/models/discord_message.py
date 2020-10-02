# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

import requests
import logging

from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class DiscordMessage(models.Model):
    _name = "discord.message"
    _inherit = 'mail.thread'
    _description = "Discord Message"
    _order = "name desc, id desc"

    name = fields.Char(string="Name", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'), track_visibility='onchange')
    channel_id = fields.Many2one('discord.channel', string="Channel", index=True, help="Channel which gets the notification.", track_visibility="onchange", track_sequence=5)
    member_id = fields.Many2one('discord.member', string="Member", index=True, help="User which gets the notification.", track_visibility="onchange", track_sequence=2)
    guild_id = fields.Many2one('discord.guild', string="Guild", index=True, help="User which gets the notification.", track_visibility="onchange", track_sequence=8)
    content = fields.Text(string="Content", help="Body or content of the notification.")
    sent = fields.Boolean(string="Sent", default=False, store=True, track_visibility="onchange", copy=False)
    message_id = fields.Char(string="Message Id", readonly=True, help="Discord message id", copy=False)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('discord.message') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('discord.message') or _('New')
        result = super(DiscordMessage, self).create(vals)
        return result

    def _send(self, url, data=None):
        self.ensure_one()
        headers = {'Content-Type': 'application/json', 'user-agent': 'odoo/11.0', 'Authorization': 'Bot %s' % self.guild_id.token}
        try:
            result = requests.post(url, headers=headers, json=data)
            _logger.warning(result.status_code)
            if result.status_code == 200:
                return result.json()
            result.close()
        except Exception as e:
            _logger.warning(e)
        return False

    @api.multi
    def send(self):
        url = self.env['ir.config_parameter'].sudo().get_param('discord_api_url') or 'https://discord.com/api'
        url = url if url.endswith('/') else url + '/'
        
        # Send Message to a Channel
        for record in self:
            base_url = ""
            data = {}
            if record.channel_id:
                base_url = url + 'channels/%s/messages' % record.channel_id.discord_id
                data = {
                    'content': record.content,
                    'tts': False,
                }
            if base_url:
                message = record._send(base_url, data)
                _logger.warning("****")
                _logger.warning(message)
                if message:
                    record.write({'sent': True, 'message_id': message['id']})