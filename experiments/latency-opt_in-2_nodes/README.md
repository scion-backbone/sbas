## Latency Experiment

### Setup

*Setting:*
Two opt-in nodes, each connected to a different SBAS point of presence, measure latency using ICMP echo to one another.

```
          Link 5 (public Internet)
        - - - - - - - - - - - - - -
        |                         |
  +--------+      Link 1      +-----------+
  |  SBAS  |==================|   SBAS    |
  | Oregon |    (SCIONLab)    | Frankfurt |
  +--------+                  +-----------+
 184.164.236.1               184.164.236.129
      |                             |
      | Link 2                      | Link 3
      |                             |
 184.164.236.2               184.164.236.130
    Host A   - - - - - - - - - - Host B
 (AWS N.Cali)      Link 4         (ETH)
              (public Internet)
```

### Results

(from `data/2021-01-11`)

- Link 1: 142ms
- Link 2: 21ms
- Link 3: 17ms
- Link 4: 186ms
- Link 5: 141ms
- **Expected** from A to B (= Link 1 + 2 + 3): 180ms
- **Measured** from A to B (`ping-sbas`): 180ms

There seems to be an SBAS overhead of less than a millisecond.
Notably, SBAS achieves **lower** latency than the IP Internet here!

