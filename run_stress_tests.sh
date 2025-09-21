#!/bin/bash
# Automated Stress Test Execution Script
# Usage: ./run_stress_tests.sh [scenario_number] [duration_minutes]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="/tmp/mcp_stress_tests"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MAIN_LOG="$LOG_DIR/stress_test_$TIMESTAMP.log"

# Create log directory
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$MAIN_LOG"
}

# Performance monitoring function
monitor_performance() {
    local duration=$1
    local output_file="$LOG_DIR/performance_$TIMESTAMP.csv"
    
    echo "timestamp,mcp_response_time,cpu_percent,memory_percent,mcp_memory_mb,mcp_cpu_percent,gpu_temp,gpu_util" > "$output_file"
    
    local end_time=$(($(date +%s) + duration * 60))
    
    while [ $(date +%s) -lt $end_time ]; do
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        
        # Test MCP response time
        local start_time=$(date +%s.%N)
        timeout 10s q chat "Use jetson-debug debug_status" >/dev/null 2>&1
        local end_time_ns=$(date +%s.%N)
        local response_time=$(echo "$end_time_ns - $start_time" | bc -l 2>/dev/null || echo "0")
        
        # System metrics
        local cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | tr -d ' ')
        local mem=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
        
        # MCP process metrics
        local mcp_pid=$(pgrep -f "debug_server.py" | head -1)
        local mcp_mem=0
        local mcp_cpu=0
        if [ ! -z "$mcp_pid" ]; then
            mcp_mem=$(ps -p $mcp_pid -o rss= 2>/dev/null | awk '{print $1/1024}' || echo "0")
            mcp_cpu=$(ps -p $mcp_pid -o %cpu= 2>/dev/null | awk '{print $1}' || echo "0")
        fi
        
        # GPU metrics (if available)
        local gpu_temp=0
        local gpu_util=0
        if command -v nvidia-smi >/dev/null 2>&1; then
            local gpu_data=$(nvidia-smi --query-gpu=temperature.gpu,utilization.gpu --format=csv,noheader,nounits 2>/dev/null || echo "0,0")
            gpu_temp=$(echo "$gpu_data" | cut -d',' -f1 | tr -d ' ')
            gpu_util=$(echo "$gpu_data" | cut -d',' -f2 | tr -d ' ')
        fi
        
        echo "$timestamp,$response_time,$cpu,$mem,$mcp_mem,$mcp_cpu,$gpu_temp,$gpu_util" >> "$output_file"
        sleep 60
    done
}

# Scenario 1: AI Inference Load Test
run_scenario_1() {
    local duration=${1:-120}  # Default 2 hours
    log "Starting Scenario 1: AI Inference Load Test ($duration minutes)"
    
    # Start performance monitoring in background
    monitor_performance $duration &
    local monitor_pid=$!
    
    # Create AI workload
    log "Creating AI inference workload..."
    python3 -c "
import time
import numpy as np
import psutil
import os

log_file = '$LOG_DIR/ai_workload_$TIMESTAMP.log'
duration_sec = $duration * 60
start_time = time.time()

with open(log_file, 'w') as f:
    f.write('timestamp,iteration,memory_mb,cpu_percent\n')
    
    iteration = 0
    while time.time() - start_time < duration_sec:
        # Simulate AI inference
        data = np.random.rand(500, 500)
        result = np.dot(data, data.T)
        
        # Log metrics
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent()
        
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'{timestamp},{iteration},{memory_mb:.1f},{cpu_percent:.1f}\n')
        f.flush()
        
        iteration += 1
        time.sleep(5)  # 5 second intervals
" &
    local workload_pid=$!
    
    # Test MCP tools during load
    log "Testing MCP tools under AI load..."
    local test_start=$(date +%s)
    local test_end=$((test_start + duration * 60))
    
    while [ $(date +%s) -lt $test_end ]; do
        # Test key AI tools
        timeout 30s q chat "Use jetson-debug cuda_analysis" >> "$LOG_DIR/mcp_responses_$TIMESTAMP.log" 2>&1
        sleep 300  # Every 5 minutes
        timeout 30s q chat "Use jetson-debug ai_system_diagnosis" >> "$LOG_DIR/mcp_responses_$TIMESTAMP.log" 2>&1
        sleep 300
    done
    
    # Cleanup
    kill $workload_pid 2>/dev/null || true
    kill $monitor_pid 2>/dev/null || true
    wait
    
    log "Scenario 1 completed"
}

