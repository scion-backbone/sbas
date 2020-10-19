## Latency Experiment

### Setup

*Setting:*
Two opt-in nodes, each connected to a different SBAS point of presence, measure latency using ICMP echo to one another.

```
  +--------+      Link 1      +-----------+
  |  SBAS  |==================|   SBAS    |
  | Oregon |    (SCIONLab)    | Frankfurt |
  +--------+                  +-----------+
 184.164.236.1                184.164.237.1
      |                             |
      | Link 2                      | Link 3
      |                             |
 184.164.236.2                184.164.237.2
    Host A   - - - - - - - - - - Host B
 (AWS N.Cali)      Link 4         (ETH)
              (public Internet)
```

### Results

- Link 1: 142ms
- Link 2: 21ms
- Link 3: 17ms
- Link 4: 170ms
- **Expected** (Link 1+2+3): 180ms
- **Measured**: 210ms

There seems to be an SBAS overhead of **~30ms**.

