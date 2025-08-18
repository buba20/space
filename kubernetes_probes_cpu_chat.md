# Chat Export (Translated to English)

## Liveness Probe Explanation

The `livenessProbe` in your manifest runs an `exec` command inside the container.  
If the command exits with code **0**, Kubernetes considers the container **alive**.  
If it exits with a non-zero code, the container is considered **dead** and kubelet restarts it.

### The command
```sh
sh -c "test $(cat /proc/1/smaps | grep -i pss | awk '{Total+=$2} END {print int(Total/1024)}') -le 2048"
```

Step by step:

1. `cat /proc/1/smaps`  
   Reads detailed memory mapping of PID 1 (main process).

2. `grep -i pss`  
   Filters lines with **Pss** (Proportional Set Size).

3. `awk '{Total+=$2} END {print int(Total/1024)}'`  
   - Sums all PSS values.  
   - Converts from KB to MB.  
   - Outputs total memory usage in MB.

4. `test ... -le 2048`  
   - Checks if the memory usage is ≤ 2048 MB.  
   - If true → exit code 0 (success).  
   - If false → exit code ≠ 0 (failure).

### Summary
The probe ensures that the main process memory (PSS) ≤ **2GB**.  
If usage exceeds, kubelet restarts the container.

---

## Flapping Explanation

**Flapping** = continuous restarting loop:

1. Container starts.  
2. Memory grows beyond 2048 MB.  
3. Probe fails → restart.  
4. Cycle repeats endlessly.

### Why is this bad?
- No real fix (memory leak still exists).  
- App never reaches stable state.  
- Extra load on cluster (logs, scheduler).  
- Debugging harder (container dies before inspection).

---

## Limits vs Probe

### `resources.limits.memory`
- Kernel enforces cgroup memory limit.  
- Process killed by **OOMKill** only when memory is truly exceeded.  
- Precise and safe.

### Custom Probe (PSS check)
- User-level script, arbitrary threshold.  
- May restart even when memory is safe.  
- Risk of **flapping**.

### Why use a probe?
- Acts as **soft limit** (restart before hard crash).  
- SLA enforcement (e.g., service must stay below 2GB).  
- Detect memory leaks early.  
- Different thresholds per environment.  
- "Graceful restart" instead of brutal OOMKill.

**Best practice**: use **both**. Probe for soft health, limit for cluster safety.

---

## Measuring CPU in .NET 6 with OpenTelemetry

Problem: service shows **~1% CPU** usage in Prometheus.

### Why?
- .NET OTEL uses EventCounters (`cpu-usage`, `process.cpu.seconds`).  
- Value = percent of **one core**, averaged.  
- On 8-core machine:  
  - 100% = one core fully loaded.  
  - 800% = full machine usage.  
- OTEL does not account for Kubernetes cgroups.  
- Prometheus may display raw counters without `rate()`.

### Better approach in Kubernetes
- Use **cAdvisor / kubelet metrics**:  
  `container_cpu_usage_seconds_total`  
- PromQL example:  
  ```promql
  rate(container_cpu_usage_seconds_total{namespace="your-ns", pod=~"your-pod.*"}[1m])
  ```

### PromQL Queries

1. **Current CPU in cores**
   ```promql
   rate(container_cpu_usage_seconds_total{namespace="your-ns", pod=~"your-pod.*"}[1m])
   ```

2. **CPU in millicores**
   ```promql
   rate(container_cpu_usage_seconds_total{namespace="your-ns", pod=~"your-pod.*"}[5m]) * 1000
   ```

3. **CPU as % of limit**
   ```promql
   100 * (
     rate(container_cpu_usage_seconds_total{namespace="your-ns", pod=~"your-pod.*"}[5m])
   )
   /
   (
     kube_pod_container_resource_limits{namespace="your-ns", pod=~"your-pod.*", resource="cpu"}
   )
   ```

4. **Total CPU in namespace**
   ```promql
   sum(rate(container_cpu_usage_seconds_total{namespace="your-ns"}[5m]))
   ```

---

## Conclusion

- Liveness probe here enforces soft memory health check.  
- Flapping can occur if thresholds are too strict.  
- Memory `limits` and probes serve different purposes.  
- For CPU, rely on **cAdvisor metrics**, not just OTEL counters.  
- PromQL allows precise per-pod or namespace CPU monitoring.
