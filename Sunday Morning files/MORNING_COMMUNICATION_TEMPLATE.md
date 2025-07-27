# 📞 Morning Communication Template

## **COPY-PASTE THIS TO YOUR AI ASSISTANT AT 9AM:**

---

**🌅 FINAL DAY STARTUP STATUS**

**Time**: [Current time - e.g., 9:05am]

**Startup Script Result**: 
- [ ] ✅ SUCCESS: All systems operational
- [ ] ❌ ISSUES DETECTED: [describe what failed]

**Current Status Check**:
- CKAN Web (http://localhost:5000): [ ] Working / [ ] Not accessible  
- Admin Login: [ ] Works / [ ] Doesn't work / [ ] Not tested yet
- Basic Dataset Creation: [ ] Works / [ ] Fails / [ ] Not tested yet

**If there are issues, paste the error output here:**
```
[paste any error messages from the startup script or terminal]
```

**Ready for**: Task 1 - Infrastructure Health Check (9:00-9:30am)

---

## **QUICK STATUS SHORTCUTS:**

### **✅ If Everything Works:**
```
🎉 Morning startup complete! All systems green. Ready for Task 1.
- CKAN accessible at localhost:5000 ✅
- Admin login works ✅  
- Basic dataset creation tested ✅
Let's start with analytics plugin debugging!
```

### **⚠️ If Partial Issues:**
```
🔧 Startup mostly successful but:
[describe specific issue - e.g., "CKAN loads but admin login fails"]
[paste any error messages]
Need quick fix before Task 1.
```

### **🚨 If Major Issues:**
```
🆘 Startup script failed:
[paste the error output from terminal]
Need troubleshooting before we can proceed.
```

---

## **DEBUG INFO TO INCLUDE (if issues):**

**Container Status:**
```bash
docker ps
# [paste output here]
```

**CKAN Logs (last 20 lines):**
```bash
tail -20 ckan.log
# [paste output here]
```

**Error Details:**
- What step failed in the startup script?
- Any specific error messages?
- What happens when you try to access localhost:5000?

---

## **WHAT I NEED TO HELP YOU QUICKLY:**

1. **Clear Status**: Working or broken?
2. **Specific Errors**: Exact error messages (copy-paste)
3. **What You Tested**: Login? Dataset creation? What works/doesn't?
4. **Current Task**: Which roadmap task are you on?

---

**🎯 GOAL: Get you to "Infrastructure Health Check Complete!" in under 30 minutes so we can move to analytics plugin debugging by 9:30am sharp!**

---

**📋 REMEMBER**: The startup script does the heavy lifting. Just tell me the result and any errors, and we'll fix them fast! 