# Scenario 2: Thermal Stress Test
run_scenario_2() {
    local duration=${1:-240}  # Default 4 hours
    log "Starting Scenario 2: Thermal Stress Test ($duration minutes)"
    
    # Start performance monitoring
    monitor_performance $duration &
    local monitor_pid=$!
    
    # Enable maximum performance
    log "Setting maximum performance mode..."
    sudo nvpmodel -m 0 2>/dev/null || log "nvpmodel not available"
    sudo jetson_clocks 2>/dev/null || log "jetson_clocks not available"
    
    # Start thermal stress
    log "Starting thermal stress workload..."
    if command -v stress-ng >/dev/null 2>&1; then
        stress-ng --cpu 4 --timeout ${duration}m &
        local stress_pid=$!
    else
        # Fallback CPU stress
        for i in {1..4}; do
            yes > /dev/null &
        done
        local stress_pid=$!
    fi
    
    # Monitor thermal predictions
    local test_start=$(date +%s)
    local test_end=$((test_start + duration * 60))
    
    while [ $(date +%s) -lt $test_end ]; do
        timeout 30s q chat "Use jetson-debug thermal_intelligence" >> "$LOG_DIR/thermal_predictions_$TIMESTAMP.log" 2>&1
        sleep 600  # Every 10 minutes
    done
    
    # Cleanup
    kill $stress_pid 2>/dev/null || true
    killall yes 2>/dev/null || true
    kill $monitor_pid 2>/dev/null || true
    wait
    
    log "Scenario 2 completed"
}

# Scenario 3: Memory Pressure Test
run_scenario_3() {
    local duration=${1:-480}  # Default 8 hours
    log "Starting Scenario 3: Memory Pressure Test ($duration minutes)"
    
    monitor_performance $duration &
    local monitor_pid=$!
    
    # Memory pressure simulator
    python3 -c "
import time
import numpy as np
import gc

duration_sec = $duration * 60
start_time = time.time()
data_arrays = []

log_file = '$LOG_DIR/memory_pressure_$TIMESTAMP.log'
with open(log_file, 'w') as f:
    f.write('timestamp,arrays_count,estimated_memory_gb\n')
    
    while time.time() - start_time < duration_sec:
        # Gradually increase memory usage
        data_arrays.append(np.random.rand(100, 100))
        
        # Log every 100 arrays
        if len(data_arrays) % 100 == 0:
            estimated_gb = len(data_arrays) * 100 * 100 * 8 / (1024**3)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'{timestamp},{len(data_arrays)},{estimated_gb:.2f}\n')
            f.flush()
            
            # Prevent system crash - limit to 2GB
            if estimated_gb > 2.0:
                data_arrays = data_arrays[-500:]  # Keep last 500 arrays
                gc.collect()
        
        time.sleep(30)  # 30 second intervals
" &
    local memory_pid=$!
    
    # Test predictive alerts
    local test_start=$(date +%s)
    local test_end=$((test_start + duration * 60))
    
    while [ $(date +%s) -lt $test_end ]; do
        timeout 30s q chat "Use jetson-debug predictive_alerts" >> "$LOG_DIR/predictive_alerts_$TIMESTAMP.log" 2>&1
        sleep 900  # Every 15 minutes
    done
    
    kill $memory_pid 2>/dev/null || true
    kill $monitor_pid 2>/dev/null || true
    wait
    
    log "Scenario 3 completed"
}

