#!/bin/bash

# 🚀 CKAN Final Day Morning Startup Script
# Purpose: Get localhost running with zero friction for 9am start

echo "🌅 FINAL DAY STARTUP - Let's Build Something Amazing!"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "docker-compose.arm64.yml" ]; then
    echo "❌ Error: Not in CKAN-Fork directory. Please cd to the correct location."
    exit 1
fi

echo "📍 Directory check: ✅ In CKAN-Fork"

# Step 1: Check current container status
echo ""
echo "🔍 Step 1: Checking current Docker container status..."
RUNNING_CONTAINERS=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(ckan|postgres|solr|redis)" | wc -l)

if [ $RUNNING_CONTAINERS -gt 0 ]; then
    echo "📊 Current running containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(ckan|postgres|solr|redis)"
else
    echo "⚠️  No CKAN containers currently running"
fi

# Step 2: Kill any existing CKAN processes
echo ""
echo "🧹 Step 2: Cleaning up any existing CKAN processes..."
pkill -f "ckan.*run" 2>/dev/null || true
if [ -f ckan.log ]; then
    echo "📝 Archiving previous ckan.log to ckan_previous.log"
    mv ckan.log ckan_previous.log
fi

# Step 3: Start/restart all containers
echo ""
echo "🐳 Step 3: Starting Docker containers..."
docker compose -f docker-compose.arm64.yml down 2>/dev/null
echo "⏳ Starting containers (this may take 30-60 seconds)..."
docker compose -f docker-compose.arm64.yml up -d

# Wait for containers to be ready
echo "⏳ Waiting for containers to initialize..."
sleep 30

# Step 4: Verify container health
echo ""
echo "🏥 Step 4: Verifying container health..."
CONTAINERS=("postgres" "solr" "redis" "ckan")
ALL_HEALTHY=true

for container in "${CONTAINERS[@]}"; do
    if docker ps --format "{{.Names}}" | grep -q "$container"; then
        echo "✅ $container: Running"
    else
        echo "❌ $container: Not running"
        ALL_HEALTHY=false
    fi
done

if [ "$ALL_HEALTHY" = false ]; then
    echo "🚨 Some containers failed to start. Check with: docker compose -f docker-compose.arm64.yml logs"
    exit 1
fi

# Step 5: Test database connection
echo ""
echo "🗄️  Step 5: Testing database connection..."
DB_TEST=$(docker compose -f docker-compose.arm64.yml exec -T postgres psql -U ckan_default -d ckan_default -c "SELECT 1;" 2>/dev/null)
if [[ $DB_TEST == *"1"* ]]; then
    echo "✅ Database: Connected"
else
    echo "❌ Database: Connection failed"
    ALL_HEALTHY=false
fi

# Step 6: Test Solr connection
echo ""
echo "🔍 Step 6: Testing Solr connection..."
SOLR_TEST=$(docker compose -f docker-compose.arm64.yml exec -T solr curl -s localhost:8983/solr/ 2>/dev/null)
if [[ $SOLR_TEST == *"Apache Solr"* ]]; then
    echo "✅ Solr: Responding"
else
    echo "❌ Solr: Not responding"
    ALL_HEALTHY=false
fi

# Step 7: Start CKAN application
echo ""
echo "🌐 Step 7: Starting CKAN application..."
echo "⏳ This will take 30-60 seconds to initialize..."

# Start CKAN in background and capture the job number
docker compose -f docker-compose.arm64.yml exec -T ckan bash -c "cd /usr/src/CKAN-Fork/CKAN-Modernization-20250721/ckan-monorepo/ckan && python startup_fix.py demo.ini && ckan -c demo.ini run --host 0.0.0.0 --port 5000" > ckan.log 2>&1 &
CKAN_PID=$!

echo "🔄 CKAN starting with PID: $CKAN_PID"
echo "📝 Logs going to: ckan.log"

# Wait for CKAN to start
echo "⏳ Waiting for CKAN to start up..."
sleep 45

# Step 8: Test CKAN accessibility
echo ""
echo "🌐 Step 8: Testing CKAN web interface..."
for i in {1..6}; do
    if curl -s http://localhost:5000 >/dev/null 2>&1; then
        echo "✅ CKAN: Accessible at http://localhost:5000"
        break
    else
        if [ $i -eq 6 ]; then
            echo "❌ CKAN: Not accessible after 60 seconds"
            echo "📋 Check logs with: tail -f ckan.log"
            ALL_HEALTHY=false
        else
            echo "⏳ CKAN not ready yet... waiting 10 more seconds ($i/6)"
            sleep 10
        fi
    fi
done

# Step 9: Final status report
echo ""
echo "📊 FINAL STATUS REPORT"
echo "====================="

if [ "$ALL_HEALTHY" = true ]; then
    echo "🎉 SUCCESS: All systems operational!"
    echo ""
    echo "🚀 READY FOR TASK 1 - Infrastructure Health Check (9:00am)"
    echo ""
    echo "Quick verification:"
    echo "  • Docker containers: ✅ All running"
    echo "  • Database: ✅ Connected"  
    echo "  • Solr: ✅ Responding"
    echo "  • CKAN Web: ✅ http://localhost:5000"
    echo ""
    echo "🎯 Next steps:"
    echo "  1. Open browser to http://localhost:5000"
    echo "  2. Log in as admin"
    echo "  3. Test creating a dataset"
    echo "  4. Tell your AI assistant: 'Infrastructure health check complete!'"
    echo ""
    echo "📋 If you need to check logs: tail -f ckan.log"
    echo "🛑 If you need to stop CKAN: kill $CKAN_PID"
else
    echo "🚨 ISSUES DETECTED - Need troubleshooting"
    echo ""
    echo "Debug commands:"
    echo "  • Container status: docker ps"
    echo "  • Container logs: docker compose -f docker-compose.arm64.yml logs [container_name]"
    echo "  • CKAN logs: tail -f ckan.log"
    echo ""
    echo "Tell your AI assistant about any errors above for quick troubleshooting."
fi

echo ""
echo "🏁 Startup script complete. Time to build something amazing!" 