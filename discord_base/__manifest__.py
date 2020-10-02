# -*- coding: utf-8 -*-
# Part of Ygen. See LICENSE file for full copyright and licensing details.

{
    'name': 'Discord - Base module for discord',
    'summary': """
        This module is a base module to provide foudation for building discord modules for Odoo.""",
    'description': """
        This module is a base module to provide foudation for building discord modules for Odoo.""",
    'version': '12.0.1.0.0',
    'license': 'OPL-1',
    'author': 'Bishal Pun, '
              'Ygen Software Pvt Ltd',
    'website': 'https://ygen.io',
    'price': 50.00,
    'currency': 'EUR',
    'depends': [
        'mail',
    ],
    'data': [
        'security/discord_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/ir_cron_data.xml',
        'views/discord_guild_views.xml',
        'views/discord_channel_views.xml',
        'views/discord_member_views.xml',
        'views/discord_message_views.xml',
        'views/discord_menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}