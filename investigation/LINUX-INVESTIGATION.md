# Linux System Investigation Report

## 1. Objective

Collect Linux system information, inspect resource utilization, verify network connectivity, review running processes, and perform a MiniPay health check.

**Execution environment:** GitHub Actions Ubuntu runner  
**Date:** 2 November 2026  
**Operating system:** Ubuntu 24.04.5 LTS

> These results describe the temporary CI runner, not a production server or the developer's office laptop.

## 2. Operating System and Kernel

- OS: Ubuntu 24.04.5 LTS
- Kernel: Linux 7.0.0-1017-azure
- Architecture: x86_64

The environment is a virtualized Azure-hosted Linux runner.

## 3. CPU Utilization and Capacity

- CPU architecture: x86_64
- Logical CPUs: 4
- Processor: Intel Xeon Platinum 8573C

The runner provides four logical CPUs. The investigation captured CPU information but did not perform a sustained CPU load test.

## 4. Memory Utilization

| Metric | Observed |
|---|---:|
| Total memory | 15 GiB |
| Used memory | 887 MiB |
| Available memory | 14 GiB |
| Swap | 3 GiB |
| Swap used | 0 B |

**Finding:** Memory availability was healthy during the investigation. No memory exhaustion was observed.

## 5. Disk Utilization

| Metric | Observed |
|---|---:|
| Root filesystem size | 145 GB |
| Used | 59 GB |
| Available | 86 GB |
| Usage | 41% |

**Finding:** Disk utilization was within a healthy range. No disk-space shortage was observed.

The repository occupied approximately 824 KB.

## 6. Listening Ports and Processes

The listening-port inspection identified:

- TCP port 22: SSH
- TCP/UDP port 53: DNS resolver
- Other local system networking services.

No MiniPay API listener was present on port 8000 during this investigation.

The process inspection identified the GitHub Actions runner, Docker daemon, system services, and other operating-system processes.

The highest memory-consuming process at the time of inspection was a temporary runner-related process, using approximately 144 MiB RSS.

## 7. DNS and Network Connectivity

- DNS resolution for github.com succeeded.
- Resolved address: 140.82.114.4
- HTTPS connectivity to GitHub returned HTTP 200.

**Finding:** DNS resolution and outbound HTTPS connectivity were working during the test.

## 8. System Logs

Recent system journal entries were collected using journalctl.

The logs showed the hosted compute agent starting the GitHub Actions runner and launching the Linux System Investigation job.

No production application logs were available in this environment.

## 9. MiniPay Health Check
The Linux CI job starts PostgreSQL, initializes the database schema, and launches the MiniPay API on port 8000 before running the investigation script.

The health endpoint was checked using:

```bash
curl -sS --max-time 5 http://127.0.0.1:8000/health
```

**Result:** The health check passed successfully in GitHub Actions.

**Finding:** MiniPay was reachable on localhost and its health endpoint responded successfully after startup. This confirms the API could connect to its configured database in the CI environment.

The earlier connection-refused result came from the initial investigation job, where the API was not running. The updated CI job resolves that limitation.

## 10. Operational Troubleshooting Guide

### High CPU utilization

1. Identify resource-intensive processes using `top` or `ps`.
2. Check application and system logs.
3. Inspect recent deployments or traffic spikes.
4. Investigate inefficient queries or application loops.
5. Scale resources if the workload requires it.

### Low disk space

1. Inspect filesystem usage with `df -h`.
2. Identify large directories using `du -sh`.
3. Review application logs and temporary files.
4. Apply safe log rotation and cleanup policies.
5. Expand storage if necessary.

### API unreachable

1. Check whether the application process is running.
2. Verify the listening port using `ss -tulnp`.
3. Check application logs.
4. Verify firewall, service, and network configuration.
5. Test the health endpoint locally and through the service endpoint.

### Repeated process termination

1. Inspect application logs and exit codes.
2. Check memory pressure and possible OOM kills.
3. Review service restart policies.
4. Inspect container events if running in Kubernetes.
5. Investigate configuration errors and dependency failures.

## 11. Evidence and Limitations

The raw command output is retained in the GitHub Actions artifact named `linux-investigation-evidence`.

This investigation was performed on a temporary GitHub-hosted Linux runner. It is not a measurement of the production environment.

The MiniPay API health check was attempted while the application was not running. No production incident, process termination, or resource exhaustion was reproduced.