# Scenario 4: Concurrent Q CLI Usage
run_scenario_4() {
    local duration=${1:-60}  # Default 1 hour
    local concurrent_users=${2:-10}
    log "Starting Scenario 4: Concurrent Q CLI Usage ($duration minutes, $concurrent_users users)"
    
    monitor_performance $duration &
    local monitor_pid=$!
    
    # Start concurrent Q CLI sessions
    local pids=()
    for i in $(seq 1 $concurrent_users); do
        (
            local end_time=$(($(date +%s) + duration * 60))
            local user_log="$LOG_DIR/user_${i}_$TIMESTAMP.log"
            
            while [ $(date +%s) -lt $end_time ]; do
                local start=$(date +%s.%N)
                timeout 30s q chat "Use jetson-debug monitor_dashboard" >/dev/null 2>&1
                local end=$(date +%s.%N)
                local response_time=$(echo "$end - $start" | bc -l 2>/dev/null || echo "0")
                echo "$(date '+%Y-%m-%d %H:%M:%S'),monitor_dashboard,$response_time" >> "$user_log"
                
                sleep 5
                
                start=$(date +%s.%N)
                timeout 30s q chat "Use jetson-debug cuda_analysis" >/dev/null 2>&1
                end=$(date +%s.%N)
                response_time=$(echo "$end - $start" | bc -l 2>/dev/null || echo "0")
                echo "$(date '+%Y-%m-%d %H:%M:%S'),cuda_analysis,$response_time" >> "$user_log"
                
                sleep 5
            done
        ) &
        pids+=($!)
    done
    
    # Wait for all concurrent sessions to complete
    for pid in "${pids[@]}"; do
        wait $pid
    done
    
    kill $monitor_pid 2>/dev/null || true
    wait
    
    log "Scenario 4 completed"
}

# Generate performance report
generate_report() {
    log "Generating performance report..."
    
    local report_file="$LOG_DIR/stress_test_report_$TIMESTAMP.md"
    
    cat > "$report_file" << EOF
# MCP Server Stress Test Report
**Test Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Test Duration**: Multiple scenarios
**Test Environment**: $(uname -a)

## Test Summary
$(ls -la "$LOG_DIR"/*_$TIMESTAMP.* | wc -l) log files generated

## Performance Data Files
$(ls "$LOG_DIR"/*_$TIMESTAMP.* | sed 's/.*\//- /')

## Key Metrics
- Performance monitoring data: $LOG_DIR/performance_$TIMESTAMP.csv
- MCP response logs: $LOG_DIR/mcp_responses_$TIMESTAMP.log
- Main test log: $MAIN_LOG

## Analysis Commands
\`\`\`bash
# Analyze response times
awk -F',' '{print \$2}' $LOG_DIR/performance_$TIMESTAMP.csv | sort -n

# Check for errors
grep -i error $LOG_DIR/*_$TIMESTAMP.*

# Memory usage trends
awk -F',' '{print \$4}' $LOG_DIR/performance_$TIMESTAMP.csv | tail -20
\`\`\`

## Recommendations
Review all log files for performance issues and optimization opportunities.
EOF
    
    log "Report generated: $report_file"
}

# Main execution
main() {
    local scenario=${1:-"all"}
    local duration=${2:-60}
    
    log "Starting MCP Server Stress Tests"
    log "Scenario: $scenario, Duration: $duration minutes"
    
    case $scenario in
        1) run_scenario_1 $duration ;;
        2) run_scenario_2 $duration ;;
        3) run_scenario_3 $duration ;;
        4) run_scenario_4 $duration ;;
        all)
            run_scenario_1 30
            sleep 300  # 5 minute break
            run_scenario_4 30
            ;;
        *) 
            echo "Usage: $0 [1|2|3|4|all] [duration_minutes]"
            echo "Scenarios:"
            echo "  1 - AI Inference Load Test"
            echo "  2 - Thermal Stress Test" 
            echo "  3 - Memory Pressure Test"
            echo "  4 - Concurrent Q CLI Usage"
            echo "  all - Run scenarios 1 and 4 with short duration"
            exit 1
            ;;
    esac
    
    generate_report
    log "All stress tests completed. Results in: $LOG_DIR"
}

# Check dependencies
check_dependencies() {
    local missing=()
    
    command -v q >/dev/null 2>&1 || missing+=("q (Amazon Q CLI)")
    command -v python3 >/dev/null 2>&1 || missing+=("python3")
    command -v bc >/dev/null 2>&1 || missing+=("bc")
    
    if [ ${#missing[@]} -ne 0 ]; then
        echo "Missing dependencies: ${missing[*]}"
        echo "Please install missing tools before running stress tests"
        exit 1
    fi
}

# Run main function
check_dependencies
main "$@"
