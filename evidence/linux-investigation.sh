
#!/usr/bin/env bash

# MiniPay Linux system investigation
# Evidence is collected from the GitHub Actions Linux runner.

set +e

OUTPUT="linux-investigation.txt"

{
    echo "======================================"
    echo "MINIPAY LINUX SYSTEM INVESTIGATION"
    echo "======================================"
    date -u

    echo
    echo "1. OPERATING SYSTEM"
    cat /etc/os-release
    uname -a

    echo
    echo "2. CPU INFORMATION"
    lscpu

    echo
    echo "3. MEMORY INFORMATION"
    free -h

    echo
    echo "4. DISK USAGE"
    df -h

    echo
    echo "5. LISTENING PORTS"
    ss -tulnp

    echo
    echo "6. RUNNING PROCESSES"
    ps aux

    echo
    echo "7. TOP MEMORY-CONSUMING PROCESSES"
    ps aux --sort=-%mem | head -n 10

    echo
    echo "8. DNS CONFIGURATION"
    cat /etc/resolv.conf

    echo
    echo "9. NETWORK CONNECTIVITY"
    getent hosts github.com
    curl -I --max-time 10 https://github.com

    echo
    echo "10. SYSTEM LOGS"
    journalctl -n 30 --no-pager 2>&1 || echo "System journal unavailable in this runner"

    echo
    echo "11. PROJECT DIRECTORY DISK USAGE"
    du -sh . 2>&1
    du -h -d 2 . 2>&1 | sort -h | tail -n 20

    echo
    echo "12. MINIPAY HEALTH CHECK"
    curl -sS --max-time 5 http://127.0.0.1:8000/health \
        || echo "MiniPay API is not running on port 8000 during this check."

    echo
    echo "======================================"
    echo "INVESTIGATION COMPLETE"
    echo "======================================"

} > "$OUTPUT" 2>&1

cat "$OUTPUT"
