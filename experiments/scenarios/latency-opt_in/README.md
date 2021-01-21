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

- Link 1: 142.93ms
- Link 2: 21.74ms
- Link 3: 16.52ms
- Link 4: 185.53ms
- Link 5: 140.56ms
- **Expected** from A to B (= Link 1 + 2 + 3): 181.19ms
- **Measured** from A to B (`ping-sbas`): 180.46ms

SBAS seems to have no measurable overhead in this scenario.
Notably, SBAS achieves **lower** latency than the IP Internet here!

