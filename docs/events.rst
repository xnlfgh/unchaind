Events
######

``unchaind`` notifiers support various types of events. Each event type has its
own set of filters.

kill
====
One of the most common events. When any notifiers that subscribe to the kill
event are configured ``unchaind`` will keep track of the live feed of
zkillboard_ kills and try to match them with your filter configuration. If a
killmail is matched it will be posted to the notifiers' output.

filters
-------
Kill supports a slew of filters. Let's start with an example configuration for
a kill notifier:::

  [[notifier]]
      type = "discord"
      webhook = "hook_url"
      subscribes_to = "kill"
  
      [notifier.filter]
          [notifier.filter.require_all_of]
              alliance = [99999999]
              minimum_value = [500000000]
              location = ["chain"]
          [notifier.filter.exclude_if_any]
              alliance_loss = [99999998]
