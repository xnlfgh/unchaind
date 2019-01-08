.. image:: https://travis-ci.org/supakeen/unchaind.svg?branch=master
    :target: https://travis-ci.org/supakeen/unchaind

.. image:: https://readthedocs.org/projects/unchaind/badge/?version=latest
    :target: https://unchaind.readthedocs.io/en/latest/

.. image:: https://unchaind.readthedocs.io/en/latest/_static/license.svg
    :target: https://github.com/supakeen/unchaind/blob/master/LICENSE

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

unchaind
########

.. image:: https://unchaind.readthedocs.io/en/latest/_static/logo.png
    :target: https://github.com/supakeen/unchaind

``unchaind`` is a tool for EVE Online groups that use wormhole space. It offers
several tools on your Discord to make your life easier. These include automatic
notifications for kills happening in your chain, systems being found in your
chain and/or specific notifications for new systems in jump range. It can also
be used as a generic killbot which can filter kills in many ways.

Examples
========
An example is probably the easiest way to get started. The most important
bit is to get your configuration right, so let's start with a sample
configuration that takes all lowsec and nullsec kills for a certain
alliance and posts them to a Discord webhook.::

  home_system = 31002238

  [[mapper]]
      type = "siggy"
      [mapper.credentials]
          username = "bla"
          password = "bla"

  [[notifier]]
      type = "discord"
      webhook = "hook_url"
      subscribes_to = "system"

      [notifier.filter]
          require_all_of = [
              {alliance_kill: 88888888},
          ]
          require_any_of = [
              {security: "low"},
              {security: "null"},
          ]

After saving this in ``config.toml`` you can then run
``unchaind -c config.toml`` to get going.

You can read more about available filters in our documentation but you can
filter on alliance, corporation, location (regions, your siggy chain, systems),
characters, items, value, and more.
