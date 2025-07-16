# Traffic Puzzle Validator Optimization Report

### Final Runtime: **\~0.092s**

### Initial Runtime: **\~0.941s**

### **Total Speedup: \~90%**

---

## 🔄 Summary of All Optimizations

|  # | Optimization Area                         | Time Before | Time After | Gain  | Description                                                                                                                                                                                  |
| -: | ----------------------------------------- | ----------- | ---------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1 | **Graph and Path Caching**                | \~0.941s    | \~0.850s   | \~9%  | Introduced a layout-based cache to avoid recomputing the road graph and all movement paths when the same layout is encountered. Eliminated redundant path generation and node linkage setup. |
|  2 | **GameState Occupancy Caching**           | \~0.850s    | \~0.180s   | \~79% | Cached results of `get_occupied_positions()` and vehicle path status. This removed excessive recomputation across the solver's recursive state exploration.                                  |
|  3 | **Vehicle Occupancy Cache**               | \~0.180s    | \~0.166s   | \~8%  | Cached vehicle body cell positions (`get_occupied_cells()`) at the instance level. Reduced a high-volume method to near-zero cost.                                                           |
|  4 | **Frozen `Position` and Bitwise Hashing** | \~0.166s    | \~0.121s   | \~27% | Made `Position` immutable and replaced Python’s default hash with a fast custom bitwise hash. Boosted performance of sets/dicts that heavily rely on position keys.                          |

---

## 📊 Profiling Impact: Method-Level Changes

* `get_occupied_cells`: From **235,821 calls, 0.41s** to **15,388 calls, 0.002s**
* `get_occupied_positions`: From **\~0.81s** to **\~0.016s**
* `__hash__` calls: Significantly reduced and sped up, now mostly handled in `~0.012s`
* Total function calls: Reduced from **>1 million** to **\~310k**

---

## ✅ Outcome

All optimizations were targeted at high-frequency, low-complexity functions that were recomputed per state or per vehicle. By removing duplicate computation and improving data structure efficiency. 

Core solving (`solve`) now runs in **\~100 ms** vs. nearly **1s** before

