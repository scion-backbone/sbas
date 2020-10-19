## Latency Experiment

*Setting:*
Two opt-in nodes, each connected to a different SBAS point of presence, measure latency using ICMP echo to one another.

```
  +--------+                  +-----------+
  |  SBAS  |==================|   SBAS    |
  | Oregon |                  | Frankfurt |
  +--------+                  +-----------+
 184.164.236.1                184.164.237.1
      |                             |
      |                             |
 184.164.236.2                184.164.237.2
    Host A                       Host B
 (AWS N.Cali)                     (ETH)
```

